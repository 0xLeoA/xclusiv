// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ILayerZeroEndpoint {
    // @notice send a LayerZero message to the specified address at a LayerZero endpoint.
    // @param _dstChainId - the destination chain identifier
    // @param _destination - the address on destination chain (in bytes). address length/format may vary by chains
    // @param _payload - a c ustom bytes payload to send to the destination contract
    // @param _refundAddress - if the source transaction is cheaper than the amount of value passed, refund the additional amount to this address
    // @param _zroPaymentAddress - the address of the ZRO token holder who would pay for the transaction
    // @param _adapterParams - parameters for custom functionality. e.g. receive airdropped native gas from the relayer on destination
    function send(uint16 _dstChainId, bytes calldata _destination, bytes calldata _payload, address payable _refundAddress, address _zroPaymentAddress, bytes calldata _adapterParams) external payable;
    function estimateFees(uint16 _dstChainId, address _userApplication, bytes calldata _payload, bool _payInZRO, bytes calldata _adapterParam) external view returns (uint nativeFee, uint zroFee);
}


pragma solidity ^0.8.0;

import "@openzeppelin/contracts/interfaces/IERC721.sol";
import "@openzeppelin/contracts/interfaces/IERC20.sol";


interface IERC20Mintable {
    function mint(address to, uint256 amount) external;
}


interface ILock {
    function purchase(uint256[] memory _values, address[] memory _recipients,address[] memory _refferers, address[] memory _keyManagers, bytes12[] memory _data) external payable;
}

contract XClusiv{
    string public data = "Nothing received yet";
    ILayerZeroEndpoint endpoint;
    address usdcToken;

    constructor(address _lzEndpoint, address _usdcToken) {
        endpoint = ILayerZeroEndpoint(_lzEndpoint);
        usdcToken = _usdcToken;
    }

    enum StakeType{ERC20, NFT}
    enum StakeWithdrawn{FALSE, TRUE}

    struct Stake {
        StakeType stakeType;
        // if stakeType is nft, tokenAmountOrNFTId will be the nft identifier. Otherwise, it will be the token amount.
        uint256 tokenAmountOrNFTId;
        address contractAddress;
        // address of staker. The only address than can withdraw the stake. 
        address staker;
        StakeWithdrawn stakeWithdrawn;
    }

    uint256 public latestStakeId;
    mapping(uint256 => Stake) public stakeIdToStakes;
    mapping(address => uint256[]) public addressToStakeIds;

    event StakeComplete(address indexed _from, StakeType indexed _stakeType, uint256 _tokenAmountOrNFTId, address indexed contractAddress);
    event UnstakeComplete(uint256 indexed _stakeId, StakeType indexed _stakeType, address indexed _staker, address _contractAddress, uint256 _tokenAmountOrNFTId);

    function stake(bool isNFT, uint256 tokenAmountOrNFTId, address contractAddress ) external {
        // if isNFT == true, staked token is an nft 
        // otherwise, staked token is erc20
        if (isNFT) {
            // transfer nft to contract
            IERC721(contractAddress).safeTransferFrom(msg.sender, address(this), tokenAmountOrNFTId);
            // define stake
            stakeIdToStakes[latestStakeId] = Stake(StakeType.NFT, tokenAmountOrNFTId, contractAddress, msg.sender, StakeWithdrawn.FALSE); 
            // append stake id to msg.sender's list of stakes 
            addressToStakeIds[msg.sender].push(latestStakeId);
            // increment stake id 
            latestStakeId ++;
            // emit event
            emit StakeComplete(msg.sender, StakeType.NFT, tokenAmountOrNFTId, contractAddress);
        } else {
            // if stake type is erc20 
            // transfer tokens to contract
            IERC20(contractAddress).transferFrom(msg.sender, address(this), tokenAmountOrNFTId);
            // define stake
            stakeIdToStakes[latestStakeId] = Stake(StakeType.ERC20, tokenAmountOrNFTId, contractAddress, msg.sender, StakeWithdrawn.FALSE); 
            // append stake id to msg.sender's list of stakes 
            addressToStakeIds[msg.sender].push(latestStakeId);
            // increment stake id 
            latestStakeId ++;
            // emit event
            emit StakeComplete(msg.sender, StakeType.ERC20, tokenAmountOrNFTId, contractAddress);
        }
    }

    function unstake(uint256 stakeId) external {
        // only staker can withdraw
        require (stakeIdToStakes[stakeId].staker == msg.sender, "Only staker can unstake");
        // require that stake isn't already withdrawn
        require(stakeIdToStakes[stakeId].stakeWithdrawn == StakeWithdrawn.FALSE);
        // if staked token is nft, send the nft back to the staker
        if (stakeIdToStakes[stakeId].stakeType == StakeType.NFT) {
            IERC721(stakeIdToStakes[stakeId].contractAddress).safeTransferFrom(address(this), msg.sender, stakeIdToStakes[stakeId].tokenAmountOrNFTId);
            stakeIdToStakes[stakeId].stakeWithdrawn = StakeWithdrawn.TRUE;
            emit UnstakeComplete(stakeId, StakeType.NFT, msg.sender, stakeIdToStakes[stakeId].contractAddress, stakeIdToStakes[stakeId].tokenAmountOrNFTId);
        } // otherwise, send erc20 tokens back to the staker 
        else {
            IERC20(stakeIdToStakes[stakeId].contractAddress).transferFrom(address(this), msg.sender, stakeIdToStakes[stakeId].tokenAmountOrNFTId);
             stakeIdToStakes[stakeId].stakeWithdrawn = StakeWithdrawn.TRUE;
            emit UnstakeComplete(stakeId, StakeType.ERC20, msg.sender, stakeIdToStakes[stakeId].contractAddress, stakeIdToStakes[stakeId].tokenAmountOrNFTId);
        }
    }

    function estimateFees(uint16 _dstChainId, address _userApplication, uint256 usdAmount, address merchantAddress) external view returns(uint) {
        (uint nativeFee, uint zroFee) = endpoint.estimateFees(_dstChainId, _userApplication, abi.encodePacked(usdAmount, merchantAddress), false, bytes(""));
        return nativeFee;
    }

    function send(uint256 usdAmount, address receiverAddress, address destinationAddress, uint16 destChainId) external payable {
        IERC20(usdcToken).transferFrom(msg.sender, address(this), usdAmount);
        endpoint.send{value: msg.value}(destChainId, abi.encodePacked(destinationAddress, address(this)), abi.encode(usdAmount, receiverAddress), payable(0x680AE5639715c4fB867EBfD18a39b47988b29173), address(0x0), bytes(""));
    }

    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64 _nonce, bytes memory _payload) external {
        uint256 amount;
        address to;
        (amount, to) = abi.decode(_payload, (uint256, address));
        IERC20Mintable(usdcToken).mint(to, amount);
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external returns (bytes4) {
        return this.onERC721Received.selector;
    }
    // 0xbfD2135BFfbb0B5378b56643c2Df8a87552Bfa23, 0x0cf57e12b489dDC02a5d24a81eE359844A398917
    // 0x59503e8F59147A97CBA9F32A97154787aC53D4BF, 0x0cf57e12b489dDC02a5d24a81eE359844A398917, 0x69fa97e84003259247BA3c5B395400ba78637F48, 100000000000000000
    // 0x59503e8F59147A97CBA9F32A97154787aC53D4BF, 0x0cf57e12b489dDC02a5d24a81eE359844A398917, [20000000000000000000], [0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7], [0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7], [0x1C7dcaf39f5675C89DD5D65894F1d4F108eCcCE7], [0x0]
}
