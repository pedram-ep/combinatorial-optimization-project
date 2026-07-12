# Solving College Admissions at Scale: An Integer Programming Approach

Implementing mathematical optimization models to fairly assign students to colleges when traditional matching algorithms fail real-world complex scenatios like tied scores and shared capacity constraints.

**Implementation of Sections 1-4** from the paper *"College admissions with ties and common quotas: Integer programming approach"* by Kolos Csaba Ágoston, Péter Biró, Endre Kováts, Zsuzsanna Jankó.

**Coursework for**: Combinatorial Optimization and Network Analysis (Dr. Farnaz Hooshmand Khaligh)

## Problem Description

College admissions systems must match students to universities fairly while respecting preferences and constraints. The classic Gale-Shapley algorithm (1962) finds stable matchings efficiently—but it breaks down in real systems like Hungary's, which have:

1. **Tied Scores** (Ties): When multiple students have identical scores, how do you decide who gets admitted?
   - Should all tied students be admitted, rejected, or decided by lottery?
   - Different policies have different fairness properties

2. **Shared Capacity Constraints** (Common Quotas): Multiple universities may compete for shared resources (e.g., limited faculty or government-funded slots)
   - Makes the problem NP-hard
   - Cannot be solved by the greedy deferred-acceptance algorithm

**The Challenge**: Design efficient integer programming (IP) formulations that handle these constraints and enable policy comparison.

## Implementations

### Dataset Generation

To test the later implemented models, we generate a random dataset of students, colleges, and applications. Students each have a score for each college, along with a list of preferences, and colleges have a upper quote for the number of students they can accept. The script `scripts/generate_datasets.py` uses the functions defined on `src/generator.py` to generates synthetic instances at three scales:

- **Small**: 10 applicants, 5 colleges
- **Medium**: 50 applicants, 20 colleges  
- **Large**: 1,000 applicants, 20 colleges

There are two king of datasets, the strict datasets artificially avoids students having same rank for a college. The datasets are finally stored as `.json` files and they can be loaded using functions in `src/data_loaders.py`.

The formulations are then compared based on:
- Solution quality (objective value)
- Computational time
- Stability guarantees
- Student satisfaction metrics

### Integer Programming Formulations

Implemented twleve differen IP and MIP formulations with different constraints and objectives:

- **SO-BB** (Student-Optimal Baïou-Balinski)
- **SO-NW-CUT** and **SO-NW-BIN-CUT**
- **MIN-CUT** and **MIN-BIN-CUT**
- **MSMR-CUT** and **MSMR-BIN-CUT**
- **MSMR-EF**
- **SO-H-NW-CUT** and **SO-H-NW-BIN-CUT**
- **SO-C-NW-CUT** and **SO-C-NW-BIN-CUT**

These formulations are implemented as `pyomo` models, with a base function containing the basic variables, parameters, and constraints. Each formulation uses the base function and adds objective function, new variables and constraints to it. The full implementations are available in `src/models/` directory.

Each formulation is solved using CPLEX (with fallback to open-source solvers).

## Repository Structure

```text
notebooks/
  ├── Complete-Notebook.ipynb      # Whole project codes and results, submission file for project
  ├── sec2_gale_shapley.ipynb      # All results for paper's Section 2
  ├── sec3_tie_formulations.ipynb  # All results for paper's Section 3
  └── sec4_policy_comaprison.ipynb # All results for paper's Section 4
reports/
  ├── photos/                      # all images used in reports
  ├── optimization-models.md       # all 12 formulations as complete optimization 
  ├── paper-summary.md             # Persian summary of sections 1-4 of paper
  ├── project-report.md            # Persian report of whole project
  └── project-report.pdf           # PDF exported version of project report
scripts/
  └── generate_datasets.py         # script for generating dataset json files 
src/
  ├── models/
  │   ├── base.py                  # Common model components
  │   └── formulations.py          # Optimizaion formulations
  ├── solver.py                    # Solve single/multiple models
  ├── generator.py                 # Synthetic instance generation
  ├── data_loader.py               # Load and parse dataset instances
  └── utils.py                     # Metrics, analysis, and helper functions
```

## Results

The final results show similar results as original paper. Since the dataset used for this project was much smaller due to computional limits, some values don't have the exact proportions, but overall the solutions show similar results.

The most important insights about policy trade-offs:

- **H-stability** (Hungarian): Conservative acceptance, but guaranteed stability; fewer students matched
- **L-stability** (Chilean): Maximizes admissions but violates capacity constraints; less stable
- **Lottery** (Irish): Balances fairness and stability; randomness adds variance

Computational times scale linearly for small/medium instances; large instances (1,000 applicants) remain solvable within reasonable timeframes using modern IP solvers, especially using binary models which have more variables and constraints, but need less time to find the solution.

One other important result shows for finding a stable matching in large scale, even using student-pessimal methods will reach the same solutions, with possible little differents.

## Key Learnings

Through this project, I developed deep understanding of:

1. **Combinatorial Optimization Theory**
   - Matching algorithms and stability concepts
   - NP-hard problem recognition and IP formulation strategies
   - Trade-offs between solution quality and computational time

2. **Integer Programming Modeling**
   - Translating real constraints into mathematical formulations
   - Model comparisons for the same problem with different objectives and constraints
   - Using Pyomo and CPLEX in a large-scale project with multiple models

3. **Software Engineering for Research**
   - Designing modular programs for extensibility, instead of solely relying on Jupyter notebookes
   - Writing a reproducubile dataset generation code using seed control and scripts
   - Writing full documentation for both practitioners and researchers

## Requirements

How to install the project:

```bash
# cloning the repository
git clone <repo-url>
cd combinatorial-optimization-project

# installing dependencies
pip install -r requirements.txt
```

## License

This project is provided as-is for educational purposes under the MIT License. See LICENSE for details.
