import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import { useEffect, useState } from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount, useConnect, useDisconnect, useNetwork, useSignMessage } from 'wagmi'
import { ERC20ABI, chainidtodata, xclusivabi, nftabi, lockabi } from "../constants";
import { readContract, watchContractEvent, getAccount, prepareWriteContract, writeContract, waitForTransaction, useContractWrite } from '@wagmi/core';
import MintButton from '@/components/mintbutton'
import { FaSpinner } from 'react-icons/fa'
import Spinner from '@/components/spinner'
import axios from 'axios';
import { ethers } from 'ethers';
import io from 'socket.io-client';
import generateInviteLink from './api/generateInviteLink'
import NFTS from './img'


function parseQueryString(queryString) {
    const params = {};
    // Remove the leading "?" if present
    queryString = queryString.replace(/^\?/, '');

    // Split the query string into key-value pairs
    const keyValuePairs = queryString.split('&');

    for (const pair of keyValuePairs) {
        const [key, value] = pair.split('=');

        // Decode URI components and store in the params object
        params[decodeURIComponent(key)] = decodeURIComponent(value || '');
    }

    return params;
}


export default function Home() {

    const params = parseQueryString(window.location.search)

    const { address, isConnecting, isDisconnected, isConnected } = useAccount()
    const { chain, chains } = useNetwork()
    const account = getAccount()
    const [approvedTokenAmount, setApprovedTokenAmount] = useState()
    const [tokenBalance, setTokenBalance] = useState()
    const [approveButtonText, setApproveButtonText] = useState("Approve " + params["token"] + " for transfer")
    const [mintButtonText, setMintButtonText] = useState("Mint Free $" + params['token'])
    const [sendCompletePaymentButtonText, setSendCompletePaymentButtonText] = useState("Complete Payment")
    const [verificationComplete, setVerificationComplete] = useState(false)
    const [stakeButtonText, setStakeButtonText] = useState("Stake Tokens")
    const [inviteLink, setInviteLink] = useState("")
    const [NFTVerifStarted, setNFTVerifStarted] = useState(false)
    const [ownedNFTs, setOwnedNFTs] = useState([])
    const [collectionName, setCollectionName] = useState()


    const supportedChains = [5, 1442, 59140, 245022926, 10200, 44787, 5001, 421613, 84531, 534351, 51]
    let provider = new ethers.providers.Web3Provider(window.ethereum);


    useEffect(() => {
        if (isConnected) {
        }
        if (params['action'] !== "send") {
            setApproveButtonText("Approve tokens for transfer")
        }
    }, [])



    async function setTgLink() {
        let invite = await generateInviteLink(params['mainchatid'], "6419841389:AAHxCI5SbkHDm_v1L-_WnBKulIxRW6D4X-U")
        setInviteLink(invite)
    }

    useEffect(() => {
        if (verificationComplete == true) {
            setTgLink()
        }
    }, [verificationComplete])

    async function getTokenAllowance() {
        if (params['lock']) {
            setApproveButtonText('Approve tokens for transfer')
        }
        if (params['action'] == "send" && params['token'] != "custom") {
            if (params['lock']) {
                const data = await readContract({
                    address: chainidtodata[chain.id][params['token']],
                    abi: ERC20ABI,
                    functionName: 'allowance',
                    args: [address, params['lock']]
                })
                await setApprovedTokenAmount(Number(data["_hex"]) / 10 ** 18)
            } else {
                const data = await readContract({
                    address: chainidtodata[chain.id][params['token']],
                    abi: ERC20ABI,
                    functionName: 'allowance',
                    args: [address, chainidtodata[chain.id]['contract']]
                })
                await setApprovedTokenAmount(Number(data["_hex"]) / 10 ** 18)
            }
        } else if (params['lock'] && params['token'] == "custom") {
            const data = await readContract({
                address: params['contract'],
                abi: ERC20ABI,
                functionName: 'allowance',
                args: [address, params['lock']]
            })
            await setApprovedTokenAmount(Number(data["_hex"]) / 10 ** 18)
        }
        if (params['action'] == "stake") {
            if (params['type'] == 'erc20') {
                if (chain.id == params['chainid']) {
                    const data = await readContract({
                        address: params['contract'],
                        abi: ERC20ABI,
                        functionName: 'allowance',
                        args: [address, chainidtodata[chain.id]['contract']]
                    })
                    await setApprovedTokenAmount(Number(data["_hex"]) / 10 ** 18)
                }
            }
        }
    }

    const [unlockNFTBalance, setUnlockNFTBalance] = useState(0)
    async function getTokenBalance() {
        if (params['lock']) {
            const data = await readContract({
                address: params['lock'],
                abi: nftabi,
                functionName: 'balanceOf',
                args: [address]
            })
            await setUnlockNFTBalance(Number(data["_hex"]))
        }
        if (params['token'] == "custom") {

            if (chain.id == params['chainid']) {
                const data = await readContract({
                    address: params['contract'],
                    abi: ERC20ABI,
                    functionName: 'balanceOf',
                    args: [address]
                })

                await setTokenBalance(Number(data["_hex"]) / 10 ** 18)
            }
        } else if (params['action'] == "send") {
            const data = await readContract({
                address: chainidtodata[chain.id][params['token']],
                abi: ERC20ABI,
                functionName: 'balanceOf',
                args: [address]
            })

            await setTokenBalance(Number(data["_hex"]) / 10 ** 18)
        } else if (params['chainid'] == chain.id) {
            if (params['type'] == "erc20") {
                const data = await readContract({
                    address: params['contract'],
                    abi: ERC20ABI,
                    functionName: 'balanceOf',
                    args: [address]
                })
                await setTokenBalance(Number(data["_hex"]) / 10 ** 18)
            } else {
                if (chain.id == params['chainid']) {
                    const data = await readContract({
                        address: params['contract'],
                        abi: nftabi,
                        functionName: 'balanceOf',
                        args: [address]
                    })
                    await setTokenBalance(Number(data["_hex"]))
                }
            }
        }
    }

    async function getCollectionName() {
        if (params["action"] == "stake" && params["type"] == "nft") {
            try {
                let data = await readContract({
                    address: params['contract'],
                    abi: nftabi,
                    functionName: 'name',
                    args: []
                })
                console.log(data)
                setCollectionName(data)
            } catch (error) {

            }
        }
    }

    getCollectionName()
    const [ownedNFTIds, setOwnedNFTIds] = useState([])
    const ownedNFTImageURLs = [];
    // get a list of all the token ids of given nft connected address owns
    async function getNFTsOwnedByAddress() {

        let index = 0
        let tokenId
        while (true) {
            try {
                tokenId = await readContract({
                    address: params['contract'],
                    abi: nftabi,
                    functionName: 'tokenOfOwnerByIndex',
                    args: [address, index]
                })
                ownedNFTIds.push(parseInt(tokenId["_hex"], 16));
                index++;
            } catch (error) {
                // If an error is thrown, it means we've reached the end of the owner's NFTs
                break
            }
        }
    }

    const [nftImages, setNFTImages] = useState([])
    const [nftImageCachingComplete, setNFTImageCachingComplete] = useState(false)
    async function getNFTIMGURLS(tokenIds) {
        for (let i = 0; ownedNFTIds.length; i++) {
            try {
                let data = await readContract({
                    address: params['contract'],
                    abi: nftabi,
                    functionName: 'getTokenIdToImageUrl',
                    args: [ownedNFTIds[i]]
                })
                nftImages.push(data)
            } catch (e) {
                return nftImages
            }
        }
        return nftImages
    }

    useEffect(() => {
        if (isConnected) {
            if (supportedChains.includes(chain.id)) {
                getTokenBalance()
                getTokenAllowance()
            }
        }
    }, [chain, address])

    async function getCrosschainTransferValue() {
        const value = await readContract({
            address: chainidtodata[chain.id]['contract'],
            abi: xclusivabi,
            functionName: 'estimateFees',
            args: [chainidtodata[params['chainid']]["lz_chainid"], chainidtodata[params['chainid']]['contract'], BigInt(params["amount"] * 10 ** 18), params["receiver_address"]]
        })
        console.log(parseInt(value['_hex'], 16) / 10 ** 18 + " eth amount for crosschain message")
        return parseInt(value['_hex'], 16)
    }

    if (params['lock']) {
        console.log(true)
    }

    async function xyz() {
        return (await prepareWriteContract({
            address: params['lock'],
            abi: lockabi,
            functionName: 'purchase',
            args: [[(BigInt(params['amount']) * BigInt(10 ** 18))], [address], [address], [address], ["0x0"]],
            value: 0
        }))
    }


    return (<div className={styles.container}>
        {verificationComplete ?
            <div className={styles.verifcompletediv} >
                <div className={styles.topheader}>
                    <p />
                    <h className={styles.xclusivtextheader}>Xclusiv</h>
                    <p />
                </div>
                <div className={styles.verifcompletepadding}>
                    <div className={styles.flexcolumn}>
                        <a href={inviteLink} className={styles.verifcomplete}>Access criteria complete, click this link to join {params['chatname']}</a>

                    </div>
                </div>
            </div> :
            <>

                <div>
                    <div className={styles.topheader}>
                        <p />
                        <h className={styles.xclusivtextheader}>Xclusiv</h>
                        <p />
                    </div>


                    <div className={styles.connectbuttondiv}>
                        <p></p>
                        <ConnectButton />
                    </div>
                    <div className={styles.actiondescriptionheader}>
                        {params['secret'] ? <></> : params['token'] == "custom" ? <h className={styles.maintexttheme}>Pay {params["amount"]} tokens at contract {params['contract']} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h>
                            : params["action"] == "send" ? <h className={styles.maintexttheme}>Pay {params["amount"]} ${params["token"]} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h> :
                                params["action"] == "verify" ? params["type"] == "nft" ? <h className={styles.maintexttheme}>Verify ownership of at least one NFT at contract address {params["contract"]} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h> :
                                    <h className={styles.maintexttheme}>Verify ownership of at least {params["amount"]} tokens at contract address {params["contract"]} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h>
                                    : params["type"] == "nft" ? <h className={styles.maintexttheme}>Stake one NFT at contract address {params["contract"]} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h> : <h className={styles.maintexttheme}>Stake {params["amount"]} tokens at contract address {params["contract"]} for access to <span className={styles.premiumnamecolor}>{params['chatname']}</span></h>}
                    </div>
                    <div className={styles.completepaymentbuttondiv}>
                        {isConnected ?
                            params["action"] == "send" ?
                                params['token'] == "custom" ?
                                    chain.id == params['chainid'] ?
                                        tokenBalance >= params['amount'] ?


                                            <div className={styles.flexcolumn}><div className={styles.balancediv}><h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h></div><div><button disabled={sendCompletePaymentButtonText !== "Complete Payment"} className={styles.sendpaymentbutton} onClick={async () => {
                                                const config = await prepareWriteContract({
                                                    address: params['contract'],
                                                    abi: ERC20ABI,
                                                    functionName: 'transfer',
                                                    args: [params["receiver_address"], BigInt(params["amount"] * 10 ** 18)]
                                                })
                                                setSendCompletePaymentButtonText("Confirm Transaction")
                                                try {
                                                    const { hash } = await writeContract(config)
                                                    setSendCompletePaymentButtonText("Awaiting Confirmation")
                                                    const data = await waitForTransaction({
                                                        hash,
                                                    })
                                                    setVerificationComplete(true)
                                                    setSendCompletePaymentButtonText("Complete Payment")
                                                } catch (e) {
                                                    setSendCompletePaymentButtonText("Complete Payment")
                                                    console.log(e)
                                                }
                                            }}>
                                                {sendCompletePaymentButtonText}{sendCompletePaymentButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</button></div></div> :

                                            <div className={styles.flexcolumn}><h className={styles.errortext}>Balance: {tokenBalance}</h><h className={styles.errortext}>Insufficient balance, unable to complete payment</h></div>
                                        : <h className={styles.errortext}>Switch to {chainidtodata[params['chainid']]['name']} to proceed</h>
                                    :
                                    supportedChains.includes(chain.id) ?
                                        tokenBalance >= Number(params["amount"]) ?
                                            chain.id == params['chainid'] ?

                                                <div className={styles.flexcolumn}>
                                                    <div className={styles.balancediv}>{tokenBalance >= params['amount'] ? <h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h> : <h className={styles.errortext}>Balance: {tokenBalance}</h>}</div>
                                                    <div>
                                                        <button disabled={sendCompletePaymentButtonText !== "Complete Payment"} className={styles.sendpaymentbutton} onClick={async () => {
                                                            const config = await prepareWriteContract({
                                                                address: chainidtodata[chain.id][params['token']],
                                                                abi: ERC20ABI,
                                                                functionName: 'transfer',
                                                                args: [params["receiver_address"], BigInt(params["amount"] * 10 ** 18)]
                                                            })
                                                            setSendCompletePaymentButtonText("Confirm Transaction")
                                                            try {
                                                                const { hash } = await writeContract(config)
                                                                setSendCompletePaymentButtonText("Awaiting Confirmation")
                                                                const data = await waitForTransaction({
                                                                    hash,
                                                                })
                                                                setVerificationComplete(true)
                                                                setSendCompletePaymentButtonText("Complete Payment")
                                                            } catch (e) {
                                                                setSendCompletePaymentButtonText("Complete Payment")
                                                                console.log(e)
                                                            }
                                                        }}>
                                                            {sendCompletePaymentButtonText}{sendCompletePaymentButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</button></div></div>

                                                :
                                                approvedTokenAmount >= Number(params["amount"])
                                                    ? <div className={styles.flexcolumn}>
                                                        <div className={styles.balancediv}>{tokenBalance >= params['amount'] ? <h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h> : <h className={styles.errortext}>Balance: {tokenBalance}</h>}</div>
                                                        <div><button disabled={sendCompletePaymentButtonText !== "Complete Payment"} className={styles.sendpaymentbutton} onClick={async () => {
                                                            const config = await prepareWriteContract({
                                                                address: chainidtodata[chain.id]['contract'],
                                                                abi: xclusivabi,
                                                                functionName: 'send',
                                                                args: [BigInt(params["amount"] * 10 ** 18), params["receiver_address"], chainidtodata[params['chainid']]['contract'], chainidtodata[params['chainid']]['lz_chainid']],
                                                                overrides: {
                                                                    'value': BigInt(Math.floor(await getCrosschainTransferValue() * 1.1))
                                                                }
                                                            })
                                                            setSendCompletePaymentButtonText("Confirm Transaction")
                                                            try {
                                                                const { hash } = await writeContract(config)
                                                                setSendCompletePaymentButtonText("Awaiting Confirmation")
                                                                const data = await waitForTransaction({
                                                                    hash,
                                                                })
                                                                setVerificationComplete(true)
                                                                setSendCompletePaymentButtonText("Complete Payment")

                                                            } catch (e) {
                                                                setSendCompletePaymentButtonText("Complete Payment")
                                                                console.log(e)
                                                            }
                                                        }}>
                                                            {sendCompletePaymentButtonText}{sendCompletePaymentButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</button></div></div>
                                                    :
                                                    <div className={styles.flexcolumn}>
                                                        <div className={styles.balancediv}>{tokenBalance >= params['amount'] ? <h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h> : <h className={styles.errortext}>Balance: {tokenBalance}</h>}</div>
                                                        <div>
                                                            <button disabled={approveButtonText !== "Approve " + params["token"] + " for transfer"} className={styles.approvebutton} onClick={async () => {
                                                                const config = await prepareWriteContract({
                                                                    address: chainidtodata[chain.id][params['token']],
                                                                    abi: ERC20ABI,
                                                                    functionName: 'approve',
                                                                    args: [chainidtodata[chain.id]["contract"], BigInt(params["amount"] * 10 ** 18)]
                                                                })
                                                                setApproveButtonText("Confirm Transaction")
                                                                try {
                                                                    const { hash } = await writeContract(config)
                                                                    setApproveButtonText("Awaiting Confirmation")
                                                                    const data = await waitForTransaction({
                                                                        hash,
                                                                    })
                                                                    getTokenAllowance()
                                                                    setApproveButtonText("Approve " + params["token"] + " for transfer")
                                                                } catch (e) {

                                                                    setApproveButtonText("Approve " + params["token"] + " for transfer")
                                                                    console.log(e)
                                                                }
                                                            }}>
                                                                <>{approveButtonText}{approveButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</></button></div></div>
                                            : <div className={styles.flexcolumn}><div className={styles.balancediv}>{tokenBalance >= params['amount'] ? <h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h> : <h className={styles.errortext}>Balance: {tokenBalance}</h>}</div><h className={styles.errortext}>Insufficient Balance, unable to complete payment</h></div>
                                        :
                                        <h className={styles.errortext}>Switch to a supported network to complete payment</h> :
                                chain.id == params["chainid"] ?
                                    params["type"] == "nft" ? params['action'] == "verify" ?
                                        tokenBalance > 0 ?
                                            <div className={styles.flexcolumn}><h className={styles.sufficientbalancetext}>NFTs owned: {tokenBalance}</h><div className={styles.verifybuttondiv}><button onClick={async () => {

                                                try {
                                                    const wallet = provider.getSigner();
                                                    const signature = await wallet.signMessage("Sign this message to prove ownership of the wallet at address " + address + " and all assets held inside said wallet");
                                                    console.log('Signature:', signature);
                                                    setVerificationComplete(true)
                                                } catch (e) {
                                                    console.log(e)
                                                }



                                            }} className={styles.verifybutton}>Sign message to verify</button></div></div>
                                            :
                                            <div className={styles.flexcolumn}>
                                                <h className={styles.errortext}>NFTs owned: {tokenBalance}</h>

                                                <h className={styles.errortext}>Insufficient balance, unable to grant access to telegram group</h>
                                            </div> :

                                        NFTVerifStarted ? tokenBalance == 0 ? <h className={styles.errortext}>You don't hold any of these NFTs, unable to complete staking</h> : nftImageCachingComplete ?

                                            <NFTS onCompletion={() => { setVerificationComplete(true) }} xclusiv={chainidtodata[chain.id]["contract"]} ca={params['contract']} imgs={nftImages} name={collectionName} tokenids={ownedNFTIds} /> : <h className={styles.maintexttheme


                                            }>Fetching NFTs...</h> : <button className={styles.verifybutton} onClick={async () => {
                                                setNFTVerifStarted(true)
                                                await getNFTsOwnedByAddress()
                                                /////////////////////////////////////////////////////
                                                /////////////////////////////////////////////////////
                                                /////////////////////////////////////////////////////
                                                await getNFTIMGURLS(ownedNFTIds)
                                                console.log(nftImages)
                                                setNFTImageCachingComplete(true)
                                            }}>Begin Staking</button> :
                                        tokenBalance >= params['amount'] ? <div className={styles.flexcolumn}><h className={styles.sufficientbalancetext}>Balance: {tokenBalance}</h> {params['action'] == "verify" ? <div className={styles.verifybuttondiv}><button onClick={async () => {
                                            try {
                                                const wallet = provider.getSigner();
                                                const signature = await wallet.signMessage("Sign this message to prove ownership of the wallet at address " + address + " and all assets held inside said wallet");
                                                console.log('Signature:', signature);
                                                setVerificationComplete(true)
                                            } catch (e) {
                                                console.log(e)
                                            }



                                        }} className={styles.verifybutton}>Sign message to verify</button></div> :
                                            <div className={styles.idkwhattocallthis}>
                                                {approvedTokenAmount >= params['amount'] ? <button disabled={stakeButtonText !== "Stake Tokens"} className={styles.approvebutton} onClick={async () => {
                                                    const config = await prepareWriteContract({
                                                        address: chainidtodata[chain.id]['contract'],
                                                        abi: xclusivabi,
                                                        functionName: 'stake',
                                                        args: [false, BigInt(params["amount"] * 10 ** 18), params['contract']]
                                                    })
                                                    setStakeButtonText("Confirm Transaction")
                                                    try {
                                                        const { hash } = await writeContract(config)
                                                        setStakeButtonText("Awaiting Confirmation")
                                                        const data = await waitForTransaction({
                                                            hash,
                                                        })
                                                        setVerificationComplete(true)
                                                        setStakeButtonText("Stake Tokens")
                                                    } catch (e) {

                                                        setStakeButtonText("Stake Tokens")
                                                        console.log(e)
                                                    }
                                                }}>
                                                    <>{stakeButtonText}{stakeButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</></button> :
                                                    <button disabled={approveButtonText !== "Approve tokens for transfer"} className={styles.approvebutton} onClick={async () => {
                                                        const config = await prepareWriteContract({
                                                            address: params['contract'],
                                                            abi: ERC20ABI,
                                                            functionName: 'approve',
                                                            args: [chainidtodata[chain.id]["contract"], BigInt(params["amount"] * 10 ** 18)]
                                                        })
                                                        setApproveButtonText("Confirm Transaction")
                                                        try {
                                                            const { hash } = await writeContract(config)
                                                            setApproveButtonText("Awaiting Confirmation")
                                                            const data = await waitForTransaction({
                                                                hash,
                                                            })
                                                            getTokenAllowance()
                                                            setApproveButtonText("Approve tokens for transfer")
                                                        } catch (e) {

                                                            setApproveButtonText("Approve tokens for transfer")
                                                            console.log(e)
                                                        }
                                                    }}>
                                                        <>{approveButtonText}{approveButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <></>}</></button>}</div>}</div> :
                                            <div className={styles.flexcolumn}><h className={styles.errortext}>Balance: {tokenBalance}</h> <h className={styles.errortext}>Insufficient balance, unable to complete verification</h></div>
                                    : <h className={styles.errortext}>Please switch network to {chainidtodata[params["chainid"]]["name"]} to proceed</h> : <></>}
                    </div>
                </div>
                <div>
                    {isConnected ? params["action"] == "send" && params['token'] != "custom" && supportedChains.includes(chain.id) ? <button disabled={mintButtonText !== "Mint Free $" + params['token']} className={styles.mintxcvbutton} onClick={
                        async () => {
                            if (isConnected) {
                                if (supportedChains.includes(chain.id)) {
                                    setMintButtonText("Confirm Transaction")
                                    const config = await prepareWriteContract({
                                        address: chainidtodata[chain.id][params['token']],
                                        abi: ERC20ABI,
                                        functionName: 'mint',
                                        args: [address, BigInt(1000000 * 10 ** 18)]
                                    })
                                    try {
                                        const { hash } = await writeContract(config)
                                        setMintButtonText("Awaiting Confirmation")
                                        const data = await waitForTransaction({
                                            hash,
                                        })
                                        getTokenBalance()
                                        setMintButtonText("Mint Free $" + params['token'])
                                    } catch (e) {
                                        getTokenBalance()
                                        setMintButtonText("Mint Free $" + params['token'])
                                        console.log(e)
                                    }

                                }
                            }

                        }}>
                        <>{mintButtonText} {mintButtonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <h />}</>
                    </button> : <></> : <></>}
                </div>
            </>
        }
    </div >)

}

