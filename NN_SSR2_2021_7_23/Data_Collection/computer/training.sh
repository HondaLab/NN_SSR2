#!/bin/bash
cd ../..
sleep 1
cd Learning/
sleep 1
python3 NN_h1.py
sleep 3
cd output_chainer_neural_network_hidden_1/
sleep 1
./send.sh
