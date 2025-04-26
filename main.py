from glob import glob


from dimacs_reader import DIMACSReader
from first_part import SimpleSolver
from second_part import DLPPSolver


def main():
    files = glob("./test-formulas/*.in")
    for file in files:
        print(f"solving file {file}")
        dimacs_reader = DIMACSReader()
        dimacs_reader.read(file)

        solver = SimpleSolver(dimacs_reader.num_vars, dimacs_reader.clauses, timeout=5)
        solver = DLPPSolver(dimacs_reader.get_clauses(), timeout=5)
        try:
            is_sat = solver.solve()
            print(is_sat)
            print(solver.model)
        except TimeoutError:
            print("timeout")
        print()


if __name__ == "__main__":
    print("starting solver")
    main()
