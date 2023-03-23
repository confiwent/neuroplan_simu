import argparse, sys, time, collections
import os, signal, socket, json, pdb
import torch
# from rl.rl import RL
from planning.ilp import ILP
from topology.topology import Topology

def read_topo(topo_name, adjust_factor_in=None):
    assert(topo_name in ["A", "B", "C", "D", "E"])
    topo_name_map_file_path = {}
    topo_name_map_file_path["A"] = './source/data/Garr_syth.xlsx'
    
    file_path = topo_name_map_file_path[topo_name]
    
    topo = Topology(adjust_factor=adjust_factor_in)
    # topo.import_fiber_from_file(file_path)
    topo.import_lease_from_file(file_path)
    topo.import_l3_node_from_file(file_path)
    topo.import_l3_link_from_file(file_path)
    topo.import_tm_from_file(file_path)
    # topo.import_spof_from_file(file_path)
    
    # topo.gen_failed_ip_link_and_spof_map()
    # topo.generate_delta_bw_matrix_from_spof_list()

    return topo


if __name__ == "__main__":
    topo=read_topo("A", adjust_factor_in=0.5)
    print("Finish_test!")
    
