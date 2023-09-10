from web3 import Web3
import json,time,sys,csv
import configparser,os


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
consumerCode = int(4)   #index of list (0~4)
supplierList = [0,1,2,3] #index of list (0~4)
rate = [] # rate, 0~50 (solidity have limited ability to deal with float number)
cpe_o = "cpe:2.3:o:blipcare:wi-fi_blood_pressure_monitor_firmware:-:*:*:*:*:*:*:*"
cpe_h = "cpe:2.3:h:blipcare:wi-fi_blood_pressure_monitor:-:*:*:*:*:*:*:*"
mfctr = "Amazon"
dev = "Echo"
mdl="v1"
fimwr ="v2"
budget_ether = int(5) #Budget of consumer, this is only a soft restriction, unit = 1 ether
offers = [[2,15],[2,10],[1,8],[3,12]] #[price,data_size]
selection = [0,1,2] #index of list (0~4), note elements of this list must be included by "supplierList"
MUDadd = ["QmRRoe2Z8dcCrNzeUmVgeV3R6Ag9Z6rG7qCST6eJvLQUtQ","QmP3e7NyxKgCgCUJKSRR4Q4iZJqq3QMjMpVYefkjXP9eyy","QmPMKuaufTTPiBPSdEuHGtPLxWPb3EanK6BB84mCS9rFum","IPFS_4"]
#Note this list need to have same length as "selection"
submitList = [0,1] #should be included by selection!

receipts = []
requestInput = [cpe_h,cpe_o,mfctr,dev,mdl,fimwr,budget_ether]
consumerAddr = accountList[consumerCode][0]
consumerPK = accountList[consumerCode][1]

TransactFunction("sendRequest",consumerAddr,consumerPK,requestInput)
print(f'consumer {consumerAddr} published a request, description = {cpe_h,cpe_o},budget = {budget_ether} ethers')
print('\n')

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

#curUID = input("please input selection of UID, suppliers will start to submit offers: ")
curUID = curUIDList[-1]

print('\n')

if offers != []:
    for i in offers:
        i.insert(0,curUID)

    j = 0
    for i in supplierList:
        curAddr = accountList[i][0]
        curPK = accountList[i][1]
        curOffer = offers[j]
        TransactFunction("offer",curAddr,curPK,curOffer)
        j+=1
        print(f'supplier {curAddr} submitted an offer for request {curUID}, \n price = {curOffer[1]},size of data = {curOffer[2]}')
        print('\n')
        #sleep(5)


    curOffer = ViewFunction("viewOfferList",[curUID])
    print('For current request, we have following offers:')
    for i in curOffer:
        print(f'supplier = {i[2]}, price = {i[0]} ethers, \nsize of data = {i[1]} kB')
    #sleep(30)
else:
    gasStatistic()
    sys.exit()

if selection != []:
    SumOfEth = int()
    selectionList = []
    for i in selection:
        curSupplier = accountList[i][0]
        curPrice = offers[i][1]
        selectionList.append(curSupplier)
        SumOfEth+=int(curPrice)

    print(f'Selected suppliers are: {selectionList}, \n Need to pay {SumOfEth} ether of ETH!')

    print(f'Consumer "{consumerAddr}" will pay {SumOfEth} ethers to suppliers\n{selectionList} to get MUD file')
    #decision = input("Press Enter key to continue transaction, otherwise enter 'C' to cancel: ")
    #if decision == "C":
    #    sys.exit()
    print(f'Transaction confirmed, consumer will pay {SumOfEth} Ether(s) to smart contract.')
    viewBalance()
    TransactPayableFunction("select_payment", consumerAddr, consumerPK, [curUID,selectionList], SumOfEth)
    print(f'Transaction completed, consumer have paid {SumOfEth} Ether to smart contract')
    viewBalance()

    print("Supplier started to submit MUD file offchain storage address to blockchain, \n then get ether from smart contract")
    j=0
else:
    gasStatistic()
    sys.exit()
    
if submitList != []:
    for i in submitList:
        supplierAddr = accountList[i][0]
        supplierPK = accountList[i][1]
        TransactFunction("submit",supplierAddr,supplierPK,[curUID,MUDadd[j]])
        j+=1
    viewBalance()
    submission = ViewFunction("view_submission",[curUID])
    print(f'Request (UID {curUID}) completed, original request and MUD file submission from supplier are:')
    for i in submission:
        UID = '0x'+ str(i[0].hex())
        output = f'UID = {UID},MUD IPFS address = {i[1]}, supplier address = {i[2]} \n '
        print(output)
else:
    gasStatistic()
    sys.exit()

if rate != []:
    RateList = []
    j = 0
    for i in selection:
        CurRate = rate[j]
        CurSupplier = accountList[i][0]
        result = ViewFunction("ViewRate", [CurSupplier])
        for k in result:
            UID = '0x' + k[0].hex()
            print(f'UID = {UID}, Rate = {k[1]} \n')
        TransactFunction("rate", consumerAddr, consumerPK, [curUID,CurSupplier,CurRate])
        result = ViewFunction("ViewRate", [CurSupplier])
        print(f'Existing rate of supplier {CurSupplier} are: \n')
        for k in result:
            UID = '0x' + k[0].hex()
            print(f'UID = {UID}, Rate = {k[1]} \n')
        j+=1
else:
    gasStatistic()
    sys.exit()

gasStatistic()




