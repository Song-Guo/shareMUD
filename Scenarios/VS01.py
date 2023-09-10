from web3 import Web3
import json,time,sys,csv
import configparser,os

#An Ethereum user search for previous request and acquire MUD address of previous submitted MUD file
#Code of Ethereum user address: 0~9

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
def viewBalance():
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
def gasStatistic():
    gasConsumption = []
    for i in receipts:
        gasConsumption.append(i.gasUsed)
    print(gasConsumption)
    SumOfGas = 0
    for i in gasConsumption:
        SumOfGas += i

    print(f'sum of gas consumption = {SumOfGas}')
    price_of_gas = 23.31
    price_of_ETH = 2786.87
    ETH_sum = SumOfGas * price_of_gas / 1000000000
    AUD_sum = ETH_sum * price_of_ETH
    print(f'sum of ETH consumption = {ETH_sum}, sum of real world money consumption = AUD${AUD_sum} ')

    gasConsumption.append(ETH_sum)
    gasConsumption.append(AUD_sum)

    with open("/Users/skoll/Desktop/test.csv","a") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(gasConsumption)



Dir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(Dir,"Env.ini")
print(configPath)
conf = configparser.ConfigParser()
conf.read(configPath)
contract_addr = conf.get('SmartContract',"address")
RPCinterface = conf.get("SmartContract","RPCinterface")
filePath = conf.get("SmartContract","ABIpath")
list1 = conf.sections()
del list1[0]
del list1[0]
del list1[0]
accountList = []
for i in list1:
    curList = []
    curList.append(conf.get(i,'address'))
    curList.append(conf.get(i,"PK"))
    accountList.append(curList)


w3 = Web3(Web3.HTTPProvider(RPCinterface))
text = open(filePath, encoding='utf-8').read()
contract_abi = json.loads(text)
contract = w3.eth.contract(address=contract_addr, abi=contract_abi)

cpe_o = conf.get("request", "cpe_o")
cpe_h = conf.get("request", "cpe_h")
mfctr = conf.get("request", "mfctr")
dev = conf.get("request", "dev")
mdl = conf.get("request", "mdl")
fimwr = conf.get("request", "fimwr")
budget_ether = int(conf.get("request", "budget_ether"))

MUDlist = conf.options("MUDadd")
MUDadd = []
for i in MUDlist:
    MUDadd.append(conf.get("MUDadd",i))


receipts = []

curOpenReq = ViewFunction_noArgu("viewOpenRequests")
curUIDList = []
for i in curOpenReq:
    UID_i = "0x" + i[0].hex()
    description = i[1]
    budget = i[2]
    timeStamp = i[3]
    timeArray = time.localtime(timeStamp)
    requestTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    consumerAddr = i[-1]
    curUIDList.append(UID_i)
    print(f'Request UID = {UID_i},request time = {requestTime}, \ndescription = {description}, consumerAddr = {consumerAddr}')
    print('\n')

curUID = input("To view the submission of specific request, please input selection of UID: ")
print(f'For current UID {curUID}, submission is: ')
Result = ViewFunction("view_submission",[curUID])
for i in Result:
    MUDadd = i[1]
    supplierAddr = i[2]
    print(f'Submission from supplier {supplierAddr}, MUD file address is {MUDadd}')



