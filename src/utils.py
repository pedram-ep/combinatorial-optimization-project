from pathlib import Path
from typing import Any, Dict, Iterable, List
import pyomo.environ as pyo

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
        solver_name: str = "glpk",
        tee: bool = False
        ) -> List[Dict[str, Any]]:
    """
    Convenience wrapper to solve all formulations and return comparable summaries.
    """
    from .solver import solve_all_models
    return summarize_results(solve_all_models(data, solver_name=solver_name, tee=tee))
