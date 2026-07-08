from typing import Any, Dict, List, Tuple
import pyomo.environ as pyo

def _applications(data: Dict[str, Any]) -> List[Tuple[int, int]]:
    preferences = data["preferences"]
    n = data["n"]
    applications: List[Tuple[int, int]] = []
    for i in range(n):
        for j in preferences.get(i, []):
            applications.append((i, j))
    return applications

def _score_lists(data: Dict[str, Any]) -> Dict[int, List[int]]:
    scores = data["scores"]
    m = data["m"]
    score_sets: Dict[int, set[int]] = {j: set() for j in range(m)}
    for (i, j), value in scores.items():
        score_sets[j].add(value)
    return {j: sorted(score_sets[j]) for j in range(m)}

def _build_common_components(model: pyo.ConcreteModel, data: Dict[str, Any]) -> None:
    n = data["n"]
    m = data["m"]
    preferences = data["preferences"]
    scores = data["scores"]
    quotas = data["quotas"]

    model.A = pyo.Set(initialize=range(n))
    model.C = pyo.Set(initialize=range(m))
    model.E = pyo.Set(initialize=_applications(data), dimen=2)

    def rank_init(model, i, j):
        return preferences[i].index(j)

    def score_init(model, i, j):
        return scores[(i, j)]

    def quota_init(model, j):
        return quotas.get(j, 0)

    model.u = pyo.Param(model.C, initialize=quota_init, within=pyo.NonNegativeIntegers)
    model.r = pyo.Param(model.E, initialize=rank_init, within=pyo.NonNegativeIntegers)
    model.s = pyo.Param(model.E, initialize=score_init, within=pyo.NonNegativeIntegers)
    model.x = pyo.Var(model.E, within=pyo.Binary)

    def one_per_student(model, i):
        return sum(model.x[i, j] for (i2, j) in model.E if i2 == i) <= 1

    def capacity(model, j):
        return sum(model.x[i, j2] for (i, j2) in model.E if j2 == j) <= model.u[j]

    model.OnePerStudent = pyo.Constraint(model.A, rule=one_per_student)
    model.Capacity = pyo.Constraint(model.C, rule=capacity)