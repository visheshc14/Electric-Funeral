#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
The controller of the network. This also detects DDoS attacks.
Vishesh Choudhary 
'''

import sys
import time

import numpy as np

import tensorflow as tf
from tensorflow import keras

import pox3.lib.packet as pac
from pox3.boot import boot
from pox3.core import core
from pox3.lib.recoco import Timer

import pox3.openflow.libopenflow_01 as of


if __name__ != "__main__":
    LOG = core.getLogger()

IPV4_PROTOCOLS = {
    pac.ipv4.ICMP_PROTOCOL: "ICMP",
    pac.ipv4.IGMP_PROTOCOL: "IGMP",
    pac.ipv4.TCP_PROTOCOL: "TCP",
    pac.ipv4.UDP_PROTOCOL: "UDP",
}

IPV6_PROTOCOLS = {
    pac.ipv6.ICMP6_PROTOCOL: "ICMP",
    pac.ipv6.IGMP_PROTOCOL: "IGMP",
    pac.ipv6.TCP_PROTOCOL: "TCP",
    pac.ipv6.UDP_PROTOCOL: "UDP",
}

class Flow:
    '''
    A class for flows through the network
    '''
    def __init__(self, src, dst, comm_prot, packets, amount_bytes):
        self.src = str(src)
        self.dst = str(dst)
        self.comm_prot = comm_prot
        self.packets = packets
        self.bytes = amount_bytes
        self.time_created = time.time()
        self.time_last_used = time.time()

    def __str__(self):
        return "{} -> {}: {}".format(self.src, self.dst, self.comm_prot)

    def is_pair(self, other):
        '''
        Find whether this is a pair flow with the other one
        :param other Another flow
        '''
        p = self.src == other.dst
        q = self.dst == other.src
        v = self.comm_prot == other.comm_prot
        return p and q and v

    def __eq__(self, other):
        if isinstance(other, Flow):
            p = self.src == other.src
            q = self.dst == other.dst
            v = self.comm_prot == other.comm_prot
            return p and q and v
        return False

    def update(self, packets, amount_bytes):
        '''
        Update the amount of packets and bytes involved in this flow
        :param packets Number of packets to add to this flow
        :param amount_bytes Number of bytes to add to this flow
        '''
        self.time_last_used = time.time()
        self.packets += packets
        self.bytes += amount_bytes

class Controller(object):
    '''A controller that can detect attacks or generate data on flows'''
    def __init__(self, connection, gen_data, label, detect, interval=0.5, clean_interval=30):
        self.connection = connection
        connection.addListeners(self)
        self.label = label
        self.mac_to_port = {}
        self.flows = dict()
        self.growing_flows = dict()
        self.ports = set()
        self.growing_ports = set()
        self.time_started = time.time()
        self.interval = interval
        if gen_data:
            self.data_timer = Timer(interval, self.write_data, recurring=True)
        self.growth_timer = Timer(interval, self.reset_growth, recurring=True)
        self.clean_interval = clean_interval
        self.clean_timer = Timer(clean_interval, self.clean_flows, recurring=True)
        self.detect = detect
        if detect:
            self.model = keras.models.load_model('model.h5')
            self.interval = time.time()

    def resend_packet(self, packet_in, out_port):
        '''
        Pass the packet from this switch on to the next port
        :param packet_in The packet to pass
        :param out_port The port to pass to
        '''
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def act_like_switch(self, packet, packet_in):
        '''
        Act like a switch by learning the mappings between the MACs and ports
        :param packet The packet processed at this point
        :param packet_in The packet to pass
        '''
        if self.detect:
            self.interval = time.time() - self.interval
            six_tuple = [self.calc_tuple()]
            LOG.debug("Six-tuple: %s", six_tuple[0])
            prediction = np.round(self.model.predict(six_tuple)[0][0])
            self.interval = time.time()
            LOG.debug("Prediction: %s", prediction)
            if prediction == 1.0:
                LOG.debug("Attack detected!")
                return
        pl = packet.payload
        if isinstance(pl, pac.arp):
            src = pl.protosrc
            dst = pl.protodst
            comm_prot = "ARP"
        else:
            src = pl.srcip
            dst = pl.dstip
            if isinstance(pl, pac.ipv4):
                comm_prot = IPV4_PROTOCOLS[pl.protocol]
            else:
                comm_prot = "IPV6"
        flow = Flow(src, dst, comm_prot, 1, len(pl))
        flow_name = str(flow)
        if self.flows.get(flow_name):
            self.flows[flow_name].update(1, len(pl))
        else:
            self.flows[flow_name] = flow
        self.growing_flows[flow_name] = flow
        if len(packet_in.data) == packet_in.total_len:
            self.mac_to_port[packet.src] = packet_in.in_port
            self.ports = self.ports.union([packet_in.in_port])
            self.growing_ports = self.growing_ports.union([packet_in.in_port])
            if self.mac_to_port.get(packet.dst):
                self.resend_packet(packet_in, self.mac_to_port[packet.dst])
            else:
                self.resend_packet(packet_in, of.OFPP_ALL)

    def calc_tuple(self):
        '''
        Calculate the six-tupe for DDoS detection
        '''
        amount_packets = []
        amount_bytes = []
        durations = []
        current_time = time.time()
        num_pair_flows = float(0)
        all_flows = list(self.flows.values())
        num_flows = float(len(all_flows))
        for i, flow in enumerate(all_flows):
            amount_packets.append(flow.packets)
            amount_bytes.append(flow.bytes)
            durations.append(current_time - flow.time_created)
            for other_flow in all_flows[i + 1:]:
                if flow.is_pair(other_flow):
                    num_pair_flows += 1
        all_growing_flows = list(self.growing_flows.values())
        num_growing_flows = len(all_growing_flows)
        num_growing_pair_flows = 0
        for i, flow in enumerate(all_growing_flows):
            for other_flow in all_growing_flows[i + 1:]:
                if flow.is_pair(other_flow):
                    num_growing_pair_flows += 1
        return [
            np.median(amount_packets) if amount_packets else 0.0,
            np.median(amount_bytes) if amount_bytes else 0.0,
            np.median(durations) if amount_bytes else 0.0,
            ((2 * num_pair_flows) / num_flows) if num_flows > 0 else 0.0,
            (num_growing_flows - (2 * num_growing_pair_flows)) / self.interval,
            len(self.growing_ports) / self.interval,
        ]

    def reset_growth(self):
        '''
        Reset variables for detecting growth of them
        '''
        self.growing_flows = dict()
        self.growing_ports = set()

    def write_data(self):
        '''
        Write the current six-tuple and label to a data file
        '''
        six_tuple = self.calc_tuple()
        if six_tuple != [0 for _ in range(6)]:
            six_tuple.append(self.label)
            LOG.debug("Writing some training data")
            LOG.debug("Current tuple: %s", six_tuple)
            with open("training_data.txt", "a") as f:
                f.write(" ".join(map(str, six_tuple)) + "\n")
            LOG.debug("Written.")

    def clean_flows(self):
        '''
        Clean the flow table
        '''
        current_time = time.time()
        del_indices = []
        for flow in self.flows.values():
            if (current_time - flow.time_last_used) > self.clean_interval:
                del_indices.append(str(flow))
        for del_index in del_indices:
            del self.flows[del_index]

    def _handle_PacketIn(self, event):
        '''
        Handle a packet in
        :param event Event that triggered this
        '''
        packet = event.parsed
        if not packet.parsed:
            LOG.warning("Ignoring incomplete packet")
        else:
            packet_in = event.ofp
            self.act_like_switch(packet, packet_in)


def launch():
    '''
    Launch this controller
    '''
    def start_switch(event):
        '''
        Start up the swithc
        :param event Event that triggered this
        '''
        LOG.debug("Controlling %s with this", (event.connection,))
        Controller(
            event.connection,
            "--gen-data" in sys.argv,
            1 if "--attack" in sys.argv else 0,
            "--detect" in sys.argv
        )
    core.openflow.addListenerByName("ConnectionUp", start_switch)

def dense_norm_dropout(x):
    x = keras.layers.Dense(100, activation=tf.nn.relu)(x)
    x = keras.layers.BatchNormalization()(x)
    return keras.layers.Dropout(0.5)(x)

if __name__ == '__main__':
    if "--train" in sys.argv:
        data, lbls = (lambda x: (x[:, :6], x[:, 6]))(np.loadtxt("training_data.txt"))
        labels = np.array([[1, 0] if l == 0 else [0, 1] for l in lbls])
        inputs = keras.Input(shape=(6,))
        x = keras.layers.Dense(100, activation=tf.nn.relu)(inputs)
        x = dense_norm_dropout(x)
        x = dense_norm_dropout(x)
        x = keras.layers.Dense(100, activation=tf.nn.relu)(x)
        outputs = keras.layers.Dense(2, activation=tf.nn.softmax)(x)
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer="Adam",
            loss=keras.losses.BinaryCrossentropy(),
            metrics=["accuracy"]
        )
        history = model.fit(
            x=data,
            y=labels,
            epochs=500,
            verbose=1,
            validation_split=0.2,
            callbacks=[keras.callbacks.EarlyStopping(patience=3)]
        )
        print(f"Reached loss: {history.history['loss'][-1]}")
        fn = "model.h5"
        model.save(fn)
        print(f"Saved model as {fn}")
    else:
        boot(
            (["log.level", "--DEBUG"] if "--debug" in sys.argv else []) +
            ["network_controller"]
        )
