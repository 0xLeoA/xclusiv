from web3 import * 
import json

unlock_address = "0x627118a4fB747016911e5cDA82e2E77C531e8206" # unlock contract address
private_key = "46f544a94d8f67dbe5070b6ca15b2c5a5fcff008cff23eb2402b79eca409ad57" #account private key
account_address = "0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7"
goerli = Web3(HTTPProvider('https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

def estimateGas(function_name, args):
    data = unlock.encodeABI(fn_name=function_name, args=args)
    transaction = {
    'to': unlock_address,  # Contract address
    'value': 0,  # Ether value (if sending Ether)
    'data': data,  # Encoded function call data
    'nonce': goerli.eth.get_transaction_count(account_address),  # Sender's address
    'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
    }
    estimated_gas = goerli.eth.estimate_gas(transaction)
    return estimated_gas


with open('unlock_abi.json', 'r') as abi_file:
    unlock_abi = json.load(abi_file)
# initialize unlock contract
unlock = goerli.eth.contract(address=unlock_address, abi=unlock_abi)

with open('lock_abi.json', 'r') as abi_file:
    lock_abi = json.load(abi_file)

lock_address = "0x59503e8F59147A97CBA9F32A97154787aC53D4BF"
lock = goerli.eth.contract(address="0x59503e8F59147A97CBA9F32A97154787aC53D4BF", abi=lock_abi)
data = lock.encodeABI(fn_name='purchase', args=[[10**19], ['0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7'], ['0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7'], ['0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7'], [bytes(12)]])
print(data)
transaction = {
                            'to': lock_address,  # Contract address
                            'value': 0,  # Ether value (if sending Ether)
                            'data': data,  # Encoded function call data
                            'nonce': goerli.eth.get_transaction_count(account_address),  # Sender's address
                            'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
                            'gas': 1100000, 
                            'gasPrice': goerli.eth.gas_price
                            }
account = goerli.eth.account.from_key(private_key)
signed_transaction = account.sign_transaction(transaction)
tx_hash = goerli.eth.send_raw_transaction(signed_transaction.rawTransaction)
print(f"Transaction sent with hash: {tx_hash.hex()}")
receipt = goerli.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # Adjust the timeout as needed
if receipt and receipt['status'] == 1:
                                    # Transaction was successful
    print(f"Transaction confirmed in block {receipt['blockNumber']}")