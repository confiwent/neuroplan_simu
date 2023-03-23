import argparse, sys, time, collections
import os, signal, socket, json, pdb
import torch
# from rl.rl import RL
from planning.ilp import ILP
from topology.topology import Topology

def read_topo(topo_name, adjust_factor_in=None):
    assert(topo_name in ["A", "B", "C", "D", "E"])
    topo_name_map_file_path = {}
    topo_name_map_file_path["A"] = './source/data/Topo_syth_Janetbackbone.xlsx'
    
    file_path = topo_name_map_file_path[topo_name]
    
    topo = Topology(adjust_factor=adjust_factor_in)
    # topo.import_fiber_from_file(file_path)
    topo.import_lease_from_file(file_path)
    topo.import_l3_node_from_file(file_path)
    topo.import_l3_link_from_file(file_path)
    topo.import_tm_from_file(file_path)
    topo.import_spof_from_file(file_path)
    
    topo.gen_failed_ip_link_and_spof_map()
    topo.generate_delta_bw_matrix_from_spof_list()

    return topo

# single data point, used for Figure 8
# support ILP, First-stage and Second-stage
def single_dp_fig8(alg, adjust_factor_in=1, load_trained=True):
    print(f'\n========== Fig8 start, A-{adjust_factor_in}, alg:{alg} ==========\n')
                                
    if alg == "ILP":
        ilp_solver = ILP(topo=read_topo("A", adjust_factor_in=adjust_factor_in))
        ilp_solver.run_ilp()
        print(f'========== Topo: A-{adjust_factor_in}, result: {ilp_solver.cost_opt} =========\n')
    # elif alg == "NeuroPlan":
    #     if load_trained:
    #         if int(adjust_factor_in) == adjust_factor_in:
    #             af_file_name = int(adjust_factor_in)
    #         else:
    #             af_file_name = adjust_factor_in
    #         model_path = f'results/trained/A-{af_file_name}/'
    #         if af_file_name == 1:
    #             model_path = f'results/trained/A/'
    #         if os.path.exists(model_path + "pyt_save/model.pt") == False:
    #             model_path = None
    #     else:
    #         model_path = None
    #     print(f'\n========== Fig8, RL: Topo: A-{adjust_factor_in}, load pre-trained model: {model_path} ==========\n')
    #     rl_solver = RL(topo=read_topo("A", adjust_factor_in=adjust_factor_in), model_path=model_path, num_gnn_layer=2, max_n_delta_bw=1)
    #     rl_solver.run_training()
    #     print(f'========== first stage result: {rl_solver.env.opt_target} =========\n')
    #     subopt_sol = rl_solver.env.ip_idx_map_num_step
    #     print(f'\n========== ILP on second stage: adjust_factor_in:{adjust_factor_in} ==========\n')
    #     ilp_solver = ILP(topo=read_topo("A", adjust_factor_in=adjust_factor_in))
    #     ilp_solver.run_ilp(subopt_sol=subopt_sol, relax_factor=1.5)
    #     print(f'========== second stage, adjust_factor_in: {adjust_factor_in}, result: {ilp_solver.cost_opt} =========\n')
    else:
        print("Illegal args")

# single data point, used for Figure 9
# support ILP, ILP-huer and First-stage
def single_dp_fig9(topo_name, alg, adjust_factor_in=1.0, load_trained=True):
    print(f'\n========== start: topo_name:{topo_name} alg:{alg} adjust_factor_in:{adjust_factor_in}==========\n')
                                
    if alg == "ILP":
        ilp_solver = ILP(topo=read_topo(topo_name, adjust_factor_in=adjust_factor_in))
        ilp_solver.run_ilp()
        print(f'========== result: {ilp_solver.cost_opt} =========\n')
    elif alg == "ILP-heur":
        ilp_solver = ILP(topo=read_topo(topo_name))
        ilp_solver.run_ilp_heuristic()
        print(f'========== result: {ilp_solver.cost_opt} =========\n')
    elif alg == "NeuroPlan":
        if load_trained:
            model_path = f'results/trained/{topo_name}/'
            if os.path.exists(model_path + "pyt_save/model.pt") == False:
                model_path = None
        else:
            model_path = None
        print(f'\n========== RL: topo_name:{topo_name}, load pre-trained model: {model_path} ==========\n')
        rl_solver = RL(topo=read_topo(topo_name), model_path=model_path, num_gnn_layer=2, max_n_delta_bw=1)
        rl_solver.run_training()
        print(f'========== first stage result: {rl_solver.env.opt_target} =========\n')
    else:
        print("Illegal args")

# given the path of the sol form the first stage, run second stage
def second_stage(topo_name, sol_path, rf=1.0):

    with open(sol_path) as json_file:
        json_dict = json.load(json_file)
    subopt_sol = {}
    for k, v in json_dict.items():
        subopt_sol[int(k)] = v
    ilp_solver = ILP(topo=read_topo(topo_name))
    ilp_solver.run_ilp(subopt_sol=subopt_sol, relax_factor=rf)
    print(f'========== sol from the first stage: {subopt_sol} ============\n')
    print(f'========== second stage, topo_name: {topo_name}, rf: {rf}, result: {ilp_solver.cost_opt} =========\n')

# single data point, used for Figure 10, 11, 12
def params_rl(adjust_factor_in=1.0, num_gnn_layer=2, max_n_delta_bw=1, hidden_sizes=(256, 256)):
    print(f'\n========== start: adjust_factor_in:{adjust_factor_in} num_gnn_layer:{num_gnn_layer}, max_n_delta_bw:{max_n_delta_bw}, hidden_sizes:{hidden_sizes} ==========\n')
    
    rl_solver = RL(topo=read_topo("A", adjust_factor_in=adjust_factor_in), num_gnn_layer=num_gnn_layer, \
        max_n_delta_bw=max_n_delta_bw,hidden_sizes=hidden_sizes)
    rl_solver.run_training()
    print(f'\n========== end: adjust_factor_in:{adjust_factor_in} num_gnn_layer:{num_gnn_layer}, max_n_delta_bw:{max_n_delta_bw}, hidden_sizes:{hidden_sizes} ==========')
    print(f'result: {rl_solver.env.opt_target}')

if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "single_dp_fig8":
        if len(sys.argv)==5 and sys.argv[4]=="False":
            single_dp_fig8(sys.argv[2], float(sys.argv[3]), load_trained=False)
        else:
            single_dp_fig8(sys.argv[2], float(sys.argv[3]), load_trained=True)
    else:
        print("Illegal args")
    
