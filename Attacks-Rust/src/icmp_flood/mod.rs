extern crate rand;
extern crate pnet;
extern crate ctrlc;

use std::net::IpAddr;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;

use rand::Rng;

use pnet::packet::util;
use pnet::packet::ip::IpNextHeaderProtocols;
use pnet::packet::icmp::{echo_request, IcmpTypes};
use pnet::transport::TransportChannelType::Layer4;
use pnet::transport::TransportProtocol::Ipv4;
use pnet::transport::transport_channel;
use pnet::packet::Packet;

pub fn run(address: &String) {
    let protocol = Layer4(Ipv4(IpNextHeaderProtocols::Icmp));
    let (mut tx, _) = match transport_channel(4096, protocol) {
        Ok((tx, rx)) => (tx, rx),
        Err(e) => panic!("Error creating the transport channel: {}", e),
    };
    let addr = match address.as_str().parse::<IpAddr>() {
        Ok(s) => s,
        Err(e) => panic!("Failed to parse address: {}", e),
    };

    let running = Arc::new(AtomicBool::new(true));
    let r = running.clone();
    ctrlc::set_handler(move || {
        r.store(false, Ordering::SeqCst);
    }).expect("Error setting CTRL+C handler");

    let mut rng = rand::thread_rng();
    
    while running.load(Ordering::SeqCst) {
        let mut vec: Vec<u8> = vec![0; 64];
        let mut packet = echo_request::MutableEchoRequestPacket::new(&mut vec[..]).unwrap();
        packet.set_icmp_type(IcmpTypes::EchoRequest);
        packet.set_sequence_number(rng.gen::<u16>());
        packet.set_identifier(rng.gen::<u16>());
        let csum = util::checksum(packet.packet(), 1);
        packet.set_checksum(csum);
        match tx.send_to(packet, addr) {
            Ok(_) => print!("."),
            Err(_) => print!("_"),
        }
    }
}