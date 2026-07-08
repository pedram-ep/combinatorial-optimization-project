from pathlib import Path
from typing import Any, Dict
import pyomo.environ as pyo

from ..data_loader import _normalize_data
from .base import _build_common_components, _score_lists

def build_model(data: Dict[str, Any] | str | Path, formulation: str = "SO-BB") -> pyo.ConcreteModel:
    """
    Build one formulation as a Pyomo model.
    """
    data = _normalize_data(data)
    model = pyo.ConcreteModel()
    _build_common_components(model, data)

    if formulation == "SO-BB":
        return _build_so_bb(model, data)
    if formulation == "SO-NW-CUT":
        return _build_so_nw_cut(model, data)
    if formulation == "MIN-CUT":
        return _build_min_cut(model, data)
    if formulation == "MSMR-CUT":
        return _build_msmr_cut(model, data)
    if formulation == "SO-NW-BIN-CUT":
        return _build_so_nw_bin_cut(model, data)
    if formulation == "MIN-BIN-CUT":
        return _build_min_bin_cut(model, data)
    if formulation == "MSMR-BIN-CUT":
        return _build_msmr_bin_cut(model, data)
    if formulation == "MSMR-EF":
        return _build_msmr_ef(model, data)
    raise ValueError(f"Unsupported formulation: {formulation}")

def _build_so_bb(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    """
    SO-BB: Student-Optimal Baïou-Balinski formulation.
    """
    def baiou_balinski_rule(model, i, j):
        rank_ij = model.r[i, j]
        preferred_or_equal = sum(
            model.x[i, h]
            for (ii, h) in model.E
            if ii == i and model.r[ii, h] <= rank_ij
        )
        higher_score = sum(
            model.x[h, j]
            for (h, j2) in model.E
            if j2 == j and model.s[h, j] > model.s[i, j]
        )
        return preferred_or_equal * model.u[j] + higher_score >= model.u[j]

    model.StabilityConstraint = pyo.Constraint(model.E, rule=baiou_balinski_rule)

    def objective(model):
        return sum(model.r[i, j] * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.minimize)
    return model


def _build_so_nw_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    scores = data["scores"]
    big_m = max(scores.values()) + 2
    epsilon = 1e-6

    model.t = pyo.Var(model.C, within=pyo.NonNegativeReals, bounds=(0, big_m))
    model.f = pyo.Var(model.C, within=pyo.Binary)

    def cutoff_upper(model, i, j):
        return model.t[j] <= (1 - model.x[i, j]) * (big_m + 1) + model.s[i, j]

    def cutoff_lower(model, i, j):
        rank_ij = model.r[i, j]
        prefix = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        return model.s[i, j] + epsilon <= model.t[j] + prefix * (big_m + 1)

    def reject_indicator(model, j):
        return model.u[j] * model.f[j] <= sum(model.x[i, j2] for (i, j2) in model.E if j2 == j)

    def cutoff_zero_if_no_reject(model, j):
        return model.t[j] <= model.f[j] * (big_m + 1)

    model.CutoffUpper = pyo.Constraint(model.E, rule=cutoff_upper)
    model.CutoffLower = pyo.Constraint(model.E, rule=cutoff_lower)
    model.RejectIndicator = pyo.Constraint(model.C, rule=reject_indicator)
    model.CutoffZeroIfNoReject = pyo.Constraint(model.C, rule=cutoff_zero_if_no_reject)

    def objective(model):
        return sum(model.r[i, j] * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.minimize)
    return model


def _build_min_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    scores = data["scores"]
    big_m = max(scores.values()) + 2
    epsilon = 1e-6

    model.t = pyo.Var(model.C, within=pyo.NonNegativeReals, bounds=(0, big_m))

    def cutoff_upper(model, i, j):
        return model.t[j] <= (1 - model.x[i, j]) * (big_m + 1) + model.s[i, j]

    def cutoff_lower(model, i, j):
        rank_ij = model.r[i, j]
        prefix = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        return model.s[i, j] + epsilon <= model.t[j] + prefix * (big_m + 1)

    model.CutoffUpper = pyo.Constraint(model.E, rule=cutoff_upper)
    model.CutoffLower = pyo.Constraint(model.E, rule=cutoff_lower)

    def objective(model):
        return sum(model.t[j] for j in model.C)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.minimize)
    return model


def _build_msmr_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    scores = data["scores"]
    big_m = max(scores.values()) + 2
    epsilon = 1e-6
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    model.t = pyo.Var(model.C, within=pyo.NonNegativeReals, bounds=(0, big_m))

    def cutoff_upper(model, i, j):
        return model.t[j] <= (1 - model.x[i, j]) * (big_m + 1) + model.s[i, j]

    def cutoff_lower(model, i, j):
        rank_ij = model.r[i, j]
        prefix = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        return model.s[i, j] + epsilon <= model.t[j] + prefix * (big_m + 1)

    model.CutoffUpper = pyo.Constraint(model.E, rule=cutoff_upper)
    model.CutoffLower = pyo.Constraint(model.E, rule=cutoff_lower)

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)
    return model


def _build_so_nw_bin_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    scores_by_college = _score_lists(data)
    score_pairs = [(j, score) for j in range(data["m"]) for score in scores_by_college[j]]
    model.TS = pyo.Set(initialize=score_pairs, dimen=2)
    model.t = pyo.Var(model.TS, within=pyo.Binary)

    def cutoff_ge_accept(model, i, j):
        sc = model.s[i, j]
        return model.x[i, j] <= model.t[j, sc]

    def monotonicity(model, j):
        score_list = scores_by_college[j]
        exprs = []
        for k in range(len(score_list) - 1):
            exprs.append(model.t[j, score_list[k]] <= model.t[j, score_list[k + 1]])
        return exprs

    def envy_rule(model, i, j):
        rank_ij = model.r[i, j]
        sum_x = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        sc = model.s[i, j]
        return 1 <= sum_x + (1 - model.t[j, sc])

    def lower_bound_rule(model, j):
        score_list = scores_by_college[j]
        if not score_list:
            return pyo.Constraint.Skip
        return (1 - model.t[j, score_list[0]]) * model.u[j] <= sum(model.x[i, j2] for (i, j2) in model.E if j2 == j)

    model.CutoffGeAccept = pyo.Constraint(model.E, rule=cutoff_ge_accept)
    monotonicity_counter = 0
    for j in range(data["m"]):
        for expr in monotonicity(model, j):
            model.add_component(f"Monotonicity_{j}_{monotonicity_counter}", pyo.Constraint(expr=expr))
            monotonicity_counter += 1
    model.Envy = pyo.Constraint(model.E, rule=envy_rule)
    model.LowerBound = pyo.Constraint(model.C, rule=lower_bound_rule)

    def objective(model):
        return sum(model.r[i, j] * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.minimize)
    return model

def _build_min_bin_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    scores_by_college = _score_lists(data)
    score_pairs = [(j, score) for j in range(data["m"]) for score in scores_by_college[j]]
    model.TS = pyo.Set(initialize=score_pairs, dimen=2)
    model.t = pyo.Var(model.TS, within=pyo.Binary)

    def cutoff_ge_accept(model, i, j):
        sc = model.s[i, j]
        return model.x[i, j] <= model.t[j, sc]

    def monotonicity(model, j):
        score_list = scores_by_college[j]
        exprs = []
        for k in range(len(score_list) - 1):
            exprs.append(model.t[j, score_list[k]] <= model.t[j, score_list[k + 1]])
        return exprs

    def envy_rule(model, i, j):
        rank_ij = model.r[i, j]
        sum_x = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        sc = model.s[i, j]
        return 1 <= sum_x + (1 - model.t[j, sc])

    model.CutoffGeAccept = pyo.Constraint(model.E, rule=cutoff_ge_accept)
    monotonicity_counter = 0
    for j in range(data["m"]):
        for expr in monotonicity(model, j):
            model.add_component(f"Monotonicity_{j}_{monotonicity_counter}", pyo.Constraint(expr=expr))
            monotonicity_counter += 1
    model.Envy = pyo.Constraint(model.E, rule=envy_rule)

    def objective(model):
        return sum(model.t[j, sc] for (j, sc) in model.TS)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)
    return model


def _build_msmr_bin_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    scores_by_college = _score_lists(data)
    score_pairs = [(j, score) for j in range(data["m"]) for score in scores_by_college[j]]
    model.TS = pyo.Set(initialize=score_pairs, dimen=2)
    model.t = pyo.Var(model.TS, within=pyo.Binary)

    def cutoff_ge_accept(model, i, j):
        sc = model.s[i, j]
        return model.x[i, j] <= model.t[j, sc]

    def monotonicity(model, j):
        score_list = scores_by_college[j]
        exprs = []
        for k in range(len(score_list) - 1):
            exprs.append(model.t[j, score_list[k]] <= model.t[j, score_list[k + 1]])
        return exprs

    def envy_rule(model, i, j):
        rank_ij = model.r[i, j]
        sum_x = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        sc = model.s[i, j]
        return 1 <= sum_x + (1 - model.t[j, sc])

    model.CutoffGeAccept = pyo.Constraint(model.E, rule=cutoff_ge_accept)
    monotonicity_counter = 0
    for j in range(data["m"]):
        for expr in monotonicity(model, j):
            model.add_component(f"Monotonicity_{j}_{monotonicity_counter}", pyo.Constraint(expr=expr))
            monotonicity_counter += 1
    model.Envy = pyo.Constraint(model.E, rule=envy_rule)

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)
    return model


def _build_msmr_ef(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    # Envy-free constraint: for each college j, for each pair (i,h) with score_i >= score_h
    def envy_free_rule(model, i, j, h):
        # Ensure we only create constraints when both applications exist
        if (i, j) not in model.E or (h, j) not in model.E:
            return pyo.Constraint.Skip
        if model.s[i, j] < model.s[h, j]:
            return pyo.Constraint.Skip
        # sum over k with rank <= rank_ij
        rank_ij = model.r[i, j]
        sum_x = sum(model.x[i, k] for (ii, k) in model.E if ii == i and model.r[ii, k] <= rank_ij)
        return sum_x >= model.x[h, j]

    # We'll create a set of triples (i, j, h) for which the constraint applies.
    # To avoid huge index sets, we loop over all (i,j) and all (h,j) and add constraints conditionally.
    # We'll use a ConstraintList for simplicity.
    model.EnvyConstraints = pyo.ConstraintList()
    for (i, j) in model.E:
        for (h, j2) in model.E:
            if j2 == j and model.s[i, j] >= model.s[h, j]:
                rank_ij = model.r[i, j]
                sum_x = sum(model.x[i, k] for (ii, k) in model.E if ii == i and model.r[ii, k] <= rank_ij)
                model.EnvyConstraints.add(sum_x >= model.x[h, j])

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)
    return model