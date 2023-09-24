import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import { useEffect, useState } from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount, useConnect, useDisconnect, useNetwork } from 'wagmi'
import { ERC20ABI, chainidtodata } from "../constants";
import { readContract, watchContractEvent, getAccount, prepareWriteContract, writeContract, waitForTransaction, useContractWrite } from '@wagmi/core';
import { FaSpinner } from 'react-icons/fa'

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


export default function MintButton() {
    const { address, isConnecting, isDisconnected, isConnected } = useAccount()
    const supportedChains = [5, 1442, 80001]
    const { chain, chains } = useNetwork()
    const [loading, setLoading] = useState(false);
    const params = parseQueryString(window.location.search)
    const [buttonText, setButtonText] = useState("Mint Free $" + params['token'])

    useEffect(() => { }, [loading])


    return (<button disabled={buttonText !== "Mint Free $" + params['token']} className={styles.mintxcvbutton} onClick={
        async () => {
            if (isConnected) {
                if (supportedChains.includes(chain.id)) {
                    setButtonText("Confirm Transaction")
                    const config = await prepareWriteContract({
                        address: chainidtodata[chain.id][params['token']],
                        abi: ERC20ABI,
                        functionName: 'mint',
                        args: [address, BigInt(1000000 * 10 ** 18)]
                    })
                    try {
                        const { hash } = await writeContract(config)
                        setButtonText("Awaiting Confirmation")
                        const data = await waitForTransaction({
                            hash,
                        })
                        setButtonText("Mint Free $" + params['token'])
                    } catch (e) {

                        setButtonText("Mint Free $" + params['token'])
                        console.log(e)
                    }

                }
            }

        }}>
        <>{buttonText} {buttonText == "Awaiting Confirmation" ? <span className={styles.buttontextspan}><FaSpinner className="spin" /></span> : <h />}</>
    </button>)
}