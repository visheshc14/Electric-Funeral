

extern crate pnet;

use std::env;

mod icmp_flood;

fn main() {

    println!("Electric Funeral Rust - Vishesh Choudhary");
    println!();
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        panic!("Not enough arguments");
    }
    let attack_name = &args[1];
    let addr = &args[2];
    run_attack(attack_name)(addr);
}

fn run_attack(attack: &String) -> Box<dyn Fn(&String)> {
    match attack.as_str() {
        "ping-flood" => Box::new(icmp_flood::run),
        _ => return Box::new(move |a| panic!("No attack named {}", a)),
    }
}
