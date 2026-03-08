# ============================================================
#  student_analytics.py
#  Student Performance Analytics Module
#  Uses: *args, **kwargs, type hints, Google docstrings,
#        defaultdict, closures, edge case handling
# ============================================================

from collections import defaultdict
from typing import Optional


# ─────────────────────────────────────────────────────────────
#  GRADE BOUNDARIES
# ─────────────────────────────────────────────────────────────
GRADE_BOUNDARIES: dict[str, tuple[float, float]] = {
    "A": (80.0, 100.0),
    "B": (65.0,  79.9),
    "C": (50.0,  64.9),
    "D": (0.0,   49.9),
}


def _letter_grade(avg: float) -> str:
    """Return letter grade for a given average score."""
    for grade, (low, high) in GRADE_BOUNDARIES.items():
        if low <= avg <= high:
            return grade
    return "D"


# ─────────────────────────────────────────────────────────────
#  1. create_student
# ─────────────────────────────────────────────────────────────

def create_student(name: str, roll: str, **marks: float) -> dict:
    """
    Create a standardised student record dict.

    Args:
        name:    Full name of the student.
        roll:    Unique roll number (e.g. 'R001').
        **marks: Subject marks as keyword arguments
                 (e.g. math=85, python=92, ml=78).

    Returns:
        A dict with keys: 'name', 'roll', 'marks', 'attendance'.
        'attendance' defaults to 100.0 unless supplied as a keyword arg.
        'marks' only stores numeric values; non-numeric entries are ignored.

    Raises:
        ValueError: If name or roll is an empty string.

    Example:
        >>> create_student('Amit', 'R001', math=85, python=92, ml=78)
        {'name': 'Amit', 'roll': 'R001', 'marks': {'math': 85, 'python': 92, 'ml': 78},
         'attendance': 100.0}
    """
    if not name or not name.strip():
        raise ValueError("Student name cannot be empty.")
    if not roll or not roll.strip():
        raise ValueError("Roll number cannot be empty.")

    # Separate attendance from subject marks
    attendance = float(marks.pop("attendance", 100.0))
    attendance = max(0.0, min(100.0, attendance))    # clamp to [0, 100]

    # Keep only numeric marks; discard invalid entries
    clean_marks: dict[str, float] = {
        subject: float(score)
        for subject, score in marks.items()
        if isinstance(score, (int, float)) and 0 <= score <= 100
    }

    return {
        "name":       name.strip(),
        "roll":       roll.strip(),
        "marks":      clean_marks,
        "attendance": attendance,
    }


# ─────────────────────────────────────────────────────────────
#  2. calculate_gpa
# ─────────────────────────────────────────────────────────────

def calculate_gpa(*marks: float, scale: float = 10.0) -> float:
    """
    Calculate GPA from any number of subject marks.

    Args:
        *marks: Variable number of numeric mark values (0–100).
        scale:  The GPA scale ceiling (default 10.0).
                Pass scale=4.0 for a US-style GPA.

    Returns:
        Rounded GPA on the given scale, or 0.0 if no marks provided.

    Raises:
        ValueError: If scale is not positive.

    Example:
        >>> calculate_gpa(85, 92, 78)
        8.5
        >>> calculate_gpa(85, 92, 78, scale=4.0)
        3.4
    """
    if scale <= 0:
        raise ValueError(f"Scale must be positive, got {scale}.")
    if not marks:
        return 0.0

    valid = [m for m in marks if isinstance(m, (int, float)) and 0 <= m <= 100]
    if not valid:
        return 0.0

    avg = sum(valid) / len(valid)
    gpa = round((avg / 100.0) * scale, 2)
    return gpa


# ─────────────────────────────────────────────────────────────
#  3. get_top_performers
# ─────────────────────────────────────────────────────────────

def get_top_performers(
    students: list[dict],
    n: int = 5,
    subject: Optional[str] = None,
) -> list[dict]:
    """
    Return the top-n performing students.

    Args:
        students: List of student dicts (as created by create_student).
        n:        Number of top students to return (default 5).
        subject:  If provided, rank by that subject's mark.
                  If None, rank by overall average across all subjects.

    Returns:
        Sorted list of up to n student dicts (best first).
        Returns [] for empty input or n <= 0.

    Example:
        >>> get_top_performers(students, n=1, subject='python')
        [{'name': 'Amit', ...}]
    """
    if not students or n <= 0:
        return []

    def _score(student: dict) -> float:
        marks: dict = student.get("marks", {})
        if not marks:
            return 0.0
        if subject:
            return float(marks.get(subject, 0.0))
        return sum(marks.values()) / len(marks)

    sorted_students = sorted(students, key=_score, reverse=True)
    return sorted_students[:n]


# ─────────────────────────────────────────────────────────────
#  4. generate_report
# ─────────────────────────────────────────────────────────────

def generate_report(student: dict, **options) -> str:
    """
    Generate a formatted performance report string for a student.

    Args:
        student: A student dict (as created by create_student).
        **options: Display options:
            include_rank  (bool, default True)  — show overall rank label.
            include_grade (bool, default True)  — show letter grade.
            verbose       (bool, default False) — show per-subject marks.

    Returns:
        A multi-line formatted string report.
        Returns an error string if student dict is empty or None.

    Example:
        >>> print(generate_report(student, include_grade=True, verbose=True))
        ╔══════════════════════════════╗
        ...
    """
    if not student:
        return "Error: No student data provided."

    include_rank  = options.get("include_rank",  True)
    include_grade = options.get("include_grade", True)
    verbose       = options.get("verbose",       False)

    name       = student.get("name", "Unknown")
    roll       = student.get("roll", "N/A")
    marks      = student.get("marks", {})
    attendance = student.get("attendance", 0.0)

    avg = sum(marks.values()) / len(marks) if marks else 0.0
    gpa = calculate_gpa(*marks.values()) if marks else 0.0

    lines: list[str] = [
        "╔══════════════════════════════════════╗",
        f"  Student Report",
        f"  Name       : {name}",
        f"  Roll No.   : {roll}",
        f"  Attendance : {attendance:.1f}%",
        f"  Average    : {avg:.2f} / 100",
        f"  GPA        : {gpa:.2f} / 10.0",
    ]

    if include_grade:
        lines.append(f"  Grade      : {_letter_grade(avg)}")

    if include_rank:
        rank_label = (
            "🏆 Distinction" if avg >= 80 else
            "✅ First Class" if avg >= 65 else
            "📘 Second Class" if avg >= 50 else
            "⚠️  Needs Improvement"
        )
        lines.append(f"  Status     : {rank_label}")

    if verbose and marks:
        lines.append("  ─────────── Marks ───────────")
        for subject, score in sorted(marks.items()):
            bar = "█" * int(score // 10)
            lines.append(f"  {subject:<10} : {score:>5.1f}  {bar}")

    lines.append("╚══════════════════════════════════════╝")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
#  5. classify_students
# ─────────────────────────────────────────────────────────────

def classify_students(students: list[dict]) -> dict[str, list[dict]]:
    """
    Classify students into grade bands A / B / C / D.

    Uses defaultdict(list) to collect students under each grade.
    Classification is based on overall average across all marks.

    Args:
        students: List of student dicts.

    Returns:
        Dict with keys 'A', 'B', 'C', 'D', each mapping to a list
        of student dicts in that band.  Empty lists are included for
        bands with no students.

    Example:
        >>> result = classify_students(students)
        >>> result['A']
        [{'name': 'Priya', ...}]
    """
    result: defaultdict[str, list[dict]] = defaultdict(list)

    # Ensure all grade keys exist even if empty
    for grade in GRADE_BOUNDARIES:
        result[grade]   # touch to initialise

    for student in students:
        marks = student.get("marks", {})
        avg   = sum(marks.values()) / len(marks) if marks else 0.0
        grade = _letter_grade(avg)
        result[grade].append(student)

    return dict(result)


# ─────────────────────────────────────────────────────────────
#  DEMO
# ─────────────────────────────────────────────────────────────

def _demo() -> None:
    students = [
        create_student("Amit",    "R001", math=85, python=92, ml=78, attendance=95.0),
        create_student("Priya",   "R002", math=95, python=88, ml=91, attendance=98.0),
        create_student("Rahul",   "R003", math=60, python=55, ml=63, attendance=80.0),
        create_student("Sneha",   "R004", math=72, python=68, ml=75, attendance=92.0),
        create_student("Dev",     "R005", math=40, python=48, ml=35, attendance=70.0),
        create_student("Aisha",   "R006", math=88, python=91, ml=85, attendance=99.0),
        create_student("Karan",   "R007", math=55, python=60, ml=58, attendance=85.0),
    ]

    print("\n── Top 3 Overall ──")
    for s in get_top_performers(students, n=3):
        m = s["marks"]
        avg = sum(m.values()) / len(m)
        print(f"  {s['name']:<10} avg={avg:.1f}")

    print("\n── Top 2 in Python ──")
    for s in get_top_performers(students, n=2, subject="python"):
        print(f"  {s['name']:<10} python={s['marks'].get('python')}")

    print("\n── Classification ──")
    for grade, group in sorted(classify_students(students).items()):
        names = [s["name"] for s in group]
        print(f"  {grade}: {names}")

    print("\n── GPA examples ──")
    print(f"  calculate_gpa(85, 92, 78)          = {calculate_gpa(85, 92, 78)}")
    print(f"  calculate_gpa(85, 92, 78, scale=4) = {calculate_gpa(85, 92, 78, scale=4.0)}")
    print(f"  calculate_gpa()                    = {calculate_gpa()}")

    print("\n── Sample Report (verbose) ──")
    print(generate_report(students[1], verbose=True, include_grade=True, include_rank=True))


if __name__ == "__main__":
    _demo()
