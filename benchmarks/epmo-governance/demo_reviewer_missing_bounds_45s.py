#!/usr/bin/env python3
"""Short, fully fictional demonstration. No identities, private records, or external calls."""
from reviewer_missing_bounds_v12 import run


def main():
    out = run()
    print("FICTIONAL EPMO missing-outcome audit | 0 human reviewers | 0 external actions")
    for scenario in out["scenarios"]:
        c = scenario["contrast"]
        print(f"{scenario['scenario']}: completed manual={scenario['manual']['completed']}/48, "
              f"worksheet={scenario['worksheet']['completed']}/48")
        print(f"  naive complete-case worksheet-minus-manual={c['complete_case_difference']['decimal']}; "
              f"sharp assigned-reviewer bounds=[{c['assigned_difference_lower']['decimal']}, "
              f"{c['assigned_difference_upper']['decimal']}]; zero included={c['zero_in_identification_interval']}")
    print("These are finite-sample identification bounds, NOT confidence intervals or observed effects.")
    print("Next: consented private pilot protocol with assigned denominators and prespecified missingness analysis.")


if __name__ == "__main__":
    main()
