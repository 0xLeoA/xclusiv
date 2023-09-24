import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import { useEffect, useState } from 'react'
import { ConnectButton } from '@rainbow-me/rainbowkit';
import { useAccount, useConnect, useDisconnect, useNetwork, useSignMessage } from 'wagmi'
import { ERC20ABI, chainidtodata, xclusivabi, nftabi } from "../constants";
import { readContract, watchContractEvent, getAccount, prepareWriteContract, writeContract, waitForTransaction, useContractWrite } from '@wagmi/core';
import MintButton from '@/components/mintbutton'
import { FaSpinner } from 'react-icons/fa'
import Spinner from '@/components/spinner'
import axios from 'axios';
import { ethers } from 'ethers';
import io from 'socket.io-client';

function MyButton(props) {
    const [loading, setLoading] = useState(false)
    const [buttonText, setButtonText] = useState("")
    const provider = new ethers.providers.Web3Provider(window.ethereum);


    async function getApproved() {
        let data = await readContract({
            address: props.ca,
            abi: nftabi,
            functionName: 'getApproved',
            args: [props.tokenid]
        })
        if (data == props.xclusiv) {
            setButtonText("Click To Stake")
        } else {
            setButtonText("Click To Approve")
        }
    }

    useState(() => { getApproved() }, [])
    console.log(props.ca + "given ca")

    return (
        <button disabled={buttonText == "Confirm Tx" || buttonText == "Awaiting Tx Hash"} className={styles.nftbutton} onClick={async () => {
            setButtonText("Confirm Tx")
            if (buttonText == "Click To Approve") {
                try {
                    const config = await prepareWriteContract({
                        address: props.ca,
                        abi: nftabi,
                        functionName: 'approve',
                        args: [props.xclusiv, props.tokenid]
                    })
                    const { hash } = await writeContract(config)
                    setLoading(true)
                    setButtonText("Awaiting Tx Hash")
                    const data = await waitForTransaction({
                        hash,
                    })
                    setLoading(false)
                    setButtonText("Click To Stake")
                } catch (e) {
                    setButtonText("Click To Approve")
                    setLoading(false)
                }
            } else {
                try {
                    const config = await prepareWriteContract({
                        address: props.xclusiv,
                        abi: xclusivabi,
                        functionName: 'stake',
                        args: [true, props.tokenid, props.ca],
                    })
                    const { hash } = await writeContract(config)
                    setLoading(true)
                    setButtonText("Awaiting Tx Hash")
                    const data = await waitForTransaction({
                        hash,
                    })
                    setButtonText("Staked!")
                    setLoading(false)
                    props.onCompletion()
                } catch (e) {
                    console.log(e)
                    setButtonText("Click To Stake")
                    setLoading(false)
                }
            }
        }}>{loading ? <><h className={styles.nftbuttontext}>Awaiting Tx Hash</h><span className={styles.buttontextspannft}><FaSpinner className="spin" /></span></> : <h className={styles.nftbuttontext}>{buttonText}</h>}</button>
    );
}

export default function NFTS(props) {
    console.log(props.tokenids)


    return (
        <div className={styles.nftscontainer}>{props.imgs.map((imageUrl, index) => (
            <div className={styles.flexcolumn}>
                <div className={styles.nftcontainer}>
                    <div className={styles.nftnametextdiv}><h className={styles.nftnametext}>{props.name} #{props.tokenids[index]}</h></div>
                    <div className={styles.nftimagecontainer}><img className={styles.imgsize} key={index} src={imageUrl} alt={`Image ${index}`} /></div>
                    <div className={styles.nftborderline} />
                    <MyButton onCompletion={props.onCompletion} ca={props.ca} xclusiv={props.xclusiv} tokenid={props.tokenids[index]}></MyButton>
                </div>
            </div>
        ))}</div>)
}