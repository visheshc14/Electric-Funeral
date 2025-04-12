## Electric-Funeral

A Combination of Software Defined Network (SDN) And A Multi-Layer Perceptron (MLP) Neural Network That Results In The
Mitigation of DDoS Attacks.

## References 
[A dynamic MLP-based DDoS attack detection method using feature selection and feedback](https://www.sciencedirect.com/science/article/pii/S0167404819301890)

[Deep Learning-based Slow DDoS Attack Detection in SDN-based Networks](https://ieeexplore.ieee.org/document/9289894)

[SDN-Based Intrusion Detection System for Early Detection and Mitigation of DDoS Attacks](https://arxiv.org/ftp/arxiv/papers/2104/2104.07332.pdf)

[A Flexible SDN-Based Architecture for Identifying and Mitigating Low-Rate DDoS Attacks Using Machine Learning](https://ieeexplore.ieee.org/abstract/document/9177002)

![Electric-Funeral Rust - Vishesh Choudhary (1)](https://user-images.githubusercontent.com/36515357/131664283-1ebf89bf-3fc0-4b4d-9d14-e1a909edd1f3.png)

![IMG_4211 Edited (1)](https://user-images.githubusercontent.com/36515357/131669989-38a23255-b0c5-44c2-9fe5-dfa22c4e5eb8.png)

![IMG_4214 Edited (1)](https://user-images.githubusercontent.com/36515357/131672958-fc16003d-3aa1-405a-8990-f3b064e17902.png)

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
<img width="531" alt="Screenshot 2025-04-09 at 3 23 29 PM" src="https://github.com/user-attachments/assets/6bc5bb80-7294-4618-aa19-273c4c67980d" />
<img width="266" alt="Screenshot 2025-04-09 at 3 07 56 PM" src="https://github.com/user-attachments/assets/081c75f9-d28f-438a-a5e5-a97bc1c6ccd7" />
<img width="266" alt="Screenshot 2025-04-09 at 3 07 36 PM" src="https://github.com/user-attachments/assets/51a9f13d-f0c6-4ed1-ad28-52ac7ecdba69" />
<img width="1517" alt="Screenshot 2025-04-09 at 1 57 21 PM" src="https://github.com/user-attachments/assets/c9e890d6-9a14-4338-a29c-b0c356fc1bf9" />
<img width="1329" alt="Screenshot 2025-04-09 at 1 54 33 PM" src="https://github.com/user-attachments/assets/cd95b5f2-a0f8-4c10-9142-2b6bab76235a" />
<img width="1329" alt="Screenshot 2025-04-09 at 1 45 59 PM" src="https://github.com/user-attachments/assets/4724e053-06c3-4f5f-8d2c-2ee8cbecedd5" />
