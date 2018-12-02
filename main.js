var async = require('async')

var Account = require('ethereumjs-account')
var Transaction = require('ethereumjs-tx')
var VM = require('ethereumjs-vm')
var Trie = require('merkle-patricia-tree')
var utils = require('ethereumjs-util')

var keyPair = require('./key-pair')

var stateTrie = new Trie()
var vm = new VM({state: stateTrie})


// overflow/underflow (toy) detector
var pcFlag = 0
var opA
var res
vm.on('step', function(e){
  var L = e.stack.length
  if (pcFlag != 0){
    console.log('Result:', e.stack[L-1].toString(16))
    res = e.stack[L-1]
    if (pcFlag == 1 && res.lt(opA)) console.log('--- Unsigned Overflow Detected ---')
    if (pcFlag == 2 && res.gt(opA)) console.log('--- Unsigned Underflow Detected ---')
    console.log()
    pcFlag = 0
  }
  if (e.opcode.name == 'ADD'){
    console.log('Trace:', e.opcode.name)
    console.log('Arg 0:', e.stack[L-1].toString(16))
    console.log('Arg 1:', e.stack[L-2].toString(16))
    opA = e.stack[L-1]
    pcFlag = 1
  }
  if (e.opcode.name == 'SUB'){
    console.log('Trace:', e.opcode.name)
    console.log('Arg 0:', e.stack[L-1].toString(16))
    console.log('Arg 1:', e.stack[L-2].toString(16))
    opA = e.stack[L-1]
    pcFlag = 2
  }
})


var myAccount
var myAddress
var myNonce
function setup (cb) {
  var publicKeyBuf = Buffer.from(keyPair.publicKey, 'hex')
  myAddress = utils.pubToAddress(publicKeyBuf, true)

  myAccount = new Account()
  myAccount.balance = '0xf00000000000000001'
  myNonce = 0

  stateTrie.put(myAddress, myAccount.serialize(), cb)
}


var contract_code
function readCode (cb) {
  var fs = require('fs')
  var fn = './testasm/testsol.bin'

  fs.readFile(fn, 'utf8', function(err, data) {
    if (err) throw err
    contract_code = data
    cb()
  })
}


var constructorTx
function getConstructorTx (cb) {
  var rawTx = {
    "nonce": "0x" + myNonce.toString(16),
    "gasPrice": "0x09184e72a000",
    "gasLimit": "0x90710",
    "data": "0x" + contract_code
  }
  myNonce ++
  var tx = new Transaction(rawTx)
  tx.sign(Buffer.from(keyPair.secretKey, 'hex'))
  constructorTx = tx
  cb()
}


var contractAddress
function runConstructorTx (cb) {
  vm.runTx({
    tx: constructorTx
  }, function (err, results) {
    contractAddress = results.createdAddress
    console.log('gas used: ' + results.gasUsed.toString())
    console.log('returned: ' + results.vm.return.toString('hex'))
    console.log()
    cb()
  })
}


var getCallerProc = function (value, payload) {
  return function (cb) {
    var rawTx = {
      nonce: '0x' + myNonce.toString(16),
      gasPrice: '0x09184e72a000',
      gasLimit: '0x20710',
      value: '0x' + value.toString(16),
      to: '0x' + contractAddress.toString('hex'),
      data: '0x' + payload
    }
    myNonce ++

    var tx = new Transaction(rawTx)
    tx.sign(Buffer.from(keyPair.secretKey, 'hex'))
    vm.runTx({
      tx: tx
    }, function (err, results) {
      console.log('gas used: ' + results.gasUsed.toString())
      console.log('returned: ' + results.vm.return.toString('hex'))
      console.log()
      cb()
    })
  }
}


function pr (cb) {
  //console.log(constructorTx)
  //console.log(myAccount)
  //console.log(myAddress)
  //console.log(stateTrie)
  //console.log(contractAddress)
}


var selector = function (sig) {
  return utils.keccak256(sig).slice(0, 4).toString('hex')
}


async.series([
  setup,
  readCode,
  getConstructorTx,
  runConstructorTx,
  getCallerProc(0, selector('overflow()')),
  getCallerProc(0, selector('max()')),
  getCallerProc(0, selector('underflow()')),
  getCallerProc(0, selector('zero()')),
  pr
])