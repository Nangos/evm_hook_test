compile:
	rm -rf testasm
	mkdir testasm
	solc --asm -o testasm testsol.sol
	solc --bin -o testasm testsol.sol
	mv testasm/*.evm testasm/testsol.evm
	mv testasm/*.bin testasm/testsol.bin

clean:
	rm testasm/*

run:
	node main.js
