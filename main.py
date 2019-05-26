import random
import networkx as nx
import copy
import time
from datetime import datetime
from NGIC import NGIC
from LDAG import LDAG

# CONST
DEFAULT_PROP_PROBABILITY = 0.01

# READ DATASET
print("Input dataset location :")
FILENAME = str(input())

print("START READING DATASET")
print("File: " + FILENAME)

G = nx.read_edgelist(FILENAME, create_using=nx.MultiDiGraph, nodetype=int, data=(('timestamp', float),))

print("FINISHED READING\n")

print("Number of nodes: " + str(len(list(G.nodes()))))
print("Number of edges: " + str(len(list(G.edges()))) + "\n")

preprocessedGraph = nx.DiGraph()

print ("Input number of seed nodes (K): ")
K = int(input())

print ("Choose Algorithm : LDAG or NGIC?")
print ("1 -> LDAG")
print ("2 -> NGIC")

modelpicked = int(input())

NGIC = NGIC()
LDAG = LDAG()
seedNode = None
propProbability = DEFAULT_PROP_PROBABILITY

# Preprocessing
if(modelpicked == 1):
    print("\nPreprocessing Graph...")
    preprocessedGraph = LDAG.preprocess(G)
    print("Graph preprocessed!\n")

    print ("Input simulation threshold (Teta): ")
    simThreshold = float(input())

    # Find Seed Node using LDAG Algorithm
    print("\nFinding Seed Node using LDAG Algorithm...\n")

    startTime = time.time()
    seedNode = LDAG.findSeed(preprocessedGraph, simThreshold, K)
    endTime = time.time()
    totalElapsedTime = endTime - startTime

    print("Seed Node: " + str(seedNode))
    print("Total time for finding seed node: " + str(round(totalElapsedTime, 2)) + " seconds\n")

else:
    print ("Input propagation probability for all edges : ")
    propProbability = float(input())

    print("\nPreprocessing Graph...")
    preprocessedGraph = NGIC.preprocess(G, propProbability)
    print("Graph preprocessed!\n")

    print("Input number of simulations (R): ")
    R = int(input())

    # Find Seed Node using NGIC Algorithm
    print("\nFinding Seed Node using NGIC Algorithm...\n")

    startTime = time.time()
    seedNode = NGIC.findSeed(preprocessedGraph, R, K, propProbability)
    endTime = time.time()
    totalElapsedTime = endTime - startTime

    print("Seed Node: " + str(seedNode))
    print("Total time for finding seed node: " + str(round(totalElapsedTime, 2)) + " seconds\n")

#Choose Model
print("Choose Model : LT or IC?")
print("1 -> LT")
print("2 -> IC")
model = int(input())
if(model == 1):
    print("Modelling influence spread using LT Model...\n")
    influenceSpread = LDAG.simulate(preprocessedGraph, seedNode)
    print("Total influence spread: " + str(influenceSpread))
else:
    print("Modelling influence spread using IC Model...\n")
    propProbability = 0.01
    influenceSpread = NGIC.simulate(preprocessedGraph, seedNode, propProbability)
    print("Total influence spread: " + str(influenceSpread))