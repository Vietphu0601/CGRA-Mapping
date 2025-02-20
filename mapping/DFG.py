#node of the DFG
class node:
    def __init__(self, id, rOp, lOp, predicate, name, opcode):
        self.id = id
        self.rOp = rOp
        self.lOp = lOp
        self.name = name
        self.predicate = predicate
        self.opcode = opcode
        self.index = -1
        self.lowlink = 0
        self.onstack = False
        self.time = 1
        self.latency = 1
    def __del__(self):
        self.index = -1
        self.lowlink = 0
        self.onstack = False
        self.time = 1
        self.latency = 1

#edge of the DFG
class edge:
    def __init__(self, source, destination, distance, latency):
        self.source = source
        self.destination = destination
        self.distance = distance
        self.latency = latency
#constant node associate to the DFG
class constant:
    def __init__(self, id, destination, value, opPos):
        self.id = id
        self.destination = destination
        self.value = value
        self.opPos = opPos

class DFG:
        return None