"""End-to-end ACHIX demo: paper analysis + transfer bridge in one run."""
import examples.qah_soc_paper as paper
import examples.sir_percolation as bridge


def main():
    print("\n### PART 1: paper analysis (ACHnX) ###\n")
    paper.main()
    print("\n\n### PART 2: transfer bridge (Level 5) ###\n")
    bridge.main()


if __name__ == "__main__":
    main()
