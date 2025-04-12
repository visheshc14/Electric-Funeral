#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created A Mininet Based Network For The Botnet
'''

import sys
import time

import numpy as np

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink


class ForkTopo(Topo):
    "A fork shaped network"
    def build(self, **opts):
        "Build the topology"
        botnet_switch = self.addSwitch("s2")
        add_hosts(self, botnet_switch, opts['num_bots'] + 1, "b")
        user_switch = self.addSwitch("s3")
        add_hosts(self, user_switch, 1, "u")
        sdn_switch = self.addSwitch(f"s1")
        self.addLink(sdn_switch, botnet_switch)
        self.addLink(sdn_switch, user_switch)
        add_hosts(
            self,
            sdn_switch,
            1,
            "t",
            {
                "bw": 0.1,
                "delay": "5ms",
                "loss": 0,
                "max_queue_size": 1000,
                "use_htb": True
            }
        )


def add_hosts(topo, switch, num_nodes, id_tag, opts=None):
    '''
    A hosts to the topology all connected in a star to the switch
    :param topo The network topology object
    :param switch Switch to attach the hosts to
    :param id_tag characters to identify the hosts
    :param opts extra arguments to pass to the link between the switch and hosts
    '''
    for i in range(num_nodes):
        if opts:
            topo.addLink(topo.addHost(f"{id_tag}{i}"), switch, **opts)
        else:
            topo.addLink(topo.addHost(f"{id_tag}{i}"), switch)


def run_network(num_bots):
    '''
    Run the DDoS attack on the target of the network, also have the user
    request a web service from the target
    :param num_bots Amount of bots in the botnet for the DDoS
    '''
    topo = ForkTopo(num_bots=num_bots)
    net = Mininet(
        topo=topo,
        link=TCLink,
        switch=OVSSwitch,
        controller=RemoteController
    )
    net.start()
    finish_time = time.time() + 3_600
    if "--train" in sys.argv:
        for host in net.hosts:
            host.cmdPrint("export FLASK_APP=WebServer.py && flask run --host=0.0.0.0 &")
        time.sleep(3)
        print(f"Training will finish at {time.ctime(finish_time)}")
    if "--attack" in sys.argv:
        info("*** Starting botnet controller\n")
        net['b0'].cmdPrint(f"./botnet_controller -n {num_bots} -t {net['t0'].IP()} &")
        time.sleep(1)
        info("*** Starting botnet attack on the target\n")
        for i in range(1, num_bots + 1):
            net[f"b{i}"].cmd(f"./bot -c {net['b0'].IP()} &")
        if "--train" in sys.argv:
            info("*** Waiting for training to finish")
            time.sleep(finish_time - time.time())
    elif "--normal" in sys.argv:
        info("*** Normal activity\n")
        tcp = 0
        icmp = 0
        while time.time() < finish_time:
            host = net.hosts[
                int(np.round(np.random.uniform(len(net.hosts)))) - 1
            ]
            random_host_ip = net.hosts[
                int(np.round(np.random.uniform(len(net.hosts)))) - 1
            ].IP()
            if np.random.choice(range(1, 100)) < 95:
                tcp += 1
                host.cmd(f"curl {random_host_ip}:5000")
            else:
                icmp += 1
                host.cmd(f"ping -c1 {random_host_ip}")
            print(f"\rTCP: {tcp}, ICMP: {icmp}", end="")
            time.sleep(np.random.uniform(0.25, 5))
    else:
        info("*** Starting web server on target\n")
        net['t0'].cmdPrint("export FLASK_APP=WebServer.py && flask run --host=0.0.0.0 &")
        time.sleep(1)
        info("*** User browsing web service\n")
        net['u0'].cmdPrint(f"netsurf http://{net['t0'].IP()}:5000/ &")
    if "--cli" in sys.argv:
        CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run_network(50) 