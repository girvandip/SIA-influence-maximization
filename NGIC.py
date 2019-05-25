import networkx as nx
import random
import copy
import time

class NGIC:
    def __init__(self):
        pass
    def preprocess(self, G, propProbability):
        directedGraph = nx.DiGraph()
        for u in G.nodes():
            for v in G.neighbors(u):
                if(u != v):
                    directedGraph.add_edge(u, v, pp=propProbability)
        return directedGraph

    def findSeed(self, G, R, K, propProbability):
        seedNode = [] 
        for _ in range(K): # (Line 2)
            nodeValues = {} #Initialize Sv (Line 3)
            for node in G.nodes():
                nodeValues[node] = 0
            for _ in range(R):
                #CREATING SUBGRAPH G' (Line  5)
                start = time.time()
                removedEdge = [] #Initialize for removal of edge (Line 5)
                setOfReachables = set()
                for edge in G.edges():
                    if(not(self.flipCoin(propProbability))):
                        removedEdge.append(edge)
                subgraph = G.copy()
                for edge in removedEdge:
                    subgraph.remove_edge(edge[0], edge[1])

                end = time.time()
                total = end - start
                print("Subgraph creation time : " + str(total))

                start = time.time()
                #Compute RG'(S) (Line 6)
                for node in seedNode: 
                    setOfReachables.update(nx.dfs_preorder_nodes(subgraph,node))
                
                #Starting at (Line 8), Compute Line 7 if in condition
                for node in subgraph.nodes():
                    if (node not in seedNode and node not in setOfReachables):
                        nodeValues[node] += len(list(nx.dfs_preorder_nodes(subgraph, node)))
                end = time.time()
                total = end - start
                print("Calculation time : " + str(total))
                
            # Find Mean of all nodeValues (Line 14)
            nodeValues = {k: v / R for k, v in nodeValues.items()}
            # Node that has the max value (Line 15)
            maxNode = max(nodeValues, key=nodeValues.get)
            seedNode.append(maxNode)

        return seedNode

    def simulate(self, G, seedNode, propProbability):
        newActive = True
        currentActiveNodes = copy.deepcopy(seedNode)
        newActiveNodes = set()
        activatedNodes = copy.deepcopy(seedNode) # Biar ga keaktivasi 2 kali
        influenceSpread = len(seedNode)

        while(newActive):
            for node in currentActiveNodes:
                for neighbor in G.neighbors(node): #Harus dicek udah aktif apa belom, jangan sampe ngaktifin yang udah aktif
                    if(neighbor not in activatedNodes):
                        if(self.flipCoin(propProbability)):
                            newActiveNodes.add(neighbor)
                            activatedNodes.append(neighbor)
            influenceSpread += len(newActiveNodes)
            if newActiveNodes:
                currentActiveNodes = list(newActiveNodes)
                newActiveNodes = set()
            else:
                newActive = False

        return influenceSpread

    def flipCoin(self, probability):
        return random.random() < probability