from pathlib import Path
from typing import Any, Dict
import pyomo.environ as pyo

from .models.formulations import build_model
from .data_loader import _normalize_data

def solve_model(
        data: Dict[str, Any] | str | Path,
        formulation: str = "SO-BB",
        solver_name: str = "glpk",
        tee: bool = False):
    """
    solve a single formulation and return the model and a compact solution summary.
    """
    instance = _normalize_data(data)
    model = build_model(instance, formulation=formulation)
    solver = pyo.SolverFactory(solver_name)
    result = solver.solve(model, tee=tee)
    status = str(result.solver.termination_condition).lower()
    return {
        "model": model,
        "instance": instance,
        "formulation": formulation,
        "status": status,
        "result": result,
    }


def solve_all_models(
        data: Dict[str, Any] | str | Path,
        solver_name: str = "glpk", tee: bool = False
        ) -> Dict[str, Dict[str, Any]]:
    """
    solve all the models and return the results for all of them as a dictionary
    """
    instance = _normalize_data(data)
    formulations = ["SO-BB", "SO-NW-CUT", "MIN-CUT", "MSMR-CUT", "SO-NW-BIN-CUT"]
    results = {}
    for formulation in formulations:
        solved = solve_model(instance, formulation=formulation, solver_name=solver_name, tee=tee)
        results[formulation] = solved
    return results