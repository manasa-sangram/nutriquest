import json
import os
from datetime import date

# -----------------------------------------------------------
# CONFIG — tweak these numbers whenever you like
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(BASE_DIR, "progress.json")


XP_PER_GOAL_LOG = 50          # XP awarded each time the user logs a goal

# Total XP needed to *reach* each level (level 1 starts at 0)
LEVEL_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
}

LEVEL_TITLES = {
    1: "Nutrition Newbie",
    2: "Calorie Counter",
    3: "Macro Master",
    4: "Health Hero",
    5: "NutriQuest Legend",
}

# Badge definitions — id: {label, description, secret check key}
ALL_BADGES = {
    "first_log":    {"label": "First Log",       "desc": "Logged your first daily goal"},
    "streak_3":     {"label": "3-Day Streak",     "desc": "Logged goals 3 days in a row"},
    "streak_7":     {"label": "Week Warrior",     "desc": "Logged goals 7 days in a row"},
    "level_3":      {"label": "Macro Master",     "desc": "Reached Level 3"},
    "level_5":      {"label": "NutriQuest Legend","desc": "Reached Level 5 — the top!"},
}


# -----------------------------------------------------------
# LOAD / SAVE  (simple JSON file on disk)
# -----------------------------------------------------------

def load_progress():
    """Read progress.json from disk. Returns a fresh dict if file doesn't exist."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)

    # Brand-new player — return default state
    return {
        "xp":             0,
        "level":          1,
        "streak":         0,
        "last_log_date":  None,   # "YYYY-MM-DD" string or None
        "badges":         [],     # list of badge ids the player has earned
        "total_logs":     0,
        "grocery_history": [],    # list of raw grocery text strings (last 10 kept)
    }


def save_progress(progress):
    """Write progress dict back to disk."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# -----------------------------------------------------------
# LEVEL HELPER
# -----------------------------------------------------------

def xp_to_level(xp):
    """Return the level (1-5) that matches a given XP total."""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level


def xp_for_next_level(current_level):
    """How much XP is needed to reach the *next* level (or None if already max)."""
    next_lvl = current_level + 1
    return LEVEL_THRESHOLDS.get(next_lvl, None)


# -----------------------------------------------------------
# STREAK HELPER
# -----------------------------------------------------------

def update_streak(progress):
    """
    Call this once per day when the user logs a goal.
    Increments streak if they logged yesterday, resets if they missed a day,
    leaves it alone if they already logged today.
    Returns the updated progress dict (also modifies it in-place).
    """
    today_str = str(date.today())           # e.g. "2025-06-01"
    last = progress.get("last_log_date")

    if last == today_str:
        # Already logged today — don't double-count
        return progress

    if last is not None:
        # Work out how many days since last log
        from datetime import datetime
        last_date = datetime.strptime(last, "%Y-%m-%d").date()
        gap = (date.today() - last_date).days
        if gap == 1:
            progress["streak"] += 1   # consecutive day — keep the streak
        else:
            progress["streak"] = 1    # missed a day — reset streak to 1
    else:
        progress["streak"] = 1        # very first log ever

    progress["last_log_date"] = today_str
    return progress


# -----------------------------------------------------------
# MAIN FUNCTION  —  call this when the user hits "Goal Met"
# -----------------------------------------------------------

def on_daily_goal_met(progress, protein_met=True):
    """
    Award XP, update streak, check for level-up, check for new badges.

    Parameters
    ----------
    progress    : dict returned by load_progress()
    protein_met : bool — True if the user hit their protein goal today
                  (you can add carbs_met, fibre_met etc. later)

    Returns
    -------
    new_badges : list of badge ids earned this session (empty list if none)
    """

    # 1 — Award XP
    if protein_met:
        progress["xp"] += XP_PER_GOAL_LOG
    progress["total_logs"] += 1

    # 2 — Update streak
    update_streak(progress)

    # 3 — Check level
    progress["level"] = xp_to_level(progress["xp"])

    # 4 — Check badges
    new_badges = check_badges(progress)

    # 5 — Save to disk
    save_progress(progress)

    return new_badges   # caller can show these to the user


# -----------------------------------------------------------
# BADGE CHECKER
# -----------------------------------------------------------

def save_grocery_entry(progress, raw_text):
    """
    Add a grocery list string to the history (keeps the last 10).
    Call this each time the user successfully analyses a list.
    """
    history = progress.get("grocery_history", [])
    history.append(raw_text)
    progress["grocery_history"] = history[-10:]   # keep only the last 10
    save_progress(progress)


def check_badges(progress):
    """
    Look at the current progress state and award any badges the player
    hasn't earned yet but now qualifies for.
    Returns a list of newly-earned badge ids.
    """
    earned     = set(progress["badges"])
    new_badges = []

    # first_log — awarded after the very first log
    if "first_log" not in earned and progress["total_logs"] >= 1:
        new_badges.append("first_log")

    # streak_3 — 3 consecutive days
    if "streak_3" not in earned and progress["streak"] >= 3:
        new_badges.append("streak_3")

    # streak_7 — 7 consecutive days
    if "streak_7" not in earned and progress["streak"] >= 7:
        new_badges.append("streak_7")

    # level_3 — reached level 3
    if "level_3" not in earned and progress["level"] >= 3:
        new_badges.append("level_3")

    # level_5 — reached level 5 (max)
    if "level_5" not in earned and progress["level"] >= 5:
        new_badges.append("level_5")

    # Add newly earned badges to the master list
    progress["badges"].extend(new_badges)

    return new_badges

# -----------------------------------------------
# Run this directly to test:  python progress.py
# -----------------------------------------------
if __name__ == "__main__":
    print(f"Saving to: {PROGRESS_FILE}")

    p = load_progress()
    print(f"Loaded — XP: {p['xp']}, Level: {p['level']}, Streak: {p['streak']}")

    # Simulate 6 goal logs on different days
    for day in range(1, 7):
        p["last_log_date"] = f"2025-01-0{day}"   # fake different dates
        new_badges = on_daily_goal_met(p, protein_met=True)
        print(f"  Day {day} → XP: {p['xp']}, Level: {p['level']}, "
              f"Streak: {p['streak']}, New badges: {new_badges}")

    print(f"\nFinal state: {p}")
    print(f"File saved to: {PROGRESS_FILE}")