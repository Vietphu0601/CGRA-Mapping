import math
import itertools
import time
from tracemalloc import take_snapshot
from z3 import *
from RegisterAllocator import *

class Mapper:
    
    def __init__(self, x, y, r, dfg, benchmark):
        
        self.CGRA_x = x
        self.CGRA_Y = y    
        self.CGRA_R = r
        self.s = Solver()
        self.benchmark = benchmark
        
        self.DFG = dfg
        self.ResII = 0
        self.RecII = 0
        self.II = 0
        self.ASAP = {}
        self.ALAP = {}
        self.MS = {}
        self.KMS = {}
        self.scheduleLen = 0
        
        #schedule found by solver that can be modulo scheduled
        '''init: Giai đoạn load dữ liệu đầu vào (live-in)
        pke: Prolog + Kernel + Epilog
        fini: Kết quả (live-out)
        '''
        self.schedule = {}
        self.prolog = {}
        self.kernel = {}
        self.epilog = {}

        self.init = {}
        self.pke = {}
        self.fini = {}
        self.mapping = {}

        self.ra = None

    def __del__(self):

        self.DFG = None
        self.ResII = 0
        self.RecII = 0
        self.II = 0
        self.scheduleLen = 0
        self.ASAP.clear()
        self.ALAP.clear()
        self.MS.clear()
        self.KMS.clear()
        self.schedule.clear()
        self.prolog.clear()
        self.kernel.clear()
        self.epilog.clear()
        self.init.clear()
        self.fini.clear()
        self.mapping.clear()
        self.ra = None

    #Tìm ResII
    def computeResII(self):
        self.ResII = math.ceil(len(self.DFG.nodes)/(self.CGRA_x*self.CGRA_Y))

    #Lấy giá trị RecII
    def computeRecII(self):
        for s in self.DFG.getSCCs():
            self.RecII = max(self.DFG.getPathDelay(s), self.RecII)        

    #Lấy giá trị MII
    def getStartingII(self):            
        self.computeRecII()
        self.computeResII()
        self.II = max(self.RecII, self.ResII)
        print("REC " + str(self.RecII))
        print("RES " + str(self.ResII))
        return self.II

    #Tạo lịch trình ASAP
    def generateASAP(self):
        self.ASAP.clear()
        self.DFG.resetNodeTime(0)
        to_explore = self.DFG.getStartingNodes()
        while to_explore:
            tmp = []
            for n in to_explore:
                for sn in self.DFG.getSuccessors(n):
                    if sn.name != "phi":
                        sn.time = max(sn.time, n.time + 1)
                        tmp.append(sn)
                        self.scheduleLen = max(self.scheduleLen, sn.time)
            to_explore = tmp[:]
            tmp.clear()
        
        for n in self.DFG.nodes:
            if n.time not in self.ASAP:
                self.ASAP[n.time] = []
            self.ASAP[n.time].append(n.id)

    '''    print("\nASAP Schedule")
        for t in range(0, len(self.ASAP)):
            tmp = ""
            for e in self.ASAP[t]:
                tmp+= str(e) + " "
            print(tmp)
        print() '''
    
    #Tạo lịch trình ASAP
    def generateALAP(self):
        self.DFG.resetNodeTime(0)
        to_explore = self.DFG.getEndingNodes()
        while to_explore:
            tmp = []
            for n in to_explore:
                for sn in self.DFG.getPredecessors(n):
                    if sn.name != 'phi':
                        sn.time = max(sn.time, n.time + 1)
                        tmp.append(sn)
                        self.scheduleLen = max(self.scheduleLen, sn.time)
                    else:
                        sn.time = max(sn.time, n.time + 1)
                        self.scheduleLen = max(self.scheduleLen, sn.time)

            to_explore = tmp[:]
            tmp.clear()

        for n in self.DFG.nodes:
            if (self.scheduleLen - n.time) not in self.ALAP:
                self.ALAP[self.scheduleLen - n.time] = []
            self.ALAP[self.scheduleLen - n.time].append(n.id)
        
        ''' print("\nALAP Schedule")
        for t in range(0, len(self.ALAP)):
            tmp = ""
            for e in self.ALAP[t]:
                tmp+= str(e) + " "
            print(tmp)
        print() '''

    def getASAPTime(self, id):
        for t in self.ASAP:
            for nid in self.ASAP[t]:
                if nid == id:
                    return t
        return -1

    def getALAPTime(self, id):
        for t in self.ALAP:
            for nid in self.ALAP[t]:
                if nid == id:
                    return t
        return -1

    #Tạo lịch Mobility schedule
    def generateMS(self):
        self.ASAP.clear()
        self.ALAP.clear()
        self.generateASAP()
        self.generateALAP()

        for n in self.DFG.nodes:

            t_asap = self.getASAPTime(n.id)
            t_alap = self.getALAPTime(n.id)

            for t in range(t_asap, t_alap + 1):
                if t not in self.MS:
                    self.MS[t] = []
                self.MS[t].append(n.id)
        
        ''' print("\nMobility Schedule")
        for t in range(0, len(self.MS)):
            tmp = ""
            for e in self.MS[t]:
                tmp+= str(e) + " "
            print(tmp)
        print() '''
    
    #Tạo Kernel Mobility Schedule
    def generateKMS(self, II):
        self.KMS.clear()
        if II <= self.scheduleLen + 1:
            for i in range(0,self.scheduleLen + 1):
                it = i//II
                
                if (i%II) not in self.KMS:
                    self.KMS[i%II] = []
                for nid in self.MS[i]:
                    self.KMS[i%II].append((it, nid))
        else:
            dup = II - (self.scheduleLen + 1)
            it = 0
            tmpKMS = {}
            for d in range(0, dup + 1):
                for i in range(0, self.scheduleLen + 1):
                    if (i + d) not in tmpKMS:
                        tmpKMS[i + d] = []
                    for nid in self.MS[i]:
                        if nid not in tmpKMS[i + d]:
                            tmpKMS[i + d].append(nid)

                d += 1
            
            for t in tmpKMS:
                if t not in self.KMS:
                    self.KMS[t] = []
                for nid in tmpKMS[t]:
                    self.KMS[t].append((it, nid))
            

    #Thêm ràng buộc thứ nhất
    def addConstraint1(self, node_literals):
        #print("Adding C1...")
        start = time.time()
        for nodeid in node_literals:
            phi = Or(node_literals[nodeid])
            tmp = []
            for i in range(len(node_literals[nodeid])-1):
                for j in range(i+1, len(node_literals[nodeid])):
                    tmp.append(Not(And(node_literals[nodeid][i], node_literals[nodeid][j])))
            tmp = And(tmp)
            exactlyone = And(phi,tmp)
            self.s.add(exactlyone)
        end = time.time()
        #print("Time: " + str(end - start))

    #Thêm ràng buộc thứ hai
    def addConstraint2(self, cycle_pe_literals):
        #print("Adding C2...")
        start = time.time()
        for cycle in cycle_pe_literals:
            for pe in cycle_pe_literals[cycle]:
                tmp = []
                for i in range(len(cycle_pe_literals[cycle][pe])-1):
                    for j in range(i+1, len(cycle_pe_literals[cycle][pe])):
                        tmp.append(Or(Not(cycle_pe_literals[cycle][pe][i]), Not(cycle_pe_literals[cycle][pe][j])))
                if len(tmp) > 1:
                    tmp = And(tmp)
                elif len(tmp) == 0:
                    continue
                self.s.add(tmp)
        end = time.time()
        #print("Time: " + str(end - start))

    #Thêm ràng buộc thứ 3
    def addConstraint3(self, II, c_n_it_p_literal, cycle_pe_literals):
        #print("Adding C3...")
        BRs = ["beq","bne","blt","bge","ble","bgt"]
        SEL = ["bzfa", "bsfa"]
        start = time.time()
        all_dep_encoded = True
        found_br = False
        for e in self.DFG.edges:
            if e.distance > 0:
                #backdependencies handled in a different way
                continue
            nodes = [e.source.id, e.destination.id]
            #print(nodes)
            tmp = []
            
            for (cs,cd) in itertools.product(c_n_it_p_literal, c_n_it_p_literal):
                if (nodes[0] not in c_n_it_p_literal[cs]) or (nodes[1] not in c_n_it_p_literal[cd]):
                    continue
                ns = nodes[0]
                nd = nodes[1]
                #filter for br node
                #BR nodes can be mapped only on the last cycle of the kernel
                #else additional resolution techniques needs to be implemented to handle BRs
                #This reduces the space of all the valid solutions
                if self.DFG.getNode(nd).name in BRs and cd != (II - 1):
                    continue
                else:
                    found_br = True
                #select flag should be in rout
                #avoid solutions that use internal registers
                if self.DFG.getNode(nd).name in SEL and self.DFG.getNode(nd).predicate == ns:
                    for (it1, it2) in itertools.product(c_n_it_p_literal[cs][ns], c_n_it_p_literal[cd][nd]):
                        if it1 == it2 and cd > cs:
                            for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                                if(self.isNeighbor(p1, p2)):
                                    distance = self.getCycleDistance(cs, cd, II)
                                    if distance == 1:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                    elif distance > 1:
                                        tmp2 = []
                                        for ci in range(cs + 1, cd):
                                            tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                        if len(tmp2) > 1:#before was only tmp append tmp2
                                            tmp.append(And(tmp2))
                                        elif len(tmp2) == 1:
                                            tmp.append(tmp2[0])
                                        #tmp.append(And(tmp2))
                                        #if p1 == p2:
                                        #    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                        elif abs(it1 - it2) == 1 and it1 < it2 and cd <= cs:
                            for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                                if(self.isNeighbor(p1, p2)):
                                    distance = self.getCycleDistance(cs, cd, II)
                                    if distance == 1:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                    elif distance > 1:
                                        tmp2 = []
                                        for ci in range(cs + 1, II):
                                            tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                        for ci in range(0, cd):
                                            tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))

                                        if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                            tmp.append(And(tmp2))
                                        elif len(tmp2) == 1:
                                            tmp.append(tmp2[0])

                                        #if p1 == p2:
                                        #    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                    elif distance == 0:
                                        tmp2 = []
                                        if p1 == p2:
                                            continue
                                        for ci in range(0, II):
                                            if ci == cs:
                                                continue
                                            tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                        if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                            tmp.append(And(tmp2))
                                        elif len(tmp2) == 1:
                                            tmp.append(tmp2[0])
                                    else:
                                        #print("Should not be here 2")
                        
                    if len(tmp) == 0:
                        continue
                        #print("No constraint for this dep. Need to check")
                        all_dep_encoded = False
                        #print(nodes[0], nodes[1])
                        # break
                    # self.s.add(Or(tmp))
                    continue



                for (it1, it2) in itertools.product(c_n_it_p_literal[cs][ns], c_n_it_p_literal[cd][nd]):
                    if it1 == it2 and cd > cs:
                        for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                            if(self.isNeighbor(p1, p2)):
                                distance = self.getCycleDistance(cs, cd, II)
                                if distance == 1:
                                    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                elif distance > 1:
                                    tmp2 = []
                                    for ci in range(cs + 1, cd):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                    if len(tmp2) > 1:#before was only tmp append tmp2
                                        tmp.append(And(tmp2))
                                    elif len(tmp2) == 1:
                                        tmp.append(tmp2[0])
                                    #tmp.append(And(tmp2))
                                    if p1 == p2:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                    elif abs(it1 - it2) == 1 and it1 < it2 and cd <= cs:
                        for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                            if(self.isNeighbor(p1, p2)):
                                distance = self.getCycleDistance(cs, cd, II)
                                if distance == 1:
                                    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                elif distance > 1:
                                    tmp2 = []
                                    for ci in range(cs + 1, II):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                    for ci in range(0, cd):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))

                                    if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                        tmp.append(And(tmp2))
                                    elif len(tmp2) == 1:
                                        tmp.append(tmp2[0])

                                    if p1 == p2:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                elif distance == 0:
                                    tmp2 = []
                                    if p1 == p2:
                                        continue
                                    for ci in range(0, II):
                                        if ci == cs:
                                            continue
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                    if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                        tmp.append(And(tmp2))
                                    elif len(tmp2) == 1:
                                        tmp.append(tmp2[0])
                                else:
                                    #print("Should not be here 2")
                    
            if len(tmp) == 0:
                #print("No constraint for this dep. Need to check")
                all_dep_encoded = False
                #print(nodes[0], nodes[1])
                break
            self.s.add(Or(tmp))
        if not found_br:
            #print("Cannot find BR node in last cycle of the kernel.\n Comment this if you don't care or check DFG/MS")

        if not all_dep_encoded:
            self.s.reset()
            return all_dep_encoded
        all_dep_encoded = True
        #handle backdeps
        #print("Adding back...")	
        for e in self.DFG.edges:
            if e.distance < 1:
                #backdependencies handled in a different way
                continue 
            nodes = [e.source.id, e.destination.id]
            #print(nodes)
            tmp = []
            for (cs,cd) in itertools.product(c_n_it_p_literal, c_n_it_p_literal):
                if (nodes[0] not in c_n_it_p_literal[cs]) or (nodes[1] not in c_n_it_p_literal[cd]):
                    continue
                ns = nodes[0]
                nd = nodes[1]
                for (it1, it2) in itertools.product(c_n_it_p_literal[cs][ns], c_n_it_p_literal[cd][nd]):
                    if abs(it1 - it2) > 1:
                        continue
                    if it1 == it2 and cs > cd:
                        for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                            if(self.isNeighbor(p1, p2)):
                                distance = self.getCycleDistance(cs, cd, II)
                                if distance == 1:
                                    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                elif distance > 1:
                                    tmp2 = []
                                    for ci in range(cs + 1, II):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                    for ci in range(0, cd):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))

                                    if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                        tmp.append(And(tmp2))
                                    elif len(tmp2) == 1:
                                        tmp.append(tmp2[0])

                                    if p1 == p2:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))

                    elif it1 > it2 and cs < cd:
                        for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                            if(self.isNeighbor(p1, p2)):
                                distance = self.getCycleDistance(cs, cd, II)
                                if distance == 1:
                                    tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                                elif distance > 1:
                                    tmp2 = []
                                    for ci in range(cs + 1, II):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                    for ci in range(0, cd):
                                        tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))

                                    if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                        tmp.append(And(tmp2))
                                    elif len(tmp2) == 1:
                                        tmp.append(tmp2[0])

                                    if p1 == p2:
                                        tmp.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2]))
                    elif it1 == it2 and cs == cd:
                        #we need this to take care of loop carried dependencies (usually between phi nodes)
                        #I will not find problems in the schedule because if there is a dependency and a
                        #backdependecy for two nodes, the sat solver is not going to take this solution
                        #because it will make the data dependency constraint unusable and viceversa.
                        for (p1, p2) in itertools.product(c_n_it_p_literal[cs][ns][it1], c_n_it_p_literal[cd][nd][it2]):
                            if(self.isNeighbor(p1, p2)):
                                if p1 == p2:
                                    continue
                                tmp2 = []
                                for ci in range(0, II):
                                    if ci == cs:
                                        continue
                                    tmp2.append(And(c_n_it_p_literal[cs][ns][it1][p1], c_n_it_p_literal[cd][nd][it2][p2], cycle_pe_literals[ci][p1]))
                                if len(tmp2) > 1:#before was only len(tmp2) != 0:
                                    tmp.append(And(tmp2))
                                elif len(tmp2) == 1:
                                    tmp.append(tmp2[0])
                                        
                    
            if len(tmp) == 0:
                #print("No constraint for this backdep. Need to check")
                #print(nodes[0], nodes[1])
                all_dep_encoded = False
                break
            self.s.add(Or(tmp))

        if not all_dep_encoded:
            self.s.reset()
            return all_dep_encoded