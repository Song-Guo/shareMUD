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


w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
contract_addr = '0xd73729384e5f720E9673B760E52969CfF8F317C1'
filePath = "/Users/skoll/shareMUD_ABI.json"
text = open(filePath, encoding='utf-8').read()
contract_abi = json.loads(text)
contract = w3.eth.contract(address=contract_addr, abi=contract_abi)
accountList = [["0xdCc53851c024f78dc48eA940Ab3def65a4107aa6","0x70bf3a9f14a95d95ca097a52765d12f0b2346c6fa84baacddeaec2e97a27270b"],
 ["0xcA16c80B8dE1997F84fA21B8ae65FFB58c060886","0xfd6d57f6e675f2dfac879aa6d5da701da04d7bee6abc93660d9ed5e8f9750681"],
 ["0x823F0A3893547553498A26856954C7da7b370ff8","0xde5d8f85c008954c62dc5b745dffd699f31851cfc26a680407b417e7a7ae629d"],
 ["0x4F4A1F16c4E4AFe40B258D2850C214a92E2f2f4E","0xcd8917697737a461eccd27483f9e9f80b8c75269dc434216d79c2632c87b4d5f"],
 ["0x2E956CbC07BBF622270b964ACC63786836c47AFC","0x7bd562c158ff887ad030e0fcc9b139654d23abd14b65ea58f793723cb8a8a928"]]


consumerCode = int(0)   #index of list (0~3)
supplierList = [] #index of list (0~3)
rate = [] # rate, 0~50 (solidity have limited ability to deal with float number)
cpe_o = "cpe:2.3:o:blipcare:wi-fi_blood_pressure_monitor_firmware:-:*:*:*:*:*:*:*"
cpe_h = "cpe:2.3:h:blipcare:wi-fi_blood_pressure_monitor:-:*:*:*:*:*:*:*"
budget_ether = int(5) #Budget of consumer, this is only a soft restriction, unit = 1 ether
offers = [] #[price,data_size]
selection = [] #index of list (0~3), note elements of this list must be included by "supplierList"
MUDadd = ["QmRRoe2Z8dcCrNzeUmVgeV3R6Ag9Z6rG7qCST6eJvLQUtQ","QmP3e7NyxKgCgCUJKSRR4Q4iZJqq3QMjMpVYefkjXP9eyy","QmPMKuaufTTPiBPSdEuHGtPLxWPb3EanK6BB84mCS9rFum","IPFS_4"]
#Note this list need to have same length as "selection"

receipts = []
requestInput = [cpe_h,cpe_o,budget_ether]
consumerAddr = accountList[consumerCode][0]
consumerPK = accountList[consumerCode][1]

TransactFunction("sendRequest",consumerAddr,consumerPK,[cpe_h,cpe_o,budget_ether])
print(f'consumer {consumerAddr} published a request, description = {cpe_h,cpe_o},budget = {budget_ether} ethers')
print('\n')


gasConsumption = []
for i in receipts:
    gasConsumption.append(i.gasUsed)
print(gasConsumption)
SumOfGas = 0
for i in gasConsumption:
    SumOfGas += i

print(f'sum of gas consumption = {SumOfGas}')
price_of_gas = 1000000000
#price_of_ETH = int(input("please input price of ETH:(AUD/Ether)"))
price_of_ETH = 3000
ETH_sum = SumOfGas * 20 / price_of_gas
AUD_sum = ETH_sum * price_of_ETH
print(f'sum of ETH consumption = {ETH_sum}, sum of real world money consumption = AUD${AUD_sum} ')

gasConsumption.append(ETH_sum)
gasConsumption.append(AUD_sum)

with open("/Users/skoll/Desktop/test2.csv","a") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(gasConsumption)