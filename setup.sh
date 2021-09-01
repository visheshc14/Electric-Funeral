#!/bin/sh

pip install -r requirements.txt &&
        git submodule update --init --recursive &&
        cd dos-attacks &&
        cargo build --release
