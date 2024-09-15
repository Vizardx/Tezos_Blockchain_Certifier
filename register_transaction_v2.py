import requests
import json
import time
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv
from pytezos import pytezos
from decimal import Decimal

# Load .env
load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
DIPLOMAS_API_URL = os.getenv("DIPLOMAS_API_URL")
TEZOS_ADDRESS = os.getenv("TEZOS_ADDRESS")

def get_working_node(): #Sometimes the node can input an error later, when signing the transaction. Put first any of the other 2 nodes to solve it.
    nodes = [
        "https://mainnet.smartpy.io",
        "https://rpc.tzbeta.net",  # Test Node
        "https://mainnet.api.tez.ie",
        "https://mainnet-tezos.giganode.io"
    ]
    for node in nodes:
        try:
            response = requests.get(f"{node}/chains/main/blocks/head")
            if response.status_code == 200:
                print(f"Working node found: {node}")
                return node
        except requests.exceptions.RequestException as e:
            print(f"Node {node} failed: {e}")
    raise Exception("No working Tezos nodes available")

def register_transaction(private_key, contract_address, data_hash):
    node_url = get_working_node()
    pytezos_instance = pytezos.using(shell=node_url, key=private_key)
    
    # Create the transacction
    transaction = pytezos_instance.transaction(
        destination=contract_address,
        amount=0,        
        parameters={
            'entrypoint': 'default',
            'value': {'string': data_hash}
        }
    ).autofill(gas_limit=1385, storage_limit=71)  # Change gas_limit or storage as needed, staying always over the node minimum

    # Firmar y enviar la transacción
    signed_transaction = transaction.fill().sign().inject()

    # Extraer información para los datos de Merkle
    blockchain_merkle_root =f"branch:{signed_transaction.get('branch', '')}"
    blockchain_merkle_proof = (
        f"Block:{signed_transaction.get('hash', '')},"
        f"protocol:{signed_transaction.get('protocol', '')},"
        f"chain_id:{signed_transaction.get('chain_id', '')}"
    )
    
    print("Transaction sent, the operation hash is:", signed_transaction['hash'])
    print(signed_transaction) # Debug info, comment on production
    
    return signed_transaction['hash'], blockchain_merkle_root, blockchain_merkle_proof, node_url

def main():
    diploma_id = "x" # I use a GET with the ID to retrieve the information to hash from our API REST, you can delete this part and input the data on json format
    diploma_api_url = f"{DIPLOMAS_API_URL}{diploma_id}" # I use a GET with the ID to retrieve the information to hash from our API REST, you can delete this part
    response = requests.get(diploma_api_url) # I use a GET with the ID to retrieve the information to hash from our API REST, you can delete this part
    diploma_data = response.json() # I use a GET with the ID to retrieve the information to hash from our API REST, you can delete this part
    
    data_to_hash = { # I use a GET with the ID to retrieve the information to hash from our API REST, you can delete this part
        k: v for k, v in diploma_data.items() if not k.startswith("blockchain_")
    }
    
    os.makedirs("Transaction_verifications", exist_ok=True) # We save the hashed information to verify it any time if needed
    with open(f"Transaction_verifications/{diploma_id}.json", "w") as f:
        json.dump(data_to_hash, f)
    
    data_str = json.dumps(data_to_hash, sort_keys=False)
    data_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    transaction_hash, blockchain_merkle_root, blockchain_merkle_proof, node_url = register_transaction(PRIVATE_KEY, CONTRACT_ADDRESS, data_hash)
    
    '''# I use a PUT with the ID to send the transaction information to our API REST, you can delete this part
    # Adjust timestamp to your needs
    timestamp = (int(time.time()))  # Hora actual en segundos
    
    
    update_payload = {
        "blockchain_certificate_id": transaction_hash,
        "blockchain_tx_id": f"https://tzkt.io/{transaction_hash}",
        "blockchain_hash": data_hash,
        "blockchain_merkle_root": blockchain_merkle_root,
        "blockchain_merkle_proof": blockchain_merkle_proof,
        "blockchain_timestamp": timestamp
    }
    
    response = requests.put(diploma_api_url, json=update_payload, headers={'Content-Type': 'application/json'})
    response.raise_for_status()
    
    print("Diploma data updated successfully.")
    print(response.json())'''

if __name__ == "__main__":
    main()
