"""
Emotional Resilience Psychological Survey
Fundamentals of Programming — 4BUIS008C
Flask Web Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
import re
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = "survey_secret_key_2024"

# ============================================================
# VARIABLE TYPES DEMONSTRATION
# ============================================================
SURVEY_TITLE: str = "Emotional Resilience Survey"           # str
QUESTION_COUNT: int = 20                                    # int
MAX_SCORE: float = 80.0                                     # float
SCORE_BANDS: tuple = (10, 20, 30, 40, 50, 60, 70)          # tuple
VALID_FORMATS: set = {"json", "csv", "txt"}                 # set
FROZEN_STATES: frozenset = frozenset({                      # frozenset
    "Excellent", "Good", "Moderate", "Low", "Critical"
})
ALLOWED_NAME_CHARS: str = r"^[A-Za-z\s\-']+$"             # str (regex)
RESULTS_FILE: str = "results.json"
QUESTIONS_FILE: str = "questions.json"
IS_DEBUG: bool = True                                       # bool
SCORE_RANGE: range = range(0, 81, 1)                       # range


# ============================================================
# LOAD QUESTIONS FROM EXTERNAL FILE
# ============================================================
def load_questions() -> list:
    """Load survey questions from external JSON file."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# INPUT VALIDATION FUNCTIONS
# ============================================================
def validate_name(name: str) -> tuple:
    """
    Validate full name using a for loop.
    Allows letters, spaces, hyphens, apostrophes.
    Returns (is_valid: bool, error_message: str)
    """
    if not name or not name.strip():
        return False, "Name cannot be empty."

    # FOR LOOP for input validation (requirement)
    for char in name:
        if not (char.isalpha() or char in (" ", "-", "'")):
            return False, f"Name contains invalid character: '{char}'. Only letters, spaces, hyphens, and apostrophes are allowed."

    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."

    return True, ""


def validate_student_id(student_id: str) -> tuple:
    """
    Validate student ID using a while loop.
    Only digits allowed.
    Returns (is_valid: bool, error_message: str)
    """
    if not student_id or not student_id.strip():
        return False, "Student ID cannot be empty."

    sid = student_id.strip()

    # WHILE LOOP for input validation (requirement)
    index: int = 0
    while index < len(sid):
        if not sid[index].isdigit():
            return False, f"Student ID must contain digits only. Found invalid character: '{sid[index]}'."
        index += 1

    if len(sid) < 3:
        return False, "Student ID must be at least 3 digits."

    return True, ""


def validate_dob(dob_str: str) -> tuple:
    """
    Validate date of birth format (YYYY-MM-DD) and logical values.
    Returns (is_valid: bool, error_message: str)
    """
    if not dob_str:
        return False, "Date of birth is required."

    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
    except ValueError:
        return False, "Date of birth must be in YYYY-MM-DD format."

    current_year: int = datetime.now().year

    if dob.year < 1900:
        return False, "Date of birth year must be 1900 or later."

    if dob > datetime.now():
        return False, "Date of birth cannot be in the future."

    age: int = current_year - dob.year
    if age < 5:
        return False, "Age must be at least 5 years."

    if age > 120:
        return False, "Please enter a valid date of birth."

    return True, ""


# ============================================================
# SCORE INTERPRETATION
# ============================================================
def get_psychological_state(score: int) -> dict:
    """
    Map total score to one of 6 psychological states.
    Returns a dict with state name, description, color, and advice.
    """
    # Conditional statements: if / elif / elif / elif / elif / else
    if score <= 13:
        return {
            "state": "Excellent Resilience",
            "emoji": "🌟",
            "color": "#10b981",
            "description": "You demonstrate outstanding emotional resilience and psychological well-being.",
            "advice": "Continue your positive habits. Consider mentoring others or sharing your coping strategies."
        }
    elif score <= 26:
        return {
            "state": "Good Psychological Balance",
            "emoji": "😊",
            "color": "#3b82f6",
            "description": "You are in a good psychological state with healthy coping mechanisms.",
            "advice": "Maintain your current routine. Small improvements can take you to an excellent level."
        }
    elif score <= 39:
        return {
            "state": "Moderate Resilience",
            "emoji": "🙂",
            "color": "#f59e0b",
            "description": "You show moderate resilience but may experience occasional emotional challenges.",
            "advice": "Consider mindfulness practices, journaling, or talking to a trusted friend regularly."
        }
    elif score <= 52:
        return {
            "state": "Reduced Well-being",
            "emoji": "😐",
            "color": "#f97316",
            "description": "You are experiencing reduced emotional well-being and may benefit from support.",
            "advice": "Prioritize self-care. Speaking with a counselor or therapist could be very beneficial."
        }
    elif score <= 65:
        return {
            "state": "Low Resilience",
            "emoji": "😟",
            "color": "#ef4444",
            "description": "Your psychological state indicates low resilience and possible emotional distress.",
            "advice": "We strongly recommend seeking professional psychological support or counseling."
        }
    else:
        return {
            "state": "Critical State",
            "emoji": "🆘",
            "color": "#7f1d1d",
            "description": "Your responses indicate significant psychological distress requiring immediate attention.",
            "advice": "Please reach out to a mental health professional or crisis helpline immediately."
        }


# ============================================================
# FILE PERSISTENCE — SAVE & LOAD RESULTS (JSON)
# ============================================================
def save_result(result_data: dict) -> bool:
    """Save a single result to results.json (appends to array)."""
    existing: list = []

    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing.append(result_data)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    return True


def load_results() -> list:
    """Load all saved results from results.json."""
    if not os.path.exists(RESULTS_FILE):
        return []

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            data: list = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return []


# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    """Home page — choose to start new survey or load existing results."""
    return render_template("index.html", title=SURVEY_TITLE)


@app.route("/start", methods=["GET", "POST"])
def start():
    """User info page with full input validation."""
    errors: dict = {}

    if request.method == "POST":
        name: str = request.form.get("name", "").strip()
        dob: str = request.form.get("dob", "").strip()
        student_id: str = request.form.get("student_id", "").strip()

        # Validate all fields
        name_valid, name_err = validate_name(name)
        dob_valid, dob_err = validate_dob(dob)
        sid_valid, sid_err = validate_student_id(student_id)

        if not name_valid:
            errors["name"] = name_err
        if not dob_valid:
            errors["dob"] = dob_err
        if not sid_valid:
            errors["student_id"] = sid_err

        if not errors:
            session["name"] = name
            session["dob"] = dob
            session["student_id"] = student_id
            return redirect(url_for("survey"))

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("start.html", errors=errors, title=SURVEY_TITLE, now=today)


@app.route("/survey", methods=["GET"])
def survey():
    """Display the survey questions."""
    if "name" not in session:
        return redirect(url_for("start"))

    questions: list = load_questions()
    return render_template(
        "survey.html",
        questions=questions,
        total=len(questions),
        title=SURVEY_TITLE,
        name=session.get("name")
    )


@app.route("/submit", methods=["POST"])
def submit():
    """Process submitted answers, compute score, save to JSON."""
    if "name" not in session:
        return redirect(url_for("start"))

    questions: list = load_questions()
    total_score: int = 0
    answers: list = []
    missing: list = []

    # FOR LOOP to process all answers
    for i in range(len(questions)):
        answer = request.form.get(f"q{i}")
        if answer is None:
            missing.append(i + 1)
        else:
            score_val: int = int(answer)
            total_score += score_val
            answers.append(score_val)

    if missing:
        questions = load_questions()
        return render_template(
            "survey.html",
            questions=questions,
            total=len(questions),
            title=SURVEY_TITLE,
            name=session.get("name"),
            error=f"Please answer all questions. Missing: Q{', Q'.join(map(str, missing))}"
        )

    state_info: dict = get_psychological_state(total_score)

    # Build result record with all required data types used
    result_data: dict = {
        "name": session.get("name"),                        # str
        "date_of_birth": session.get("dob"),                # str
        "student_id": session.get("student_id"),            # str
        "score": total_score,                               # int
        "max_score": int(MAX_SCORE),                        # int from float
        "percentage": round((total_score / MAX_SCORE) * 100, 2),  # float
        "state": state_info["state"],                       # str
        "answers": answers,                                 # list
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # str
        "question_count": QUESTION_COUNT,                   # int
        "valid_formats": list(VALID_FORMATS),               # from set
    }

    save_result(result_data)

    # Store in session for result page
    session["result"] = result_data
    session["state_info"] = state_info

    return redirect(url_for("result"))


@app.route("/result")
def result():
    """Display the result page."""
    if "result" not in session:
        return redirect(url_for("index"))

    result_data: dict = session["result"]
    state_info: dict = session["state_info"]

    return render_template(
        "result.html",
        result=result_data,
        state=state_info,
        max_score=int(MAX_SCORE),
        title=SURVEY_TITLE
    )


@app.route("/history")
def history():
    """Load and display all saved results from JSON file."""
    all_results: list = load_results()
    return render_template(
        "history.html",
        results=all_results,
        title=SURVEY_TITLE
    )


@app.route("/api/results")
def api_results():
    """JSON API endpoint returning all results."""
    return jsonify(load_results())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=IS_DEBUG)
