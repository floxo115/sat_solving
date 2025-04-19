from itertools import product
from time import perf_counter
from glob import glob

import sys
import os
sys.path.append(os.path.abspath("../"))

from dimacs_reader import DIMACSReader

class Solver:
    def __init__(self, num_variables, clauses, timeout=float("inf")):
        self.num_variables = num_variables
        self.clauses = clauses
        self.model = []

        self.timeout = timeout

    def solve(self):
        start_time = perf_counter()
        for assignment in  product([0,1], repeat=self.num_variables):
            if perf_counter() - start_time > self.timeout:
                raise TimeoutError()
            for clause in self.clauses:
                clause_val = False
                for literal in clause:
                    val = bool(assignment[literal[1]])
                    if literal[0] == -1:
                        val = not val
                    if val is True:
                        clause_val = True
                        break
                
                if clause_val is False:
                    break
            else:
                self.model = assignment
                return True
        return False

def main():
    files = glob("../test-formulas/*.in")
    for file in files:
        print(f"solving file {file}")
        dimacs_reader = DIMACSReader()
        dimacs_reader.read(file)

        solver = Solver(dimacs_reader.num_vars, dimacs_reader.clauses, timeout=5)
        try:
            is_sat = solver.solve()
            print(is_sat)
            print(solver.model)
        except TimeoutError:
            print("timeout")
        print()



if __name__ == "__main__":
    main()
