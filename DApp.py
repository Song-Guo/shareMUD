from web3 import Web3
import json,time,sys,csv
from time import sleep

def TransactFunction(function_name, Eth_address, Private_key, ListOfParameters):
    print(
        f'Send data to method "{function_name}" with {ListOfParameters} from account{Eth_address} to smart contract {contract_addr}'
    )
    nonce = w3.eth.get_transaction_count(Eth_address)
    data_tx = contract.functions[function_name](*ListOfParameters).build_transaction(
        {
            'from': Eth_address,
            'nonce': nonce
        }
    )
    tx_create = w3.eth.account.sign_transaction(data_tx, Private_key)

    # 7. Send tx and wait for receipt
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f'Tx successful with hash: {tx_receipt.transactionHash.hex()}')
    receipts.append(tx_receipt)
def ViewFunction(_function_name,list_of_Argu):
    result = contract.functions[_function_name](*list_of_Argu).call()
    return(result)
def ViewFunction_noArgu(_function_name):
    result = contract.functions[_function_name]().call()
    return(result)
def TransactPayableFunction(function_name, eth_address, private_key, list_parameters, msgValue):
    print(
        f'Attempting send data to method "{function_name}" with {list_parameters} from account{eth_address} to smart contract {contract_addr}'
    )
    nonce = w3.eth.get_transaction_count(eth_address)
    data_tx = contract.functions[function_name](*list_parameters).build_transaction(
        {
            'from': eth_address,
            'nonce': nonce,
            'value': msgValue*(10**18)
        }
    )
    tx_create = w3.eth.account.sign_transaction(data_tx, private_key)

    # 7. Send tx and wait for receipt
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f'Tx successful with hash: {tx_receipt.transactionHash.hex()}')
    receipts.append(tx_receipt)
    # Or change Solidity function，allow consumer pay ETH automatically instead of manually setting msg.value
def viewAllBalance():
    BalanceList = []
    for i in accountList:
        curList = []
        curAddr = i[0]
        balance = w3.eth.get_balance(curAddr)/(10**18)
        curList.append(curAddr)
        curList.append(balance)
        BalanceList.append(curList)
    print("accounts and balance (Ether) is:","\n")
    for i in BalanceList:
        print(i,"\n")
receipts = []

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
contract_addr = '0x0195bAA2405662cc0d9d0D8A686fb6320e3ab669'
filePath = "/Users/skoll/shareMUD_ABI.json"
text = open(filePath, encoding='utf-8').read()
contract_abi = json.loads(text)
contract = w3.eth.contract(address=contract_addr, abi=contract_abi)
accountList = [["0x5Af33cEE5f60A8Bb52c3FbDe4431978b71D6A77F","0x15e2a7b65b7e17d439f90562af5fa50c7e833fa50460b705aaf1391f23f048f0"],
 ["0xfa7A74081a705758A089394266C9b3Eb7ee888f9","0x6c519b1adf37083b63dd795ad16ac018596156c3a60ce86272105fe81b4bd800"],
 ["0xF4243eac1E31DE16C7Be7e3869bB0Aa704B05005","0xf1c8f3648df260b0c994a2e76de38fdb8cc77de872cd0df8abf9b71212233ccb"],
 ["0x4d8874E43d73596C0B28783f4bCbbd8f4c2e230F","0x6078b9fcff4722a249ffdd65e619fb758d892e187dad2558e2b538926b217baa"],
 ["0xa81FC27026DE1cC229ca58B9311fb79BfB1E6890","0xca166358b1bb206cbbe1c73ea440de512c08fe04e29cbb39451b3b9493494441"]]

CurAccount = accountList[1][0]
CurPK = accountList[1][1]
balance = w3.eth.get_balance(CurAccount)/(10**18)
print(f'Welcome! Current Account = {CurAccount} Ether1, Current Balance is {balance}, please select your role')
Role = input(' 1 for Consumer; \n 2 for Supplier; \n 3 for data viewer \n')
if Role == '1':
    select1 = input('Please select your action:\n 1 for post a request; \n 2 for make selection for an existing request; \n 3 for rate a supplier \n')
    if select1 == '1':
        description = {'cpe_h':"None",'cpe_o':"None",'mfctr': "None", 'dev':"None",'mdl':"None",'fimwr':"None"}
        select2 = input('Step 1: need to describe your IoT device. Do you have CPE of your IoT device? y/n \n')
        if select2 == 'y':
            cpe_h = input('Please input the CPE of hardware: \n')
            cpe_o = input('Please input the CPE of firmware: \n')
            description['cpe_h'] = cpe_h
            description['cpe_o'] = cpe_o
            select3 = ('Do you still wish to provide legacy description of IoT device? y/n \n')
            if select3 == 'y':
                mfctr = input('Please input the Manufacturer of IoT device: \n')
                dev = input('Please input the device name of IoT device: \n')
                mdl = input('Please input the model of IoT device: \n')
                fimwr = input('Please input the firmware version of IoT device: \n')
                description['mfctr'] = mfctr
                description['dev'] = dev
                description['mdl'] = mdl
                description['fimwr'] = fimwr
            elif select3 == 'n':
                print('Proceed to next step')
            else:
                print('invalid input, system exit!')
                sys.exit()
        elif select2 == 'n':
            print('Use legacy description of IoT device, please answer following questions: \n')
            mfctr = input('Please input the Manufacturer of IoT device: \n')
            dev = input('Please input the device name of IoT device: \n')
            mdl = input('Please input the model of IoT device: \n')
            fimwr = input('Please input the firmware version of IoT device: \n')
            
            description['mfctr'] = mfctr
            description['dev'] = dev
            description['mdl'] = mdl
            description['fimwr'] = fimwr
        else:
            print('invalid input, system exit!')
            sys.exit()
        select4 = input(f'Press y to confirm transaction if correct: \n cpe_h:{description["cpe_h"]} \n cpe_o:{description["cpe_o"]} \n Manufacturer: {description["mfctr"]} \n Device Name:{description["dev"]} \n Model Name:{description["mdl"]} \n Firmware: {description["fimwr"]} \n')
        if select4 == 'y':
            budget = int(input('Please input budget in Ether, pure number \n'))
            ParaList = [description['cpe_h'], description['cpe_o'], description['mfctr'], description['dev'],description['mdl'],description['fimwr'],budget]
            TransactFunction('sendRequest', CurAccount, CurPK, ParaList)
        else:
            print('Transaction Cancelled.')
            sys.exit()

    elif select1 == '2' :
        pass
#1. Input UID
#2. Get Offer List
#3. Input supplier address to select
#4. Confirm transaction, send transaction
    elif select1 == '3':
        pass
#1. Input UID
#2. Get Submission List
#3. Print address --> input rate
#4. Confirm transaction, send transaction
    else:
        print('invalid input, system exit!')
        sys.exit()
elif Role == '2':
    print("Current open request include: \n")
    print(ViewFunction_noArgu("viewOpenRequests"))
    UID = input("Please select your offer by inputing UID of it: \n")
    UID_1 = "0x" + UID.hex()
    Price = int(input("Please input price in Ether: \n"))
    size_data = int(input("Please input size of data in kb: \n"))
    select1 = input(f'You are going to provide an offer for request {UID}, price of your offer is {Price} Ether, size of your MUD file is {size_data} kB. \n Press y to continue: \n')
    if select1 == 'y':
        ParaList = [UID,Price,size_data]
        TransactFunction("")
#1. Offer
#   1.1 show requests, input UID
#   1.2 input price and size of data(Do we still need the size of data?)
#   1.3 Confirm and send transaction
#2. Submit
#   2.1 Input UID, use a view function to confirm if current user a selected supplier (If not, quit)
#   2.2 If user a selected supplier: 
elif Role == '3':
    pass
else:
    print(f'invalid input {Role}, check again!')
    sys.exit()