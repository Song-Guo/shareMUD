import configparser, os

Dir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(Dir,"Env.ini")
print(configPath)

conf = configparser.ConfigParser()

conf.read(configPath)

SCaddress = conf.get('SmartContract',"address")
print(SCaddress)

list1 = conf.sections()
del list1[0]
addressList = []
for i in list1:
    curList = []
    curList.append(conf.get(i,'address'))
    curList.append(conf.get(i,"PK"))
    addressList.append(curList)

print(addressList)