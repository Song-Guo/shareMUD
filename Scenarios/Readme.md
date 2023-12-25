This folder contains automated test scripts designed to validate the smart contract. Before you use these scripts, please follow the instructions below.

0. Deploy a private Ethereum network on your local environment and deploy the smart contract onto this network. Also, you need to create five user accounts to facilitate the completion of the testing procedure.
1. These instructions are tailored for Unix-based systems such as Ubuntu or MacOS.
2. Obtain the following parameters necessary for the testing process:
    - Address of the smart contract on the Ethereum private network
    - Web3 RPC interface of local Ethereum network (typically http://127.0.0.1:7545 by default in Ganache Ethereum blockchain)
    - Path to the ABI file (an ABI file is available within this current folder).
    - For each of 5 Ethereum users:
        (a) Ethereum address
        (b) Private key associated with each address
3. Update the **Env.ini** file with these parameters
4. To execute the Python3 test script, ensure you have installed the python3 environment on your workstation and installed the following packages:
    - Web3.py
    - json,time,sys,csv
    - configparser,os
    Before running the scripts, it's recommended to run the following command in your terminal:
    ```
    pip3 install web3
    ```
5. Execute .py file with python3.
