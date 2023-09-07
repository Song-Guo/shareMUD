This folder contains automatic test scripts for smart contract. Before attemping to verify the function of this smart contract with these scripts, please follow these instructions;

0. Deploy a private Ethereum network on your local environment, and deploy the smart contract on this network. Also you need to create 5 users to finish the test procedure.
1. Assume scripts are running on an Unix operating system (Ubuntu/MacOS prefered)
2. Get following parameters:
    -- Address of the smart contract on Ethereum private network
    -- web3 RPC interface of local Ethereum network(Usually http://127.0.0.1:7545 as default in Ganache Ethereum blockchain)
    -- Path of ABI file, we prepared an ABI file within this current folder.
    -- For each of 5 Ethereum users:
        --Address
        --Private Key
3. Update Env.ini file with these parameters
4. To execute python3 test script, you need install python3 environment in your workstation, and install following packets:
    --Web3.py
    --json,time,sys,csv
    --configparser,os
    Suggest to run following script in terminal before running scripts
    pip3 install web3
5. Execute .py file with python3.