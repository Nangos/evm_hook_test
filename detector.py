def is_contract(addr):
    pass

def read_trace_from(file_name):
    # return type: Trace
    pass


class Item:
    def __init__(self, opcode, inputs, outputs, subprocs=None):
        self.opcode = opcode # type: Python string
        self.inputs = inputs # type: Python list of Python integer
        self.outputs = outputs # type: Python list of Python integer
        self.subprocs = subprocs # type: None or Python list of Item

    def __str__(self):
        c = self.opcode
        for i in self.inputs:
            c += ' ' + i
        if self.subprocs:
            c += ' { ... }'
        c += ' =>'
        for o in self.outputs:
            c += ' ' + o
        return c


class Trace:
    # included in metadata: addr, is_constructor
    def __init__(self, metadata, items):
        self.metadata = metadata # type: Python dict
        self.items = items # type: Python list of Item
        self.detectors = [
            arith_detector,
            race_detector,
            delegate_detector,
            unchecked_detector,
            addr_detector,
            blockinfo_detector
        ]

    def run(self):
        for d in self.detectors:
            self.d()

    # for arithmetic anomalies (outflow & zerodiv)
    # (assuming uint)
    def arith_detector(self):
        def exp_check(a, b, c):
            if a >= 2 and b >= 256:
                return True
            else:
                return a ** b != c
        def recursive(items):
            for item in items:
                if item.opcode == 'ADD':
                    if item.inputs[0] + item.inputs[1] != item.outputs[0]:
                        print 'unsigned overflow: ' + item
                elif item.opcode == 'SUB':
                    if item.inputs[0] - item.inputs[1] != item.outputs[0]:
                        print 'unsigned underflow: ' + item
                elif item.opcode == 'MUL':
                    if item.inputs[0] * item.inputs[1] != item.outputs[0]:
                        print 'unsigned overflow: ' + item
                elif item.opcode == 'EXP':
                    if exp_check(item.inputs[0], item.inputs[1], item.outputs[0]):
                        print 'unsigned overflow: ' + item
                elif item.opcode in ['DIV', 'SDIV', 'MOD', 'SMOD']:
                    if item.inputs[1] == 0:
                        print 'divided by zero: ' + item
                elif item.opcode in ['ADDMOD', 'MULMOD']:
                    if item.inputs[2] == 0:
                        print 'divided by zero: ' + item
                elif item.subprocs:
                    recursive(item.subprocs)
        recursive(self.items)

    # for cross-function races
    def race_detector(self):
        call_stack = [{
          'addr': self.metadata['addr'],
          'reentered': False
        }]
        def is_reentered(stack, new_addr):
            sm = lambda a,b: 2 if a == 2 else a + (a ^ b) # transition rule of state machine
            seq = [x['addr'] == new_addr for x in stack] # sequence to feed
            return reduce(sm, seq, 0) == 2 # reentered iff state == 2 
        def recursive(items):
            for item in items:
                if call_stack[-1]['reentered']:
                    if item.opcode == 'SSTORE': # state override
                        print 'condition race: ' + item
                    elif item.opcode == 'CALL' and item.inputs[2] > 0: # money transfer
                        print 'condition race: ' + item
                if item.opcode in ['CALL', 'STATICCALL']:
                    call_stack.append({
                      'addr': item.inputs[1],
                      'reentered': is_reentered(call_stack, item.inputs[1])
                    })
                    recursive(item.subprocs)
                    call_stack.pop()
                elif item.opcode in ['DELEGATECALL', 'CALLCODE']:
                    recursive(item.subprocs)
        recursive(self.items)
    
    # for dangerous delegate calls
    def delegate_detector(self):
        def recursive(items, is_dele_env):
            if is_dele_env: # i.e. in a delegate call enviroment
                for item in items:
                    if item.opcode in ['SSTORE', 'SELFDESTRUCT']:
                        print 'dangerous delegate call: ' + item
                    elif item.opcode == 'CALL' and item.inputs[2] > 0:
                        print 'dangerous delegate call: ' + item
                    if item.subprocs:
                        recursive(item.subprocs, item.opcode in ['DELEGATECALL, CALLCODE'])
            else:
                for item in items:
                    if item.subprocs:
                        recursive(item.subprocs, item.opcode in ['DELEGATECALL, CALLCODE'])
        recursive(self.items, False)

    # for unchecked return
    def unchecked_detector(self):
        def recursive(items):
            state = 0
            target_item = None
            for item in items:
                if state == 1:
                    if item.opcode is 'JUMPI':
                        state = 0
                        continue
                    elif item.opcode is 'ISZERO':
                        continue
                    else:
                        print 'unchecked return: ' + target_item
                        state = 0
                if item.subprocs:
                    recursive(item.subprocs)
                    if item.outputs[0] == 0: # a return with exception
                        state = 1
                        target_item = item
        recursive(self.items)

    # for contract address modification
    def addr_detector(self):
        def recursive(items):
            for item in items:
                if item.opcode == 'SSTORE':
                    if is_contract(items.inputs[1]):
                        print 'contract address modified: ' + item
                if item.subprocs:
                    recursive(item.subprocs)
        if not self.metadata['is_constructor']:
            recursive(self.items)

    # for improper calculation on block information
    # (only catches on-stack local dependency)
    def blockinfo_detector(self):
        blockinfo_opcodes = [
          'BLOCKHASH', 'COINBASE', 'TIMESTAMP',
          'NUMBER', 'DIFFICULTY', 'GASLIMIT'
        ]
        def recursive(items):
            seed_marks = []
            for item in items:
                seed_dependent = item.opcode in blockinfo_opcodes
                for i in item.inputs:
                    seed_dependent |= seed_marks.pop()
                for o in item.outputs:
                    seed_marks.append(seed_dependent)
                if seed_dependent:
                    if item.opcode in ['MOD', 'SMOD', 'ADDMOD', 'MULMOD', 'AND']:
                        print 'improper randomness: ' + item
                if item.subprocs:
                    recursive(item.subprocs)
        recursive(self.items)