with open("backend/app/services/advisor_agent.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_block = """        history_context = ""
        if history:
            recent_turns = [f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in history[-4:]]
            history_context = "RECENT CONVERSATION HISTORY:\\n" + "\\n".join(recent_turns) + "\\n\\n"

        current_profile_str = ""
        if existing_slots:
            current_profile_str = (
                f"CURRENT USER PROFILE: Segment: {existing_slots.segment or 'unknown'}, "
                f"City Tier: {existing_slots.city_tier or 'unknown'}, "
                f"Staff: {existing_slots.employee_count or 'unknown'}, "
                f"GSTIN: {existing_slots.has_gstin}, "
                f"Budget: ₹{existing_slots.monthly_budget_cap or 'unknown'}/mo, "
                f"Needs: {existing_slots.detected_needs}\\n\\n"
            )
"""

prefix = lines[:104]
suffix = lines[124:]
with open("backend/app/services/advisor_agent.py", "w", encoding="utf-8") as f:
    f.writelines(prefix)
    f.write(new_block)
    f.writelines(suffix)
print("Fixed lines in advisor_agent.py")
