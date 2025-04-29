from glob import glob


from dimacs_reader import DIMACSReader
from first_part import SimpleSolver
from second_part import DLPPSolver


def main():
    files = glob("./test-formulas/*.in")
    for file in files:
        print(f"solving file {file}", flush=True)
        dimacs_reader = DIMACSReader()
        dimacs_reader.read(file)

        try:
            solver1 = SimpleSolver(dimacs_reader.clauses, timeout=10)
            print("solver1 ...")
            is_sat1 = solver1.solve()
            print(is_sat1)
            print(solver1.get_model())
            print(solver1.get_num_decisions())
        except TimeoutError:
            print("solver1 timeout")
        try:
            print()
            print("solver2 ...")
            solver2 = DLPPSolver(dimacs_reader.get_clauses(), timeout=10)
            is_sat2 = solver2.solve()
            print(is_sat2)
            print(solver2.get_model())
            print(solver2.get_num_decisions())
        except TimeoutError:
            print("solver2 timeout")
        print()


if __name__ == "__main__":
    print("starting solver")
    main()
