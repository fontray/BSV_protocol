import BSV_protocol
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import paho.mqtt.client as mqtt
import base64
import random
import re
import json
from web3 import Web3

# Connect to Ethereum node
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Ensure connection to Ethereum node is successful
if w3:
    print("Connected to Ethereum node")
else:
    print("Failed to connect to Ethereum node")
    exit()

# Read contract ABI
with open('C:\\Users\\yuan\\votestorage\\build\\contracts\\VoteStorage.json', 'r', encoding='utf-8') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

# Set contract address (replace with your deployed contract address)
contract_address = '0x141B6fe360AE280B9bC111838b2DCbE26e0431D8'

# Create contract object
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set default account
account = w3.eth.accounts[0]
w3.eth.defaultAccount = account

def upload_to_blockchain(signature, random_number):
    signature_byte = bytes.fromhex(hex(signature)[2:])
    random_byte = bytes.fromhex(hex(random_number)[2:])
    
    # Ensure the transaction includes the `from` address
    tx_hash = contract.functions.storeVote(signature_byte, random_byte).transact({'from': account})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Transaction receipt:", receipt)


# Define MQTT broker
broker = 'broker.emqx.io'
port = 1883
topic = "Government"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker! Result code: {rc}")
        client.subscribe(topic)
        print(f"Subscribed to topic: {topic}")
    else:
        print(f"Failed to connect, return code {rc}")
        
count = 0        
def on_message(client, userdata, msg):
    # print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    global count
    # Extract the numbers from the received message
    match = re.search(r"\((\d+), (\d+)\)", msg.payload.decode())
    
    if match:
        blind_vote = int(match.group(1))
        blind_r = int(match.group(2))
        # print(f"blind vote: {blind_vote}")
        # print(f"blind r: {blind_r}")
        
        # Sign the extracted values
        blind_msg_sign = BSV_protocol.sign(blind_vote , sK, n)
        blind_r_sign = BSV_protocol.sign(blind_r, sK, n)
        print(f"Government Signed voter {count+1} vote: {blind_msg_sign}")
        print(f"Government Signed r: {blind_r_sign}")
        
        # voter unblind signature
        unblind_msg = BSV_protocol.unblind(blind_msg_sign, b_values[count], pK)
        unblind_r = BSV_protocol.unblind(blind_r_sign, b_values[count], pK)
        print(f"The voter {count+1} ballot with government's sign s:({unblind_msg}, {unblind_r})")
        
        # Verify the signature on ballot
        is_valid = BSV_protocol.verify(unblind_msg, vote_list[count], pK)
        print(f"Is the voter {count+1} signature valid? {is_valid}")
        count += 1
        upload_to_blockchain(unblind_msg, unblind_r)
    
# Connect to MQTT topic
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_start()

# Give it some time to process messages
import time
time.sleep(2)

with open('public_rsa') as f:
    public_Key = f.read() 
    print("Public key:", public_Key)
    pK = RSA.importKey(public_Key)
    
with open('private_rsa') as f:
    private_Key = f.read() 
    print("Private key:", private_Key)
    sK = RSA.importKey(private_Key)
    
n = pK.n

b_values = []
vote_list = []
ballot = []
sign_ballot = []

for i in range(5):
    b = BSV_protocol.gne_blindfactior(pK)  #  voter's blind factor
    r = BSV_protocol.gen_random(32, n)     # voter's random number
    vote = random.choice(["Yes", "No"]) # voter's agree or disagree
    b_values.append(b)
    vote_list.append(vote)
    
    print(f"Voter {i+1} - \n Blind factor 'b': {b} \n Random number 'r': {r} \n Vote : {vote}")
    
    blind_vote, blind_r = BSV_protocol.blinding(vote, r, b, pK)
    
    # print(f"The voter {i+1} blind ballot (m,r)':({blind_vote}, {blind_r})")
    ballot.append((blind_vote, blind_r))
    
    client.publish(topic, f"The voter {i+1} blind ballot (m,r)':({blind_vote}, {blind_r})") 
    
# with open('voter_ballot.txt', 'w') as f:
#     for i, (blind_vote, blind_r) in enumerate(ballot):
#         f.write(f"Voter {i+1} -\n Blind vote : {blind_vote}\n Blind random number : {blind_r}\n")

# Function to get vote by index
def get_vote(index):
    # Call the contract function
    result = contract.functions.getVote(index).call()

    # Extract the signature and random number from the result
    signature, random_number = result

    return signature.hex(), random_number.hex()

index = 3  # Replace with the index of the vote you want to retrieve
signature, random_number = get_vote(index)
print(f"Vote {index + 1}:")
print(f"  Signature: {signature}")
print(f"  Random Number: {random_number}")

time.sleep(10)
client.loop_stop()
