import sys
from sys import getsizeof
RequestInput = ["cpe:2.3:o:blipcare:wi-fi_blood_pressure_monitor_firmware:-:*:*:*:*:*:*:*","cpe:2.3:h:blipcare:wi-fi_blood_pressure_monitor:-:*:*:*:*:*:*:*","Amazon","Echo","v1","v2","0x626c01e4312659215366e7a25d84ed1a744af5c76f1f36fb65acf13fa79efd1a",1692281734,5,"0x54f6323B2c6723Cec76EC053D5F87c12Fdf6E050"]
OfferInput = [2,15,"0x7061AbB3bD4389612b68d613Cfc8BF053b061A0b","0x626c01e4312659215366e7a25d84ed1a744af5c76f1f36fb65acf13fa79efd1a"]
selectInput = ["0x626c01e4312659215366e7a25d84ed1a744af5c76f1f36fb65acf13fa79efd1a","0x7061AbB3bD4389612b68d613Cfc8BF053b061A0b","0x7061AbB3bD4389612b68d613Cfc8BF053b061A0b","0x7061AbB3bD4389612b68d613Cfc8BF053b061A0b"]
SubmitInput = ["0x626c01e4312659215366e7a25d84ed1a744af5c76f1f36fb65acf13fa79efd1a","QmRRoe2Z8dcCrNzeUmVgeV3R6Ag9Z6rG7qCST6eJvLQUtQ","0x6899b4F73dFd30cb27849EcF51130Dd68c6564bb"]
RateInput = ["0x2033222aa635038614a515dbe66bd65092af335bf2b55dbf4224c70c98893bd4",40]

Datasize = 0.0
for i in RequestInput:
    cursize = getsizeof(i)
    Datasize += cursize
print(f'Data size of Request is {Datasize} Bytes')

datasize = 0.0
for i in OfferInput:
    cursize = getsizeof(i)
    datasize+=cursize
print(f'Data size of offer is {datasize} Bytes')

datasize = 0.0
for i in selectInput:
    cursize = getsizeof(i)
    datasize+=cursize
print(f'Data size of select is {datasize} Bytes')

datasize = 0.0
for i in SubmitInput:
    cursize = getsizeof(i)
    datasize+=cursize
print(f'Data size of submit is {datasize} Bytes')

datasize = 0.0
for i in RateInput:
    cursize = getsizeof(i)
    datasize+=cursize
print(f'Data size of rate is {datasize} Bytes')