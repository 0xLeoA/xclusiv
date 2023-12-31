// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";


contract USDC is ERC20 {
    constructor() ERC20("USDC", "USDC") {
        mint(msg.sender, 10000000*10**18);
    }

    function mint(address to, uint256 amount) public {
        _mint(to, amount);
    } 
}
