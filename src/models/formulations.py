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
    elif formulation == "SO-NW-CUT":
        return _build_so_nw_cut(model, data)
    elif formulation == "MIN-CUT":
        return _build_min_cut(model, data)
    elif formulation == "MSMR-CUT":
        return _build_msmr_cut(model, data)
    elif formulation == "SO-NW-BIN-CUT":
        return _build_so_nw_bin_cut(model, data)
    elif formulation == "MIN-BIN-CUT":
        return _build_min_bin_cut(model, data)
    elif formulation == "MSMR-BIN-CUT":
        return _build_msmr_bin_cut(model, data)
    elif formulation == "MSMR-EF":
        return _build_msmr_ef(model, data)
    elif formulation == "SO-H-NW-CUT":
        return _build_so_h_nw_cut(model, data)
    elif formulation == "SO-H-NW-BIN-CUT":
        return _build_so_h_nw_bin_cut(model, data)
    elif formulation == "SO-C-NW-CUT":
        return _build_so_c_nw_cut(model, data)
    elif formulation == "SO-C-NW-BIN-CUT":
        return _build_so_c_nw_bin_cut(model, data)
    else:
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

def _build_so_h_nw_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    """
    SO-H-NW-CUT: Student-Optimal Hungarian Non-Wasteful Cutoff (continuous).
    For ties under Hungarian policy.
    Variables: x (binary), t_j (continuous), f_j (binary), d_{ij} (binary).
    Constraints: (1),(2),(5),(6),(8),(17),(18),(19). Objective (10).
    """
    scores = data["scores"]
    big_m = max(scores.values()) + 2
    epsilon = 1e-6

    # Cutoff and reject indicator variables
    model.t = pyo.Var(model.C, within=pyo.NonNegativeReals, bounds=(0, big_m))
    model.f = pyo.Var(model.C, within=pyo.Binary)
    # d_{ij}: 1 if student i would be admitted to college j if cutoff decreased by one
    model.d = pyo.Var(model.E, within=pyo.Binary)

    # --- Cutoff constraints (5) and (6) ---
    def cutoff_upper(model, i, j):
        return model.t[j] <= (1 - model.x[i, j]) * (big_m + 1) + model.s[i, j]

    def cutoff_lower(model, i, j):
        rank_ij = model.r[i, j]
        prefix = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        return model.s[i, j] + epsilon <= model.t[j] + prefix * (big_m + 1)

    model.CutoffUpper = pyo.Constraint(model.E, rule=cutoff_upper)
    model.CutoffLower = pyo.Constraint(model.E, rule=cutoff_lower)

    # --- Constraint (8): cutoff zero if no rejection ---
    def cutoff_zero_if_no_reject(model, j):
        return model.t[j] <= model.f[j] * (big_m + 1)

    model.CutoffZeroIfNoReject = pyo.Constraint(model.C, rule=cutoff_zero_if_no_reject)

    # --- Constraint (17): d_{ik} <= 1 - x_{ij} for all i and all j,k with r_{ik} >= r_{ij} ---
    model.d_blocking_constraint = pyo.ConstraintList()
    for i in range(data["n"]):
        pref_i = data["preferences"][i]
        # For each college j that student applied to, and each k with rank >= rank_ij
        for rank_idx_j, j in enumerate(pref_i):
            for rank_idx_k, k in enumerate(pref_i):
                if rank_idx_k >= rank_idx_j:  # r_{ik} >= r_{ij}
                    # need (i,j) and (i,k) in E
                    if (i, j) in model.E and (i, k) in model.E:
                        model.d_blocking_constraint.add(
                            model.d[i, k] <= 1 - model.x[i, j]
                        )

    # --- Constraint (18)
    def d_cutoff_relation(model, i, j):
        return model.t[j] - 1 <= (1 - model.d[i, j]) * (big_m + 1) + model.s[i, j]

    model.DCutoffRelation = pyo.Constraint(model.E, rule=d_cutoff_relation)

    # --- Constraint (19)
    def non_wastefulness(model, j):
        return model.f[j] * (model.u[j] + 1) <= sum(
            model.x[i, j2] + model.d[i, j2]
            for (i, j2) in model.E
            if j2 == j
        )

    model.NonWastefulness = pyo.Constraint(model.C, rule=non_wastefulness)

    # --- Objective (10)
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)

    return model


def _build_so_h_nw_bin_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    """
    SO-H-NW-BIN-CUT: Student-Optimal Hungarian Non-Wasteful Binary Cutoff.
    For ties under Hungarian policy.
    Variables: x (binary), t_j^k (binary), d_{ij} (binary).
    Constraints: (1),(2),(11),(12),(13),(17),(20),(21). Objective (10).
    """
    scores_by_college = _score_lists(data)
    score_pairs = [(j, score) for j in range(data["m"]) for score in scores_by_college[j]]
    model.TS = pyo.Set(initialize=score_pairs, dimen=2)
    model.t = pyo.Var(model.TS, within=pyo.Binary)

    # d_{ij}: 1 if student i would be admitted to college j if cutoff decreased by one
    model.d = pyo.Var(model.E, within=pyo.Binary)

    # --- Cutoff constraints (11), (12), (13)
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

    # --- Constraint (17)
    model.d_blocking_constraint = pyo.ConstraintList()
    for i in range(data["n"]):
        pref_i = data["preferences"][i]
        for rank_idx_j, j in enumerate(pref_i):
            for rank_idx_k, k in enumerate(pref_i):
                if rank_idx_k >= rank_idx_j:
                    if (i, j) in model.E and (i, k) in model.E:
                        model.d_blocking_constraint.add(
                            model.d[i, k] <= 1 - model.x[i, j]
                        )

    # --- Constraint (21)
    model.d_cutoff_relation_bin = pyo.ConstraintList()
    for (i, j) in model.E:
        sc = model.s[i, j]
        score_list = scores_by_college[j]
        if sc in score_list:
            k = score_list.index(sc)
            if k < len(score_list) - 1:
                model.d_cutoff_relation_bin.add(
                    model.d[i, j] <= model.t[j, score_list[k+1]] - model.t[j, sc]
                )

    # --- Constraint (20)
    def non_wastefulness_bin(model, j):
        score_list = scores_by_college[j]
        if not score_list:
            return pyo.Constraint.Skip
        return (1 - model.t[j, score_list[0]]) * (model.u[j] + 1) <= sum(
            model.x[i, j2] + model.d[i, j2]
            for (i, j2) in model.E
            if j2 == j
        )

    model.NonWastefulnessBin = pyo.Constraint(model.C, rule=non_wastefulness_bin)

    # --- Objective (10)
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)

    return model


def _build_so_c_nw_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    """
    SO-C-NW-CUT: Student-Optimal Chilean Non-Wasteful Cutoff (continuous).
    Chilean permissive policy: last tied group is all accepted, possibly violating quota.
    Variables: x (binary), t_j (continuous), f_j (binary), dbar_{ij} (binary).
    Constraints: (1),(5),(6),(7),(8),(22),(23),(24). Objective (10) max.
    """
    scores = data["scores"]
    big_m = max(scores.values()) + 2
    epsilon = 1e-6

    # Cutoff and reject indicator variables (f_j)
    model.t = pyo.Var(model.C, within=pyo.NonNegativeReals, bounds=(0, big_m))
    model.f = pyo.Var(model.C, within=pyo.Binary)

    model.dbar = pyo.Var(model.E, within=pyo.Binary)

    # --- Constraints (5) and (6)
    def cutoff_upper(model, i, j):
        return model.t[j] <= (1 - model.x[i, j]) * (big_m + 1) + model.s[i, j]

    def cutoff_lower(model, i, j):
        rank_ij = model.r[i, j]
        prefix = sum(model.x[i, h] for (ii, h) in model.E if ii == i and model.r[ii, h] <= rank_ij)
        return model.s[i, j] + epsilon <= model.t[j] + prefix * (big_m + 1)

    model.CutoffUpper = pyo.Constraint(model.E, rule=cutoff_upper)
    model.CutoffLower = pyo.Constraint(model.E, rule=cutoff_lower)

    # --- Constraints (7) and (8)
    def reject_indicator(model, j):
        return model.u[j] * model.f[j] <= sum(model.x[i, j2] for (i, j2) in model.E if j2 == j)

    def cutoff_zero_if_no_reject(model, j):
        return model.t[j] <= model.f[j] * (big_m + 1)

    model.RejectIndicator = pyo.Constraint(model.C, rule=reject_indicator)
    model.CutoffZeroIfNoReject = pyo.Constraint(model.C, rule=cutoff_zero_if_no_reject)

    # --- Constraint (22)
    def dbar_le_x(model, i, j):
        return model.dbar[i, j] <= model.x[i, j]

    model.DbarLeX = pyo.Constraint(model.E, rule=dbar_le_x)

    # --- Constraint (23)
    def dbar_cutoff_relation(model, i, j):
        return (model.dbar[i, j] - 1) * (big_m + 1) + model.s[i, j] <= model.t[j]

    model.DbarCutoffRelation = pyo.Constraint(model.E, rule=dbar_cutoff_relation)

    # --- Constraint (24)
    def non_wastefulness_chile(model, j):
        return sum(model.x[i, j2] - model.dbar[i, j2] for (i, j2) in model.E if j2 == j) <= model.u[j] - 1

    model.NonWastefulnessChile = pyo.Constraint(model.C, rule=non_wastefulness_chile)

    # --- Objective (10)
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)

    # --- Deactivate capacity constraint (2)
    model.Capacity.deactivate()

    return model

def _build_so_c_nw_bin_cut(model: pyo.ConcreteModel, data: Dict[str, Any]) -> pyo.ConcreteModel:
    """
    SO-C-NW-BIN-CUT: Student-Optimal Chilean Non-Wasteful Binary Cutoff.
    Chilean permissive policy.
    Variables: x (binary), t_j^k (binary), dbar_{ij} (binary).
    Constraints: (1),(11),(12),(13),(22),(24),(25). Objective (10) max.
    """
    scores_by_college = _score_lists(data)
    score_pairs = [(j, score) for j in range(data["m"]) for score in scores_by_college[j]]
    model.TS = pyo.Set(initialize=score_pairs, dimen=2)
    model.t = pyo.Var(model.TS, within=pyo.Binary)

    # dbar_{ij}
    model.dbar = pyo.Var(model.E, within=pyo.Binary)

    # --- Constraints (11), (12), (13)
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

    # --- Constraint (22)
    def dbar_le_x(model, i, j):
        return model.dbar[i, j] <= model.x[i, j]

    model.DbarLeX = pyo.Constraint(model.E, rule=dbar_le_x)

    # --- Constraint (24)
    def non_wastefulness_chile_bin(model, j):
        return sum(model.x[i, j2] - model.dbar[i, j2] for (i, j2) in model.E if j2 == j) <= model.u[j] - 1

    model.NonWastefulnessChileBin = pyo.Constraint(model.C, rule=non_wastefulness_chile_bin)

    # --- Constraint (25)
    model.dbar_cutoff_bin = pyo.ConstraintList()
    for (i, j) in model.E:
        sc = model.s[i, j]
        score_list = scores_by_college[j]
        if sc in score_list:
            k = score_list.index(sc)
            if k == 0:
                model.dbar_cutoff_bin.add(model.dbar[i, j] <= model.t[j, sc])
            else:
                prev_score = score_list[k-1]
                model.dbar_cutoff_bin.add(model.dbar[i, j] <= model.t[j, sc] - model.t[j, prev_score])
    
    # --- Non-wastefulness constraint (14) equivalent for Chilean
    # --- Not in the paper
    def chilean_lower_bound(model, j):
        score_list = scores_by_college[j]
        if not score_list:
            return pyo.Constraint.Skip
        return (1 - model.t[j, score_list[0]]) * model.u[j] <= sum(
            model.x[i, j2] for (i, j2) in model.E if j2 == j
        )
    model.ChileanLowerBound = pyo.Constraint(model.C, rule=chilean_lower_bound)

    # --- Objective (10)
    max_rank = max(model.r[i, j] for (i, j) in model.E)
    K = max_rank + 1

    def objective(model):
        return sum((K - model.r[i, j]) * model.x[i, j] for (i, j) in model.E)

    model.Objective = pyo.Objective(rule=objective, sense=pyo.maximize)

    # --- Deactivate capacity constraint (2)
    model.Capacity.deactivate()

    return model
