"""Location check for Gate 1 (deterministic rules over model-supplied geography).

Inputs, each with one job:
  requirements.yaml  JD FACTS: location, work_arrangement, hybrid_days,
                     relocation_support (as the JD states them).
  location.yaml      GEOGRAPHY, judged by the model: drive minutes from home,
                     nearest listed metro, minutes from that metro's core, and a
                     borderline flag.
  preferences.yaml   THRESHOLDS, set by the candidate: commute radii, hybrid day
                     limit, relocation metros, metro reach, package rule.

Result: pass | open-question | trip | not-evaluated. A trip fires Gate 1 on its
own, independent of the skill-gap tally. An open-question never trips; it must
appear in the report's Open Questions. Rules, in order:

  1. no preferences file                      -> not-evaluated (never a silent pass)
  2. remote                                   -> pass
  3. location or arrangement unstated         -> open-question
  4. borderline (model's judgment)            -> open-question
  5. within the on-site commute radius        -> pass
  6. hybrid within the hybrid radius:
       days stated and <= the limit           -> pass
       days unstated                          -> open-question (conservative:
                                                 cannot tell hybrid from near-daily)
  7. in a listed metro, within its reach:
       no package required, or offered        -> pass
       relocation support unstated            -> open-question
       relocation explicitly not offered      -> trip
  8. anything else                            -> trip

The commute is checked BEFORE the metros: Columbus can be both a hybrid commute
and a relocation metro, and a commute needs no relocation package.
"""
from __future__ import annotations

ARRANGEMENTS = {"remote", "hybrid", "onsite", "unstated"}
RELOCATION = {"offered", "not-offered", "unstated"}


def _result(result: str, reason: str) -> dict:
    return {"result": result, "reason": reason}


def evaluate(requirements: dict, assessment: dict | None, prefs: dict | None) -> dict:
    if prefs is None:
        return _result("not-evaluated", "no preferences.yaml; location was not checked")

    arrangement = requirements.get("work_arrangement") or "unstated"
    if arrangement not in ARRANGEMENTS:
        raise ValueError(f"unknown work_arrangement {arrangement!r}; expected one of {sorted(ARRANGEMENTS)}")
    relocation = requirements.get("relocation_support") or "unstated"
    if relocation not in RELOCATION:
        raise ValueError(f"unknown relocation_support {relocation!r}; expected one of {sorted(RELOCATION)}")

    if arrangement == "remote":
        return _result("pass", "remote role")
    if arrangement == "unstated" or not requirements.get("location"):
        return _result("open-question", "JD does not state the location or work arrangement; ask the recruiter")

    if assessment is None:
        raise ValueError("a non-remote role needs location.yaml (the location assessment)")
    where = requirements["location"]
    if assessment.get("borderline"):
        note = assessment.get("notes") or "edge case"
        return _result("open-question", f"{where}: borderline ({note}); confirm with the recruiter")

    commute = prefs["commute"]
    drive = assessment.get("drive_minutes_from_home")
    if drive is not None:
        if drive <= commute["onsite_max_minutes"]:
            return _result("pass", f"{where}: ~{drive} min from home, within the on-site commute")
        if arrangement == "hybrid" and drive <= commute["hybrid_max_minutes"]:
            days = requirements.get("hybrid_days")
            if days is None:
                return _result(
                    "open-question",
                    f"{where}: ~{drive} min from home, within the hybrid radius only; "
                    "office days not stated, ask how many",
                )
            if days <= commute["hybrid_max_days_per_week"]:
                return _result("pass", f"{where}: hybrid {days} days/week, ~{drive} min from home")

    reloc = prefs["relocation"]
    metro = assessment.get("nearest_metro")
    if metro is not None and metro not in reloc["metros"]:
        raise ValueError(
            f"location.yaml nearest_metro {metro!r} is not a listed metro "
            f"{reloc['metros']}; use an exact name or null"
        )
    metro_minutes = assessment.get("metro_minutes")
    in_metro = (
        reloc["open"]
        and metro is not None
        and metro_minutes is not None
        and metro_minutes <= reloc["metro_reach_minutes"]
    )
    if in_metro:
        label = f"{where}: in the {metro} metro (~{metro_minutes} min from its core)"
        if not reloc["requires_paid_package"] or relocation == "offered":
            return _result("pass", f"{label}, relocation acceptable")
        if relocation == "unstated":
            return _result("open-question", f"{label}; JD is silent on relocation support, ask the recruiter")
        return _result("trip", f"{label}, but the JD says relocation is not supported")

    return _result("trip", f"{where}: outside the commute radius and every relocation metro")
