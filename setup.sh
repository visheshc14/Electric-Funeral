#!/bin/sh

pip3 install -r requirements.txt &&
        git submodule update --init --recursive &&
        cd Attacks-Rust &&
        cargo build --release
