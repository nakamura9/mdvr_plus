import sys
import os
import hmac 
import hashlib
import json
import datetime


def generate_license():
    if not os.path.exists('mdvr_key.txt'):
        print('No key text was found!')
        input('Press any key to exit.')
        sys.exit()

    hid = None
    with open('mdvr_key.txt') as f:
        hid = f.read()

    
    customer = input('Enter a customer name: ')
    devices = input('Enter the number of devices the customer can manage: ')
    print('Generating License')
    timestamp = datetime.datetime.now()

    license_data = {
        'customer': customer,
        'devices': devices,
        'timestamp': timestamp.strftime('%d-%m-%Y %H:%M:%S'),
    }
    license_str = json.dumps(license_data)
    data_string = hid + license_str

    byte_data = bytes(data_string, 'ascii')
    hash = hashlib.sha3_512(byte_data).hexdigest()

    license = {
        'signature': hash,
        'license':license_data
    }
    with open('license.json', 'w') as lic_file:
        json.dump(license, lic_file)

    input('Generated license successfully! Press any key to exit.')



print('MDVR+ License Creator.')
print("=========================")
print(os.getcwd())
print("""Select an option:
1. Generate a license
2. Exit""")
option = input("> ")
while option not in ['1', '2']:
    option = input("> ")

if option == '2':
    sys.exit()

else:
    generate_license()

