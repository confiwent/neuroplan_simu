# c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` gurobi_c.cpp -o ../gurobi_c`python3-config --extension-suffix` -I/opt/gurobi902/linux64/include -L/opt/gurobi902/linux64/lib -lgurobi_c++ -lgurobi90

c++ -O3 -Wall -shared -std=c++11 -fPIC `python3 -m pybind11 --includes` gurobi_c_v2.cpp -o ../gurobi_c`python3-config --extension-suffix` -I/opt/gurobi902/linux64/include -L/opt/gurobi902/linux64/lib -lgurobi_c++ -lgurobi90
