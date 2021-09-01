## Electric-Funeral

A Combination Of Software Defined Network (SDN) And A Multi-Layer Perceptron (MLP) Neural Network That Results In The
Mitigation of DDoS Attacks.

## Requirements
- python3
- pip
- rust
- cargo

## Installation
```
setup.sh
```

## Generating data
First start the controller in generate data mode:
```
./network_controller.py --gen-data
```

Then start the network in normal interactions training mode (this uses mininet
so it will probably require root privileges to run):
```
./create_network --normal
```

Once done, train for the attack state. Start the controller in generate attack
data mode:
```
./network_controller.py --attack --gen-data
```

Then start the network in attack interactions training mode:
```
./create_network --all-attack
```

## Training the MLP
Simply run the following:
```
./network_controller.py --train
```

## Run DDoS Mitigation
Start the controller in detection mode:
```
./network_controller.py --detect
```

Then start the network in attack and CLI mode:
```
./create_network --attack --cli
```

The user should be able to ping the attack target with the following command:
```
u0 ping t0
```
