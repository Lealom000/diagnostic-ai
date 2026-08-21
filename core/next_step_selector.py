"""Deterministic ranking of recommended information-gathering steps."""
from __future__ import annotations

_DISCRIMINATING_POWER_RANK={"high":0,"medium":1,"low":2}
_COST_RISK_RANK={"low":0,"medium":1,"high":2}

def _bucket(entry:dict)->int:
    if entry.get("tier")==0:return 0
    if entry.get("eliminates_dangerous_diagnosis"):return 1
    if entry.get("discriminating_power")=="high":return 2
    if entry.get("cost_risk")=="low":return 3
    if entry.get("resolves_contradiction"):return 4
    return 5

def _sort_key(entry:dict)->tuple:
    return (_bucket(entry),_DISCRIMINATING_POWER_RANK.get(entry.get("discriminating_power"),3),_COST_RISK_RANK.get(entry.get("cost_risk"),3))

def rank_next_steps(missing_information:list[dict])->list[dict]:
    return sorted((dict(entry,status="recommended_only") for entry in missing_information),key=_sort_key)
