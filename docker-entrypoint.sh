#!/bin/bash
set -e

# Initialize OpenVSwitch if needed
if [ ! -f /etc/openvswitch/conf.db ]; then
    ovsdb-tool create /etc/openvswitch/conf.db
fi

# Start Open vSwitch
service openvswitch-switch start

# Wait for OpenVSwitch to be ready
while ! ovs-vsctl show > /dev/null 2>&1; do
    echo "Waiting for OpenVSwitch to be ready..."
    sleep 1
done

# Create a bridge for Mininet if it doesn't exist
if ! ovs-vsctl br-exists s1; then
    ovs-vsctl add-br s1
fi

# Start the POX controller if needed
if [[ "$*" == *"create_network.py"* ]]; then
    cd /app && python3 network_controller.py --gen-data &
    sleep 2
fi

exec "$@" 