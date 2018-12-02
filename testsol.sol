pragma solidity ^0.5.0;

// Contract to test unsigned integer underflows and overflows
// note: uint in solidity is an alias for uint256

// Guidelines: Press "Create" to the right, then check the values of max and zero by clicking "Call"
// Then, call overflow and underflow and check the values of max and zero again

contract OverflowUnderFlow {
    uint public zero = 0;
    uint public max = 2**256-1;
    
    // zero will end up at 2**256-1
    function underflow() public {
        zero -= 1;
    }
    // max will end up at 0
    function overflow() public {
        max += 1;
    }
}