from pathlib import Path
from typing import Any, Dict, Iterable, List
import pyomo.environ as pyo
import tempfile
import os

def extract_assignment(
        model: pyo.ConcreteModel,
        data: Dict[str, Any] | None = None
        )-> Dict[int, int | None]:
    if data is None:
        data = {"preferences": {i: [] for i in range(len(model.A))}}
    preferences = data.get("preferences", {})
    assignment = {}
    for i in range(len(preferences)):
        assigned = None
        for j in preferences.get(i, []):
            try:
                if pyo.value(model.x[i, j]) > 0.5:
                    assigned = j
                    break
            except ValueError:
                break
        assignment[i] = assigned
    return assignment

def summarize_results(
        results: Dict[str, Dict[str, Any]]
        ) -> List[Dict[str, Any]]:
    rows = []
    for formulation, info in results.items():
        model = info["model"]
        instance = info["instance"]
        assignment = extract_assignment(model, instance)
        admitted = [j for j in assignment.values() if j is not None]
        college_loads = {j: sum(1 for assigned in assignment.values() if assigned == j) for j in range(instance["m"])}
        try:
            rank_objective = sum(instance["preferences"][i].index(assignment[i]) for i in range(instance["n"]) if assignment[i] is not None)
            model_objective = pyo.value(model.Objective)
        except (ValueError, TypeError):
            rank_objective = None
            model_objective = None
        rows.append(
            {
                "model": formulation,
                "status": info["status"],
                "model_objective": model_objective,
                "rank_objective": rank_objective,
                "students_assigned": len(admitted),
                "college_loads": college_loads,
                "assignments": assignment,
            }
        )
    return rows

def print_summary(
        rows: Iterable[Dict[str, Any]]
        ) -> None:
    for row in rows:
        print(f"{row['model']}: status={row['status']}, model_objective={row['model_objective']}, rank_objective={row['rank_objective']}, assigned={row['students_assigned']}")
        print("  college loads:", row["college_loads"])
        print("  assignments:", row["assignments"])
        print()

def solve_and_summarize_all(
        data: Dict[str, Any] | str | Path,
        solver_name: str = "cplex",
        tee: bool = False,
        formulations: List[str] | None = None
        ) -> List[Dict[str, Any]]:
    """
    Convenience wrapper to solve all formulations and return comparable summaries.
    """
    from .solver import solve_all_models
    return summarize_results(solve_all_models(data, solver_name=solver_name, tee=tee, formulations=formulations))

def compute_metrics(assignment, data):
    """Compute fairness and satisfaction metrics from an assignment."""
    preferences = data['preferences']
    n = data['n']
    m = data['m']
    
    matched = [i for i in range(n) if assignment[i] is not None]
    unmatched = [i for i in range(n) if assignment[i] is None]
    
    college_loads = {}
    for j in range(m):
        college_loads[j] = sum(1 for assigned in assignment.values() if assigned == j)
    
    ranks_achieved = []
    for i in matched:
        j = assignment[i]
        rank = preferences[i].index(j)
        ranks_achieved.append(rank)
    
    avg_rank = sum(ranks_achieved) / len(ranks_achieved) if ranks_achieved else None
    max_rank = max(ranks_achieved) if ranks_achieved else None
    
    return {
        'num_matched': len(matched),
        'num_unmatched': len(unmatched),
        'college_loads': college_loads,
        'avg_preference_rank': avg_rank,
        'max_preference_rank': max_rank,
        'total_rank_objective': sum(ranks_achieved)
    }

def display_solution(formulation_name, model, data):
    """
    Display solution details for a single formulation.
    """
    print(f"\n{'='*60}")
    print(f"Formulation: {formulation_name}")
    print(f"{'='*60}")
    
    assignment = extract_assignment(model, data)
    metrics = compute_metrics(assignment, data)
    
    try:
        obj_value = pyo.value(model.Objective)
        print(f"Objective value: {obj_value:.2f}")
    except:
        print(f"Objective value: NOT AVAILABLE")
    
    print(f"Students matched: {metrics['num_matched']}/{data['n']}")
    print(f"Unmatched students: {metrics['num_unmatched']}")
    print(f"Average preference rank: {metrics['avg_preference_rank']:.2f}" if metrics['avg_preference_rank'] else "N/A")
    print(f"Max preference rank: {metrics['max_preference_rank']}" if metrics['max_preference_rank'] else "N/A")
    print(f"Total rank objective: {metrics['total_rank_objective']}")
    print(f"College loads: {metrics['college_loads']}")
    print(f"Assignments: {assignment}")
    
    return metrics

def get_model_stats(model):
    """
    Return a dict with:
        num_vars: total number of variables
        num_constraints: total number of constraints (including block constraints)
        size_kb: size of the LP file in KB
    """
    # variables
    num_vars = 0
    for var in model.component_objects(pyo.Var, active=True):
        num_vars += len(var)

    # constraints
    num_constraints = 0
    for con in model.component_objects(pyo.Constraint, active=True):
        if con.is_indexed():
            num_constraints += len(con)
        else:
            num_constraints += 1

    # write LP file to temp and get its size
    with tempfile.NamedTemporaryFile(suffix='.lp', delete=False) as f:
        temp_filename = f.name
    try:
        model.write(temp_filename, format='lp')
        size_kb = os.path.getsize(temp_filename) / 1024.0
    finally:
        os.remove(temp_filename)

    return {
        'num_vars': num_vars,
        'num_constraints': num_constraints,
        'size_kb': size_kb,
    }

def break_ties_randomly(data):
    import copy, random
    new_data = copy.deepcopy(data)
    new_scores = {}
    for (i,j), score in data['scores'].items():
        new_scores[(i,j)] = score + random.random() * 1e-5
    new_data['scores'] = new_scores
    return new_data

def compute_policy_metrics(model, data):
    """
    Compute metrics for a given model and data, similar to paper's table 4.
    Returns a dict with:
        size:        number of students assigned
        avg_rank:    average rank of assigned students
        avg_cutoffs: average cutoff scores for colleges (if applicable)
        rejections:  number of applications rejected (student not matched)
    """
    # 1. Size & Ranks
    size = 0
    rank_sum = 0
    for (i, j) in model.E:
        if pyo.value(model.x[i, j]) > 0.5:
            size += 1
            rank_sum += pyo.value(model.r[i, j])

    avg_rank = rank_sum / size if size > 0 else 0

    # 2. Rejections: total students - matched students
    rejections = data['n'] - size

    # 3. Average Cutoffs
    cutoffs = []
    for j in range(data['m']):
        assigned_scores = []
        for (i, col) in model.E:
            if col == j and pyo.value(model.x[i, j]) > 0.5:
                assigned_scores.append(data['scores'][(i, j)])
        if assigned_scores:
            cutoff = min(assigned_scores)
        else:
            cutoff = 0
        cutoffs.append(cutoff)

    avg_cutoffs = sum(cutoffs) / len(cutoffs) if cutoffs else 0

    return {
        'size': size,
        'avg_rank': avg_rank,
        'avg_cutoffs': avg_cutoffs,
        'rejections': rejections
    }