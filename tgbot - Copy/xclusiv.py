from telegram import *
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    CallbackContext,
)

from collections import defaultdict

import re
import json

from web3 import Web3, HTTPProvider, contract
from ens import ENS
 # Initialize a Web3 instance and connect to an Ethereum node
w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/49271972f9ae491080258954dfc45531'))
goerli = Web3(HTTPProvider('https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

    # Initialize the ENS resolver
ens = ENS.from_web3(w3)

link_id_to_data = defaultdict(dict)
portal_id_to_data = defaultdict(dict)
group_id_to_data = defaultdict(dict)
counter_to_data = defaultdict(dict)

unlock_address = "0x627118a4fB747016911e5cDA82e2E77C531e8206" # unlock contract address
private_key = "46f544a94d8f67dbe5070b6ca15b2c5a5fcff008cff23eb2402b79eca409ad57" #account private key
account_address = "0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7"
image_url = 'https://europe1.discourse-cdn.com/standard21/uploads/nouns/original/2X/c/caec3989eabc016c06a862ff90c2d9fede6ab676.jpeg'  # Replace with the actual image URL


with open('unlock_abi.json', 'r') as abi_file:
    unlock_abi = json.load(abi_file)
with open('erc20abi.json', 'r') as abi_file:
    erc20_abi = json.load(abi_file)
with open('lock_abi.json', 'r') as abi_file:
    lock_abi = json.load(abi_file)
# initialize unlock contract
unlock = goerli.eth.contract(address=unlock_address, abi=unlock_abi)

def estimateGas(function_name, args):
    data = unlock.encodeABI(fn_name=function_name, args=args)
    transaction = {
    'to': unlock_address,  # Contract address
    'value': 0,  # Ether value (if sending Ether)
    'data': data,  # Encoded function call data
    'nonce': w3.eth.get_transaction_count(account_address),  # Sender's address
    'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
    }
    estimated_gas = goerli.eth.estimate_gas(transaction)
    return estimated_gas

link_id = 1
counter = 0

chain_name_to_chainid = {"Neon EVM": 245022926,"Goerli": 5, "Polygon Mumbai": 80001, "Polygon ZkEVM": 1442, "Arbitrum": 421613, "Base": 84531, "Scroll": 534351, "Linea": 59144, "Celo": 44787, "Mantle": 5001, "Gnosis": 10200}


latest_context = None



def XclusivTgBot(): 



    def is_valid_address(address):
        # Ethereum address regex pattern
        ethereum_address_pattern = re.compile(r'^0x[0-9a-fA-F]{40}$')
        
        # Check if the address matches the pattern
        if ethereum_address_pattern.match(address):
            return True
        else:
            return False
        
    def is_valid_wallet_address(address):
        if is_valid_address(address):
            return True
        elif address.endswith('.eth') and address != ".eth":
            
            try :
                ethereum_address = ens.address(address)
                print(ethereum_address)
                if ethereum_address == None: 
                    return False
                else: 
                    return True
            except:
                return False
        else: 
            return False


    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        latest_context = context
        # is message is in dms
        if update.message.chat.id == update.message.from_user.id:

            # if /start has a portal id attached, complete security verification
            if update.message.text != "/start":
                text=update.message.text

                portal_id = int(text.split(" ")[1])
                print(f'Found portal id: {portal_id}')
                
                # if portal is created for given id
                if portal_id_to_data[portal_id]:

                    main_chat = await context.bot.get_chat(portal_id_to_data[portal_id
                    
                ]["main_chat_id"])

                    if portal_id_to_data[portal_id]["token_action"] == "send":
                        if portal_id_to_data[portal_id]["token"] != "custom":
                            if portal_id_to_data[portal_id]["lock_contract"]:
                                url = f'http://10.6.1.35:3000/verify?action={portal_id_to_data[portal_id]["token_action"]}&receiver_address={portal_id_to_data[portal_id]["receiver_address"]}&chainid={chain_name_to_chainid[portal_id_to_data[portal_id]["receiving_chain"]]}&token={portal_id_to_data[portal_id]["token"]}&amount={portal_id_to_data[portal_id]["token_amount"]}&type={portal_id_to_data[portal_id]["token_type"]}&mainchatid={portal_id_to_data[portal_id]["main_chat_id"]}&chatname={main_chat.title}&lock={portal_id_to_data[portal_id]["lock_contract"]}'   
                            else:
                                url = f'http://10.6.1.35:3000/verify?action={portal_id_to_data[portal_id]["token_action"]}&receiver_address={portal_id_to_data[portal_id]["receiver_address"]}&chainid={chain_name_to_chainid[portal_id_to_data[portal_id]["receiving_chain"]]}&token={portal_id_to_data[portal_id]["token"]}&amount={portal_id_to_data[portal_id]["token_amount"]}&type={portal_id_to_data[portal_id]["token_type"]}&mainchatid={portal_id_to_data[portal_id]["main_chat_id"]}&chatname={main_chat.title}'
                        else:
                            if portal_id_to_data[portal_id]["lock_contract"]:
                                url = f'http://10.6.1.35:3000/verify?action={portal_id_to_data[portal_id]["token_action"]}&receiver_address={portal_id_to_data[portal_id]["receiver_address"]}&chainid={chain_name_to_chainid[portal_id_to_data[portal_id]["receiving_chain"]]}&token=custom&type={portal_id_to_data[portal_id]["token_type"]}&contract={portal_id_to_data[portal_id]["contract_address"]}&amount={portal_id_to_data[portal_id]["token_amount"]}&mainchatid={portal_id_to_data[portal_id]["main_chat_id"]}&chatname={main_chat.title}&lock={portal_id_to_data[portal_id]["lock_contract"]}'
                            else:
                                url = f'http://10.6.1.35:3000/verify?action={portal_id_to_data[portal_id]["token_action"]}&receiver_address={portal_id_to_data[portal_id]["receiver_address"]}&chainid={chain_name_to_chainid[portal_id_to_data[portal_id]["receiving_chain"]]}&token=custom&type={portal_id_to_data[portal_id]["token_type"]}&contract={portal_id_to_data[portal_id]["contract_address"]}&amount={portal_id_to_data[portal_id]["token_amount"]}&mainchatid={portal_id_to_data[portal_id]["main_chat_id"]}&chatname={main_chat.title}'
                    else:
                        url = f'http://10.6.1.35:3000/verify?action={portal_id_to_data[portal_id]["token_action"]}&chainid={chain_name_to_chainid[portal_id_to_data[portal_id]["receiving_chain"]]}&contract={portal_id_to_data[portal_id]["contract_address"]}&amount={portal_id_to_data[portal_id]["token_amount"]}&type={portal_id_to_data[portal_id]["token_type"]}&mainchatid={portal_id_to_data[portal_id]["main_chat_id"]}&chatname={main_chat.title}'

                    inline_keyboard = [[InlineKeyboardButton(text="Complete access criteria", url=url)]]


                    await update.message.reply_text(text=f"""💫🌀 *Xclusiv Protection Bot*\n\nPress this button to get access to '{main_chat.title}'""", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))
                    print("Sent user verification button")
                    return

                else: 
                    print("Portal id not found")
            else:

                caption = """💫*The ultimate free bot for creating exclusive telegram groups!*\n\nCreate holder-only telegram groups, have members stake tokens, or require payment in exchange for access\n\n`/setup`— Create portal & configure settings\n`/help`—Learn more
            """
                media = InputMediaPhoto(media=image_url, caption=caption, parse_mode='Markdown')

                await update.message.reply_media_group([media])


    async def setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            latest_context = context
            # if message isn't in dms, don't do anything 
            if not update.message.chat.id == update.message.from_user.id:
                return 
            print(update)
            global link_id
            global counter

            group_id_to_data[str(update.message.chat.id)]["counter"] = counter
            counter += 1
            counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                "link_id"
            ] = link_id
            counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                "started_bot"
            ] = True
            link_id += 1
            counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                "setup_step"
            ] = "token_action"
            keyboard = [
                [
                    InlineKeyboardButton("Verify Token Holdings", callback_data="verify"),
                    InlineKeyboardButton("Stake Tokens", callback_data="stake"),
                ],
                [InlineKeyboardButton("Pay for access", callback_data="send")],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                "latest_bot_message"
            ] = await update.message.reply_text(


                
                """🔰 *Xclusiv Robot V1.0* 🔰\n\nTo begin, click below and select the action you will require members to perform to gain access to your telegram group
    """,
                reply_markup=reply_markup, parse_mode="Markdown"
            )


    async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        latest_context = context
        # print(f"New message: {update.message}")
        if update.message.chat_shared:
            print(update.message)
            if link_id_to_data[
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "link_id"
                ]
            ]:
                link_id_to_data[
                    counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["link_id"]
                ]["main_chat_id"] = update.message.chat_shared.chat_id
                print("Portal and Main Chat linked!")
                if counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_action"] == "verify":
                    if counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_type"] == "erc20":
                        await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Setup Complete*\n\nDirect members to your portal channel. Once they verify that they hold at least {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"]} of your tokens they will be invited to your group ', parse_mode="Markdown")
                    else : 
                        await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Setup Complete*\n\nDirect members to your portal channel. Once they verify that they hold at least one of your NFTs they will be invited to your group ', parse_mode="Markdown")
                elif counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_action"] == "stake":
                    if counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_type"] == "erc20":
                        await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Success!*\n\nDirect members to your portal channel. Once they stake {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"]} of your tokens they will be invited to your group!', parse_mode="Markdown")
                    else : 
                        await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Success!*\n\nDirect members to your portal channel. Once they verify stake one of your NFTs they will be invited to your group!', parse_mode="Markdown")
                elif counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_action"] == "send":
                        if counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token"] == "custom":
                            await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Success!*\n\nDirect members to your portal channel. Once they pay you {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"]} of your tokens they will be invited to your group!', parse_mode="Markdown")
                            if (False):
                                # get decimals of custom token
                                token_contract = goerli.eth.contract(address=counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["contract_address"], abi=erc20_abi)
                                decimals = token_contract.functions.decimals().call()
                                print(decimals)
                                args = [10**18, counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["contract_address"], int(counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"])*10**decimals, 10**10,(await context.bot.get_chat(link_id_to_data[
                                counter_to_data[
                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ]["link_id"]
                                ]["main_chat_id"])).title, bytes(12)]
                                print(args)
                                data = unlock.encodeABI(fn_name='createLock', args=args)
                                transaction = {
                            'to': unlock_address,  # Contract address
                            'value': 0,  # Ether value (if sending Ether)
                            'data': data,  # Encoded function call data
                            'nonce': goerli.eth.get_transaction_count(account_address),  # Sender's address
                            'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
                            'gas': estimateGas('createLock', args)*2, 
                            'gasPrice': goerli.eth.gas_price
                            }
                                account = goerli.eth.account.from_key(private_key)
                                signed_transaction = account.sign_transaction(transaction)
                            
                        else: 
                            await update.message.reply_text(f'🔰 *Xclusiv Robot V1.0*\n\n*Success!*\n\nDirect members to your portal channel. Once they pay you {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"]} ${counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token"]} we will add them to your group!', parse_mode="Markdown")
                            if (False):
                                args = [10**18, "0x0cf57e12b489dDC02a5d24a81eE359844A398917", int(counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_amount"])*10**18, 10000, (await context.bot.get_chat(link_id_to_data[
                                counter_to_data[
                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ]["link_id"]
                                ]["main_chat_id"])).title, bytes(12)]
                                data = unlock.encodeABI(fn_name='createLock', args=args)
                        
                                transaction = {
                            'to': unlock_address,  # Contract address
                            'value': 0,  # Ether value (if sending Ether)
                            'data': data,  # Encoded function call data
                            'nonce': goerli.eth.get_transaction_count(account_address),  # Sender's address
                            'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
                            'gas': estimateGas('createLock', args)*2, 
                            'gasPrice': goerli.eth.gas_price
                            }
                                account = goerli.eth.account.from_key(private_key)
                                signed_transaction = account.sign_transaction(transaction)
                        if (False):
                            try:
                                tx_hash = goerli.eth.send_raw_transaction(signed_transaction.rawTransaction)
                                print(f"Transaction sent with hash: {tx_hash.hex()}")
                                receipt = goerli.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # Adjust the timeout as needed
                                if receipt and receipt['status'] == 1:
                                    # Transaction was successful
                                    print(f"Transaction confirmed in block {receipt['blockNumber']}")
                                    event_name = 'NewLock'  # Replace with the event name
                                    argus = None
                                    try:
                                        events = unlock.events[event_name]().process_receipt(receipt)
                                        print(f"Emitted {event_name} events:")
                                        print(events[0]['args'])
                                        argus = events[0]['args']
                                    except Exception as e: 
                                        pass
                                    print(argus['newLockAddress'])
                                    lock_contract_address = argus['newLockAddress']
                                    # map portal id to lock contract address
                                    portal_id_to_data[
                    
                                            link_id_to_data[
                                                counter_to_data[
                                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                                ]["link_id"]
                                            ]["portal_chat_id"]
                                    
                                    ]["lock_contract"] = lock_contract_address
                                    print("Lock contract address linked!")
                                    # if needed, map portal id to receiver address
                            except Exception as e:
                                print(f"Error sending transaction: {e}")
                            if (
                                    counter_to_data[
                                        group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ]["token_action"]
                                    == "send"
                                ):
                                    # if given address is an ens name, fetch raw eth address
                                if (counter_to_data[
                                        group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ][
                                        "receiver_address"
                                    ].endswith(".eth")):
                                        counter_to_data[
                                        group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ][
                                        "receiver_address"
                                    ] = ens.address(counter_to_data[
                                        group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ][
                                        "receiver_address"
                                    ])
                                        print(f'Updated eth address to {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["receiver_address"]}')

                                        portal_id_to_data[
                                    
                                            link_id_to_data[
                                                counter_to_data[
                                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                                ]["link_id"]
                                            ]["portal_chat_id"]
                                        
                                    ]["receiver_address"] = counter_to_data[
                                        group_id_to_data[str(update.message.chat.id)]["counter"]
                                    ][
                                        "receiver_address"
                                    ]
                            ## add receiver wallet address as lock admin 
                            lock = goerli.eth.contract(address=lock_contract_address, abi=lock_abi)
                            data = lock.encodeABI(fn_name='addLockManager', args=[counter_to_data[
                                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                                ]["receiver_address"] ])
                            transaction = {
                            'to': lock_contract_address,  # Contract address
                            'value': 0,  # Ether value (if sending Ether)
                            'data': data,  # Encoded function call data
                            'nonce': goerli.eth.get_transaction_count(account_address),  # Sender's address
                            'chainId': 5,  # Chain ID (e.g., 1 for Ethereum Mainnet)
                            'gas': estimateGas('createLock', args), 
                            'gasPrice': goerli.eth.gas_price
                            }      
                            signed_transaction = account.sign_transaction(transaction)
                            tx_hash = goerli.eth.send_raw_transaction(signed_transaction.rawTransaction)
                            print(f"Transaction sent with hash: {tx_hash.hex()}")
                            receipt = goerli.eth.wait_for_transaction_receipt(tx_hash, timeout=120)  # Adjust the timeout as needed
                            if receipt and receipt['status'] == 1:
                                    # Transaction was successful
                                print(f"AddLockManager confirmed in block {receipt['blockNumber']}")
                            else:
                                print("Transaction failed or not confirmed.")
                                

                            
                                
                # map portal id to main chat id
                portal_id_to_data[
                
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                
                ]["main_chat_id"] = str(
                    link_id_to_data[
                        counter_to_data[
                            group_id_to_data[str(update.message.chat.id)]["counter"]
                        ]["link_id"]
                    ]["main_chat_id"]  
                )
                # map portal id to rest of data

                # map portal id to token action
                portal_id_to_data[
                    
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["token_action"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "token_action"
                ]
                # if needed, map portal id to receiver address
                if (
                    counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_action"]
                    == "send"
                ):
                    # if given address is an ens name, fetch raw eth address
                    if (counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ][
                        "receiver_address"
                    ].endswith(".eth")):
                        counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ][
                        "receiver_address"
                    ] = ens.address(counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ][
                        "receiver_address"
                    ])
                        print(f'Updated eth address to {counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["receiver_address"]}')

                    portal_id_to_data[
                    
                            link_id_to_data[
                                counter_to_data[
                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                ]["link_id"]
                            ]["portal_chat_id"]
                        
                    ]["receiver_address"] = counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ][
                        "receiver_address"
                    ]

    

                # map portal id to contract address or token
                if counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_action"] == "send":
                    portal_id_to_data[
                
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["token"] = counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token"]
                    if counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token"] == "custom": 
                        portal_id_to_data[
                    
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["contract_address"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "contract_address"
                ]
                        
                else:
                    
                    portal_id_to_data[
                    
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["contract_address"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "contract_address"
                ]

                # map portal id to token type

                portal_id_to_data[
                    
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["token_type"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "token_type"
                ]

                # map portal id -> token amount

                if (
                    counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["token_type"]
                    == "erc20"
                ):
                    portal_id_to_data[
                        
                            link_id_to_data[
                                counter_to_data[
                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                ]["link_id"]
                            ]["portal_chat_id"]
                        
                    ]["token_amount"] = counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ][
                        "token_amount"
                    ]
                else:
                    portal_id_to_data[
                        
                            link_id_to_data[
                                counter_to_data[
                                    group_id_to_data[str(update.message.chat.id)]["counter"]
                                ]["link_id"]
                            ]["portal_chat_id"]
                        
                    ]["token_amount"] = 1

                # map portal id to link id
                portal_id_to_data[
                    
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["link_id"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "link_id"
                ]

                # map portal id to network 

                portal_id_to_data[
            
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["receiving_chain"] = counter_to_data[
                    group_id_to_data[str(update.message.chat.id)]["counter"]
                ][
                    "receiving_chain"
                ]

                # send message in portal channel  contract address

                inline_keyboard = [[InlineKeyboardButton(text="Complete Access Criteria", url=f't.me/xclusivrobot?start={link_id_to_data[counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["link_id"]]["portal_chat_id"]}')]]

                main_chat = await context.bot.get_chat(portal_id_to_data[
            
                        link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"]
                    
                ]["main_chat_id"])

                await context.bot.send_message(chat_id=link_id_to_data[
                            counter_to_data[
                                group_id_to_data[str(update.message.chat.id)]["counter"]
                            ]["link_id"]
                        ]["portal_chat_id"], text=f"""{main_chat.title} is being protected by @XclusivRobot\n\nTo get access to the group, please complete the owner's access criteria""", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard))


                
                    
            else:
                link_id_to_data[
                    counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["link_id"]
                ]["portal_chat_id"] = update.message.chat_shared.chat_id
                print("Portal linked")
        if group_id_to_data[str(update.message.chat.id)]:

            '''if (
                group_id_to_data[str(update.message.chat.id)]["setup_step"]
                == "token_action"
            ):
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Verify Token Holdings", callback_data="verify"
                        ),
                        InlineKeyboardButton("Stake Token Holdings", callback_data="stake"),
                    ],
                    [
                        InlineKeyboardButton(
                            "Send Token Holdings to Your Wallet", callback_data="send"
                        )
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "Please enter the action you will require members to perform to gain access to the chat group:",
                    reply_markup=reply_markup,
                )

            """elif (
                group_id_to_data[str(update.message.chat.id)]["setup_step"] == "token_type"
            ):
                keyboard = [
                    [
                        InlineKeyboardButton("NFT", callback_data="nft"),
                        InlineKeyboardButton("ERC-20 Token", callback_data="erc20"),
                    ],
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    "Please enter the type of token required to enter the group",
                    reply_markup=reply_markup,
                )'''
            if (
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ]
                == "link_portal"
            ):
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "link_mainchat"
                params = KeyboardButtonRequestChat(
                    counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["link_id"],
                    False,
                    user_administrator_rights=ChatAdministratorRights(
                        False, True, True, True, True, True, True, True, True, True
                    ),
                    bot_administrator_rights=ChatAdministratorRights(
                        False,
                        can_manage_chat=False,
                        can_delete_messages=False,
                        can_manage_video_chats=False,
                        can_restrict_members=True,
                        can_promote_members=False,
                        can_change_info=False,
                        can_invite_users=True,
                        can_post_messages=True,
                    ),
                )
                keyboard = [[KeyboardButton("➡️ Select a group", request_chat=params)]]
                reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard = True, is_persistent=True,one_time_keyboard = True, input_field_placeholder ="Select your chat group")
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await update.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nClick below and select the group you want to attach your portal to 🔐🔐 \n\n_(Xclusiv will be automatically added as an admin)_",
                    reply_markup=reply_markup, parse_mode="Markdown"
                )
            elif (
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ]
                == "receiver_address"
            ):  
                if is_valid_wallet_address(update.message.text):
                    await context.bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    message_id=counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["latest_bot_message"].id,
                    text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nReceiver address is {update.message.text}", parse_mode="Markdown"
                )
                
                
                    # await query.edit_message_text(text=f"Receiver contract_address is f{update.message.text}")
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "receiver_address"
                ] = update.message.text

                    print(update.message.text)
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_type"] = "erc20"
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["setup_step"] = "token"
                    keyboard = [
                    [
                        InlineKeyboardButton("$USDC", callback_data="USDC"),
                        InlineKeyboardButton("Custom", callback_data="custom")
                    ],
                ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                    ] = await update.message.reply_text(
                    '''🔰 *Xclusiv Robot V1.0* 🔰\n\nChoose the token you wish to receive payment in 
    ''',
                    reply_markup=reply_markup, parse_mode="Markdown"
                )
                
                else: 
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                    # reply_markup=Force
                ] = await update.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\n*Error:*\n\nProvided wallet or ENS address is invalid or not yet created \n\nPlease provide a valid ethereum or ENS address", parse_mode="Markdown")
                    

            elif (
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ]
                == "token_amount"
            ):  

                try:
                    # Attempt to convert the input string to an integer
                    int_value = int(update.message.text)
                    token_amount_valid = True
                except ValueError:
                    # If a ValueError occurs, it's not a valid integer contract_address
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                    # reply_markup=Force
                ] = await update.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\n*Error:*\n\nInvalid amount", parse_mode="Markdown")
                    token_amount_valid = False
                
                if token_amount_valid:
                    
                    if update.message.text == "1":
                            await context.bot.edit_message_text(
                            chat_id=update.message.chat.id,
                            message_id=counter_to_data[
                            group_id_to_data[str(update.message.chat.id)]["counter"]
                        ]["latest_bot_message"].id,
                            text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\n1 token required", parse_mode="Markdown"
                )
                    elif update.message.text != "1":
                        await context.bot.edit_message_text(
                        chat_id=update.message.chat.id,
                        message_id=counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                        ]["latest_bot_message"].id,
                        text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\n{update.message.text} tokens required", parse_mode="Markdown"
                )
            
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "token_amount"
                ] = update.message.text
                    print(update.message.text)
                    if counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_action"] == "send":
                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["setup_step"] = "receiving_chain"
                        keyboard = [
                            [InlineKeyboardButton("Goerli", callback_data="Goerli")],
                    [   InlineKeyboardButton("Arbitrum", callback_data="Arbitrum"),
                        InlineKeyboardButton("Neon EVM", callback_data="Neon EVM") , 
                        InlineKeyboardButton("Scroll", callback_data="Scroll"), 
                    ],
                    [
                        InlineKeyboardButton("Polygon ZkEVM", callback_data="Polygon ZkEVM"),
                        InlineKeyboardButton("Base", callback_data="Base"),
                        InlineKeyboardButton("Linea", callback_data="Linea")
                    ],
                    [
                        InlineKeyboardButton("Celo", callback_data="Celo"),
                        InlineKeyboardButton("Mantle", callback_data="Mantle"),
                        InlineKeyboardButton("Gnosis", callback_data="Gnosis")
                    ]
                    
                ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await update.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nChoose Network",
                        reply_markup=reply_markup, parse_mode="Markdown"
                )
                    else:
                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                    ] = "contract_address"
                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                    ] = await update.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter contract address", parse_mode="Markdown"
                )
                    
            elif (
                counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ]
                == "contract_address"
            ):  
                
                if (is_valid_address(update.message.text)):
                    await context.bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    message_id=counter_to_data[
                        group_id_to_data[str(update.message.chat.id)]["counter"]
                    ]["latest_bot_message"].id,
                    text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nContract address is {update.message.text}", parse_mode="Markdown"
                )
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "contract_address"
                ] = update.message.text
                    print(update.message.text)

                    if (counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["token_type"] == "custom"):
                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["setup_step"] = "token_amount"
                        counter_to_data[
                            group_id_to_data[str(update.message.chat.id)]["counter"]
                        ]["latest_bot_message"] =await update.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter token amount", parse_mode="Markdown")

                    else:
                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]]["setup_step"] = "receiving_chain"
                        keyboard = [
                            [InlineKeyboardButton("Goerli", callback_data="Goerli")],
                    [
                        InlineKeyboardButton("Arbitrum", callback_data="Arbitrum"),
                        InlineKeyboardButton("Polygon ZkEVM", callback_data="Polygon ZkEVM"),
                        InlineKeyboardButton("Neon EVM", callback_data="Neon EVM")
                    ],
                    [
                        InlineKeyboardButton("Base", callback_data="Base"),
                        InlineKeyboardButton("Scroll", callback_data="Scroll"),
                        InlineKeyboardButton("Linea", callback_data="Linea")
                    ],
                    [
                        InlineKeyboardButton("Celo", callback_data="Celo"),
                        InlineKeyboardButton("Mantle", callback_data="Mantle"),
                        InlineKeyboardButton("Gnosis", callback_data="Gnosis")
                    ]
                ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await update.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nChoose Network",
                        reply_markup=reply_markup, parse_mode="Markdown"
                )
                else: 
                    counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await update.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nError:\n\nAddress is invalid. Provide a valid ethereum contract address", parse_mode="Markdown")
                


                '''counter_to_data[group_id_to_data[str(update.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "verify_data"'''

            


    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        latest_context = context
        query = update.callback_query

        await query.answer()

        if query.data == "verification button pressed":
            print("Verification buttton pressed!")
            return

        if query.data == "verify":
            await query.edit_message_text(text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nMembers will be required to verify token holdings", parse_mode="Markdown")
        elif query.data == "stake":
            await query.edit_message_text(text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nMembers will be required to stake tokens in exchange for group access", parse_mode="Markdown")
        elif query.data == "send":
            await query.edit_message_text(
                text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nMembers will pay for group access", parse_mode="Markdown"
            )
        elif query.data == "nft":
            await query.edit_message_text(text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nToken type is NFT",parse_mode="Markdown")
        elif query.data == "erc20":
            await query.edit_message_text(text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nToken type is ERC-20", parse_mode="Markdown")
        elif query.data == "correct":
            await query.edit_message_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nData is correct, moving on to last step", parse_mode="Markdown")
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "setup_step"
            ] = "link_portal"
            params = KeyboardButtonRequestChat(
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "link_id"
                ],
                chat_is_channel=True,
                user_administrator_rights=ChatAdministratorRights(
                    False, True, True, True, True, True, True, True, True, True
                ),
                bot_administrator_rights=ChatAdministratorRights(
                    False,
                    can_manage_chat=True,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=True,
                    can_promote_members=False,
                    can_change_info=False,
                    can_invite_users=True,
                    can_post_messages=True,
                ),
            )
            keyboard = [[KeyboardButton("➡️Select a channel", request_chat=params)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard = True, is_persistent=True, one_time_keyboard = True, input_field_placeholder = "Select portal channel")
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "latest_bot_message"
            ] = await query.message.reply_text(
                "🔰 *Xclusiv Robot V1.0* 🔰\n\nSelect a channel where your portal will be created 🌀🌀 \n\n_(Xclusiv will be automatically added as an admin)_",
                reply_markup=reply_markup, parse_mode="Markdown"
                
            )
        elif query.data == "incorrect":
            await query.edit_message_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nData is incorrect, run /setup to restart", parse_mode="Markdown")

        # print(query.message.chat.id)contract_address

        if counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["setup_step"] == "receiving_chain":
            await query.edit_message_text(text=f"🔰 *Xclusiv Robot V1.0* 🔰\n\nNetwork is {query.data}", parse_mode="Markdown")
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"] = query.data
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["setup_step"] = "verify_data"
            if (
                    counter_to_data[
                        group_id_to_data[str(query.message.chat.id)]["counter"]
                    ]["token_type"]
                    == "custom"
                ):
                keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will pay {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token_amount"]} tokens at contract address {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["contract_address"]} to {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiver_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} in exchange for group access""",  reply_markup=reply_markup, parse_mode="Markdown")

            elif (
                    counter_to_data[
                        group_id_to_data[str(query.message.chat.id)]["counter"]
                    ]["token_action"]
                    == "send"
                ):
                        
                        keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will pay {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token_amount"]} ${counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token"]} to {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiver_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} in exchange for group access""",  reply_markup=reply_markup, parse_mode="Markdown")
                ######################
            elif (
                    counter_to_data[
                        group_id_to_data[str(query.message.chat.id)]["counter"]
                    ]["token_action"]
                    == "stake"
                ):
                    if (
                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["token_type"]
                        == "nft"
                    ):
                        # await update.message.reply_text
                        keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will be required to stake one NFT at contract address {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["contract_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} to gain access to the telegram group""",
                            reply_markup=reply_markup, parse_mode="Markdown"
                        )

                    elif (
                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["token_type"]
                        == "erc20"
                    ):
                        keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will be required to stake {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token_amount"]} tokens at contract address {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["contract_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} to gain access to the group""",
                            reply_markup=reply_markup, parse_mode="Markdown"
                        )
                ######################
            elif (
                    counter_to_data[
                        group_id_to_data[str(query.message.chat.id)]["counter"]
                    ]["token_action"]
                    == "verify"
                ):
                    if (
                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["token_type"]
                        == "nft"
                    ):
                        # await update.message.reply_text
                        keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will be required to verify ownership of at least one NFT at contract address {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["contract_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} to gain access to the group """,
                            reply_markup=reply_markup, parse_mode="Markdown"
                        )

                    elif (
                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["token_type"]
                        == "erc20"
                    ):
                        keyboard = [
                            [
                                InlineKeyboardButton("Yes", callback_data="correct"),
                                InlineKeyboardButton("No", callback_data="incorrect"),
                            ],
                        ]

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text(
                            f"""🔰 *Xclusiv Robot V1.0* 🔰\n\nIs this correct?\n\nMembers will be required to verify ownership of at least {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token_amount"]} tokens at contract address {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["contract_address"]} on {counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["receiving_chain"]} to gain access to the group""",
                            reply_markup=reply_markup, parse_mode="Markdown"
                        )

        if counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["setup_step"] == "token":
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["token"] = query.data
            if (query.data != "custom"): 
                await query.edit_message_text(f"🔰 *Xclusiv Robot V1.0* 🔰\n\nYou will receive payment in ${query.data}", parse_mode="Markdown")
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["setup_step"] = "token_amount"
                counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] =await query.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter token amount", parse_mode="Markdown")
            else: 
                await query.edit_message_text(f"🔰 *Xclusiv Robot V1.0* 🔰\n\nCustom token selected", parse_mode="Markdown")
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]]["setup_step"] = "contract_address"
                counter_to_data[
                            group_id_to_data[str(query.message.chat.id)]["counter"]
                        ]["latest_bot_message"] = await query.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter your token contract address", parse_mode="Markdown")


        if (
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "setup_step"
            ]
            == "token_action"
        ):

            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "token_action"
            ] = query.data
            if query.data == "send":

                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "receiver_address"
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await query.message.reply_text(
                    """🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter a wallet address\n\nThis is the address which will collect payments from users\n\nENS is supported               
                    """, parse_mode="Markdown"
                )

            else:

                    counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "token_type"
                    keyboard = [
                    [
                        InlineKeyboardButton("NFT", callback_data="nft"),
                        InlineKeyboardButton("ERC-20", callback_data="erc20"),
                    ],
                ]

                    reply_markup = InlineKeyboardMarkup(keyboard)

                    counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await query.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nChoose token type", parse_mode="Markdown",
                    reply_markup=reply_markup)

        elif (
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "setup_step"
            ]
            == "token_type"
        ):
            counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                "token_type"
            ] = query.data

            if query.data == "erc20":
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "token_amount"
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await query.message.reply_text(
                    "🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter token amount",  parse_mode="Markdown"
                )# You will receive

            elif query.data == "nft":
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "contract_address"
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await query.message.reply_text("🔰 *Xclusiv Robot V1.0* 🔰\n\nEnter contract address",parse_mode="Markdown" )

        
        '''counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "setup_step"
                ] = "receiver_address"
                counter_to_data[group_id_to_data[str(query.message.chat.id)]["counter"]][
                    "latest_bot_message"
                ] = await query.message.reply_text(
                    "Please enter your wallet address. This is the address to which users will send their tokens in exchange for group access."
                )'''


    app = (
        ApplicationBuilder().token("6419841389:AAHxCI5SbkHDm_v1L-_WnBKulIxRW6D4X-U").build()
    )


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(None, message))
    # app.add_handler(CommandHandler("testbutton", buttonMessage))

    app.run_polling()

XclusivTgBot()