# evm_hook_test

## Prerequsites

* node.js (`sudo apt-get install nodejs npm`) : JavaScript terminal shell

* npm : Node package manager

* etheremjs-vm (`npm install ethereumjs-vm`) : JavaScript implementation of Ethereum virtual machine

* solc (`npm install -g solc`) : Solidity compiler

## Running the program

Type `make run` in the project directory. Expected output:

```
node main.js
gas used: 166489
returned: 608060405260043610610061576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680624264c3146100665780636ac5db191461007d578063bc1b392d146100a8578063dc75bec7146100d3575b600080fd5b34801561007257600080fd5b5061007b6100ea565b005b34801561008957600080fd5b506100926100fc565b6040518082815260200191505060405180910390f35b3480156100b457600080fd5b506100bd610102565b6040518082815260200191505060405180910390f35b3480156100df57600080fd5b506100e8610108565b005b60018060008282540192505081905550565b60015481565b60005481565b6001600080828254039250508190555056fea165627a7a72305820d257090f5a1ba2a7cca651d64cfd859a824b6da655023df8d71ca0bec37ddc820029

Trace: ADD
Arg 0: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
Arg 1: 1
Result: 0
--- Unsigned Overflow Detected ---

gas used: 13287
returned:

Trace: ADD
Arg 0: 20
Arg 1: 80
Result: a0

Trace: SUB
Arg 0: a0
Arg 1: 80
Result: 20

gas used: 21688
returned: 0000000000000000000000000000000000000000000000000000000000000000

Trace: SUB
Arg 0: 0
Arg 1: 1
Result: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
--- Unsigned Underflow Detected ---

gas used: 41704
returned:

Trace: ADD
Arg 0: 20
Arg 1: 80
Result: a0

Trace: SUB
Arg 0: a0
Arg 1: 80
Result: 20

gas used: 21710
returned: ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
```



