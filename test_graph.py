import os, sys, json, pickle
import pandas as pd
import numpy as np 
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import math
from random import sample

def main():
    path = './source/data/signals/graph_signal_0.json'
    
    with open(path, 'r') as f:
        # dic_graph = pickle.load(f)
        dic_graph = f.read()
    dic_graph = json.loads(dic_graph)
    
    # graph = nx.Graph(dic_graph)
    graph = json_graph.node_link_graph(dic_graph)
    adj = nx.adj_matrix(graph)
    print('Reload graph!')

if __name__ == '__main__':
    main()