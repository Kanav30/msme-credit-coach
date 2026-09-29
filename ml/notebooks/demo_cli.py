"""
Interactive demo tool for Phase 5 live testing sessions.

Run this on your laptop while sitting with a tester (business owner or CA).
Prompts for plain-language inputs matching docs/PHASE5_TESTING_KIT.md's
interview script, then prints a clean, human-readable report — no JSON,
no Swagger UI, nothing that assumes the tester is technical.

Run with: python demo_cli.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from feature_engineering import BusinessCreditProfile, generate_action_plan
from trajectory_simulator import predict_time_to_target


def ask_float(prompt, low=0.0, high=1.0):
    while True:
        try:
            val = float(input(prompt))
            if low <= val <= high:
                return val
            print(f"  Please enter a number between {low} and {high}.")
        except ValueError:
            print("  Please enter a number.")


def ask_yes_no(prompt):
    return input(prompt + " (y/n): ").strip().lower().startswith("y")


def ask_choice(prompt, choices):
    choices_str = "/".join(choices)
    while True:
        val = input(f"{prompt} ({choices_str}): ").strip().lower()
        if val in choices:
            return val
        print(f"  Please enter one of: {choices_str}")


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def score_bar(score, width=30):
    filled = int(score / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + f"] {score:.0f}/100"


def main():
    print_header("MSME Credit Score Improvement Coach — Live Demo")
    print("This is a college prototype. No documents or account access needed —")
    print("just your general sense of a few things. Answers stay on this laptop.\n")

    payment_pct = ask_float(
        "Roughly what fraction of payments were on time in the last year? (0.0-1.0): "
    )
    recent_delinquency = ask_yes_no("Any late payment in the last 2-3 months, even small?")
    utilization = ask_float(
        "Roughly what fraction of your available credit limit are you using? (0.0-1.0): "
    )
    tenure = float(input("How many years have you had a business loan/credit line? "))
    age = float(input("How many years has your business been operating? "))
    risk = ask_choice("Would you describe your industry as", ["low", "medium", "high"])
    target_rank = int(input("\nWhat CMR rank are you aiming for (1=best .. 10)? [default 3]: ") or 3)

    profile = BusinessCreditProfile(
        on_time_payment_pct=payment_pct,
        has_recent_delinquency=recent_delinquency,
        credit_utilization=utilization,
        credit_tenure_years=tenure,
        business_age_years=age,
        industry_risk_category=risk,
    )

    plan = generate_action_plan(profile, target_rank)

    print_header(f"Estimated CMR Rank: {plan['current_rank']}  (target: {target_rank})")
    print(f"Overall proxy score: {score_bar(plan['overall_score'])}")

    print("\nWhat's affecting your score, in priority order:\n")
    for i, factor in enumerate(plan["prioritized_factors"], 1):
        name = factor["factor"].replace("_", " ").title()
        print(f"{i}. {name}  {score_bar(factor['current_sub_score'])}")
        print(f"   Speed to improve: {factor['improvement_speed']}")
        print(f"   {factor['recommendation']}\n")

    if ask_yes_no("Want to see a projected timeline assuming consistent effort on all fixable factors?"):
        effort = {"credit_utilization": True, "payment_history": True}
        result = predict_time_to_target(profile, effort, target_rank)
        print_header("Projected Timeline")
        if result["target_reached"]:
            print(f"If you keep up consistent effort, you could reach rank {target_rank} "
                  f"in approximately {result['months_to_target']} months.")
        else:
            print(f"Target rank {target_rank} isn't projected within 24 months under this "
                  f"effort pattern — likely because a slow-moving factor (tenure/profile) is "
                  f"the main constraint. Worth discussing which factor is really holding this back.")
        print("\n(Reminder: this is a calibrated estimate from a student prototype, not a "
              "certified prediction — it's not validated against real historical CMR data.)")

    print_header("Thank you — please fill in the feedback log for this session")
    print("See docs/PHASE5_TESTING_KIT.md for the feedback questions to ask now.")


if __name__ == "__main__":
    main()
