import networkx as nx
import copy
import random
import time

def weight(G, u, v):
    if(G.has_edge(u,v)):
        return G[u][v]['pp']
    else:
        return 0

class LDAG_Data:
    def __init__(self, localDAG, node):
        self.localDAG = localDAG
        self.node = node
        self.AP = {}
        self.alpha = {}
        self.deltaAP = {}
        self.deltaAlpha = {}
    
    def set_AP(self, u, value):
        self.AP[u] = value
    
    def set_alpha(self, u, value):
        self.alpha[u] = value

    def set_deltaAP(self, u, value):
        self.deltaAP[u] = value

    def set_deltaAlpha(self, u, value):
        self.deltaAlpha[u] = value

    def update_AP(self, u, value):
        self.AP[u] += value

    def update_alpha(self, u, value):
        self.alpha[u] += value

    def get_LDAG(self):
        return self.localDAG

    def get_node(self):
        return self.node

    def get_AP(self, u):
        return self.AP[u]
    
    def get_alpha(self, u):
        return self.alpha[u]

    def get_deltaAP(self, u):
        return self.deltaAP[u]

    def get_deltaAlpha(self, u):
        return self.deltaAlpha[u]
    
    def compute_alpha(self):
        for u in self.localDAG:
            self.alpha[u] = 0
        self.alpha[self.node] = 1
        sequenceP = list(reversed(list(nx.topological_sort(self.localDAG))))
        for u in sequenceP:
            if(u != self.node):
                for x in self.localDAG.neighbors(u):
                    self.alpha[u] += weight(self.localDAG, u, x) * self.alpha[x]

    def compute_deltaAP(self, s, seedNode):
        sequenceP = list(nx.topological_sort(self.localDAG))
        sIndex = sequenceP.index(s)
        sequenceP = sequenceP[sIndex + 1:]
        sequenceP = [x for x in sequenceP if x not in seedNode]
        for u in sequenceP:
            self.set_deltaAP(u, 0)
            for x in self.localDAG.predecessors(u):
                if(x in sequenceP):
                    self.deltaAP[u] += self.get_deltaAP(x) * weight(self.localDAG, x, u)

    def compute_deltaAlpha(self, s, seedNode):
        sequenceP = list(reversed(list(nx.topological_sort(self.localDAG))))
        sIndex = sequenceP.index(s)
        sequenceP = sequenceP[sIndex + 1:]
        sequenceP = [x for x in sequenceP if x not in seedNode]
        for u in sequenceP:
            self.set_deltaAlpha(u, 0)
            for x in self.localDAG.neighbors(u):
                if(x in sequenceP):
                    self.deltaAlpha[u] += weight(self.localDAG, u, x) * self.get_deltaAlpha(x)

class LDAG:
    def __init__(self):
        pass

    def preprocess(self, G):
        directedGraph = nx.DiGraph()
        for u in G.nodes():
            for v in G.neighbors(u):
                if(v != u):
                    propProb = G.number_of_edges(u,v) / G.in_degree(v)
                    directedGraph.add_edge(u, v, pp=propProb)
        return directedGraph

    def findLDAG(self, G, v, simThreshold):
        LDAG = nx.DiGraph()
        Inf = {}
        selectedNodes = []
        for node in G.nodes():
            Inf[node] = 0
        Inf[v] = 1
        maxInf = v
        selectedNodes.append(maxInf)
        while (Inf[maxInf] >= simThreshold):
            nodes = copy.deepcopy(LDAG.nodes())
            for node in nodes:
                LDAG.add_edge(maxInf, node, pp=weight(G, maxInf, node))
            del nodes
            LDAG.add_node(maxInf)
            for node in G.predecessors(maxInf):
                Inf[node] += weight(G, node, maxInf) * Inf[maxInf]
            if(len(selectedNodes) >= len(G.nodes())):
                break
            maxInf = max({x: Inf[x] for x in Inf if x not in selectedNodes}, key=Inf.get)
            selectedNodes.append(maxInf)
        return LDAG

    def findSeed(self, G, simThreshold, K):
        # Preparation Phase (Line 1 - 3)
        seedNode = [] 
        IncInf = {}
        for node in G.nodes():
            IncInf[node] = 0

        # Line 4 - 11        
        listOfLDAG = {}
        startTime = time.time()
        for v in G.nodes():
            nodeLDAG = self.findLDAG(G, v, simThreshold) #(Line 5)
            tempLDAG = LDAG_Data(nodeLDAG, v) 
            for u in nodeLDAG.nodes():
                tempLDAG.set_AP(u, 0) # Line 7
            tempLDAG.compute_alpha()
            for u in nodeLDAG.nodes():
                IncInf[u] += tempLDAG.get_alpha(u)
            listOfLDAG[v] = tempLDAG
        
        endTime = time.time()
        totalFindLDAGTime = endTime - startTime
        print("Time needed to find all LDAG : " + str(round(totalFindLDAGTime, 2)) + " seconds")

        # Main Loop (Line 13)
        for _ in range(K):
            s = max({x: IncInf[x] for x in IncInf if x not in seedNode}, key=IncInf.get) # (Line 15)
            InfSet = []
            for v in listOfLDAG: # Find InfSet (Before Line 16)
                if(v != s and v not in seedNode and s in list(listOfLDAG[v].localDAG.nodes())): 
                    InfSet.append(v)
            for v in InfSet: # (Start Line 16)
                listOfLDAG[v].set_deltaAlpha(s, -(listOfLDAG[v].get_alpha(s))) # Line 18
                for u in seedNode: # Line 18
                    listOfLDAG[v].set_deltaAlpha(u, 0)
                
                listOfLDAG[v].compute_deltaAlpha(s, seedNode) # Line 19-20

                sequenceP = list(reversed(list(nx.topological_sort(listOfLDAG[v].localDAG))))
                sIndex = sequenceP.index(s)
                sequenceP = sequenceP[sIndex:]
                for u in sequenceP:
                    listOfLDAG[v].update_alpha(u, listOfLDAG[v].get_deltaAlpha(u)) # Line 21
                    IncInf[u] += listOfLDAG[v].get_deltaAlpha(u) * (1 - listOfLDAG[v].get_AP(u)) # Line 22

                listOfLDAG[v].set_deltaAP(s, 1 - (listOfLDAG[v].get_AP(s))) # Line 24
                for u in seedNode: # Line 24
                    listOfLDAG[v].set_deltaAP(u, 0)
                
                listOfLDAG[v].compute_deltaAP(s, seedNode) # Line 25-26 

                sequenceP = list(nx.topological_sort(listOfLDAG[v].localDAG))
                sIndex = sequenceP.index(s)
                sequenceP = sequenceP[sIndex:]
                for u in sequenceP:
                    listOfLDAG[v].update_AP(u, listOfLDAG[v].get_deltaAP(u))
                    IncInf[u] -= listOfLDAG[v].get_alpha(u) * listOfLDAG[v].get_deltaAP(u)

            seedNode.append(s) # Line 30

        return seedNode

    def simulate(self, G, seedNode):
        # Set Random threshold for every node ~ [0,1]
        nodeThresholds = {}
        for node in G.nodes():
            nodeThresholds[node] = random.uniform(0,1)
        
        nodeValues = {}
        for node in G.nodes():
            nodeValues[node] = 0

        newActive = True
        currentActiveNodes = copy.deepcopy(seedNode)
        newActiveNodes = set()
        activatedNodes = copy.deepcopy(seedNode) # Prevent from activating node twice
        influenceSpread = len(seedNode)
        
        while(newActive):
            for node in currentActiveNodes:
                for neighbor in G.neighbors(node): 
                    if(neighbor not in activatedNodes):
                        nodeValues[neighbor] += weight(G, node, neighbor)
                        if(nodeValues[neighbor] >= nodeThresholds[neighbor]): 
                            newActiveNodes.add(neighbor)
                            activatedNodes.append(neighbor)
            influenceSpread += len(newActiveNodes)
            if newActiveNodes:
                currentActiveNodes = list(newActiveNodes)
                newActiveNodes = set()
            else:
                newActive = False
        return influenceSpread