# DoS Attacks
Rust implementations of Denial of Service attacks, currently only the ICMP flood
attack is implemented.

## Requirements
- Rust
- Cargo

## Build
```sh
cargo build
```

## Run
You will probably need to run the resulting binary with sudo:
```sh
sudo ./target/debug/dos-attacks ping-flood 127.0.0.1
```
