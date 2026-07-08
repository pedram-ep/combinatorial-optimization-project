import json
import random

def generate_instance(n, m, score_range=(0, 100), quota_factor=2, complete=True):
    """
    n: number of appliacants
    m: number of universities
    score_range: range of scores (min, max)
    quota_factor: factor for determining capacity (capacity = random between 1 and max(2, n//(m))*quota_factor)
    complete: if True, each applicant applies to all universities (complete list)
    """
    # generating quotas for each university
    quotas = {}
    max_quota = int(max(2, n // m) * quota_factor)
    for j in range(m):
        quotas[j] = random.randint(1, max_quota)
    
    # generating preferences and scores
    preferences = {}
    scores = {}
    for i in range(n):
        # list of universities
        if complete:
            colleges = list(range(m))
        else:
            k = max(1, int(m * 0.6))
            colleges = random.sample(range(m), k)
        random.shuffle(colleges)
        preferences[i] = colleges  # order of preference
        # generating scores for each university in the list
        for j in colleges:
            score = random.randint(score_range[0], score_range[1])
            scores[f"{i},{j}"] = score

    return {
        "n": n,
        "m": m,
        "preferences": preferences,
        "scores": scores,
        "quotas": quotas
    }

def save_instance(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)