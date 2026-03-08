# ============================================================
#  test_analytics.py  —  Comprehensive test suite
# ============================================================

import sys
from student_analytics import (
    create_student, calculate_gpa,
    get_top_performers, generate_report, classify_students,
)

passed = 0
failed = 0

def test(name: str, condition: bool):
    global passed, failed
    if condition:
        print(f"  ✅  {name}")
        passed += 1
    else:
        print(f"  ❌  {name}")
        failed += 1

def test_raises(name: str, exc_type, fn):
    global passed, failed
    try:
        fn()
        print(f"  ❌  {name}  → expected {exc_type.__name__} but none raised")
        failed += 1
    except exc_type:
        print(f"  ✅  {name}")
        passed += 1
    except Exception as e:
        print(f"  ❌  {name}  → wrong exception: {type(e).__name__}: {e}")
        failed += 1

# ── Fixtures ──────────────────────────────────────────────────
amit  = create_student("Amit",  "R001", math=85, python=92, ml=78, attendance=95.0)
priya = create_student("Priya", "R002", math=95, python=88, ml=91, attendance=98.0)
rahul = create_student("Rahul", "R003", math=60, python=55, ml=63, attendance=80.0)
dev   = create_student("Dev",   "R005", math=40, python=48, ml=35, attendance=70.0)
ALL   = [amit, priya, rahul, dev]

# ── create_student ────────────────────────────────────────────
print("\n── create_student ──────────────────────────────────────")
test("required keys present",     set(amit.keys()) == {"name","roll","marks","attendance"})
test("name stored correctly",     amit["name"] == "Amit")
test("roll stored correctly",     amit["roll"] == "R001")
test("marks is a dict",           isinstance(amit["marks"], dict))
test("marks captured via **kwargs", amit["marks"] == {"math":85.0,"python":92.0,"ml":78.0})
test("attendance separated from marks", "attendance" not in amit["marks"] and amit["attendance"]==95.0)

s_no_att = create_student("X","R999",math=70)
test("attendance defaults to 100.0", s_no_att["attendance"] == 100.0)

s_clamp = create_student("X","R999",math=70,attendance=150.0)
test("attendance clamped to 100.0", s_clamp["attendance"] == 100.0)

test_raises("ValueError on empty name",  ValueError, lambda: create_student("","R001",math=80))
test_raises("ValueError on empty roll",  ValueError, lambda: create_student("Name","",math=80))

s_bad = create_student("X","R999",math=80,subject="abc")
test("non-numeric marks excluded",  "subject" not in s_bad["marks"] and "math" in s_bad["marks"])

s_oor = create_student("X","R999",math=150)
test("out-of-range marks excluded",  "math" not in s_oor["marks"])

s_ws = create_student("  Ravi  ","  R010  ",math=70)
test("whitespace trimmed",  s_ws["name"]=="Ravi" and s_ws["roll"]=="R010")


# ── calculate_gpa ─────────────────────────────────────────────
print("\n── calculate_gpa ───────────────────────────────────────")
test("(85+92+78)/3 = 85 → 8.5",   calculate_gpa(85,92,78) == 8.5)
test("single mark 100 → 10.0",    calculate_gpa(100) == 10.0)
test("all zeros → 0.0",           calculate_gpa(0,0,0) == 0.0)
test("no args → 0.0",             calculate_gpa() == 0.0)
test("scale=4.0 correct",         calculate_gpa(85,92,78,scale=4.0) == 3.4)
test("perfect on scale 4.0",      calculate_gpa(100,100,scale=4.0) == 4.0)
test_raises("ValueError scale=0", ValueError, lambda: calculate_gpa(80,scale=0))
test_raises("ValueError scale<0", ValueError, lambda: calculate_gpa(80,scale=-1))


# ── get_top_performers ────────────────────────────────────────
print("\n── get_top_performers ──────────────────────────────────")
top1 = get_top_performers(ALL, n=1)
test("returns list",              isinstance(top1, list))
test("top 1 overall is Priya",    top1[0]["name"] == "Priya")
test("n=2 returns exactly 2",     len(get_top_performers(ALL,n=2)) == 2)

top_py = get_top_performers(ALL, n=1, subject="python")
test("top by python is Amit(92)", top_py[0]["name"] == "Amit")

top_ma = get_top_performers(ALL, n=1, subject="math")
test("top by math is Priya(95)",  top_ma[0]["name"] == "Priya")

test("empty list → []",           get_top_performers([],n=3) == [])
test("n=0 → []",                  get_top_performers(ALL,n=0) == [])
test("n>len returns all",         len(get_top_performers(ALL,n=100)) == len(ALL))
test("unknown subject returns n", len(get_top_performers(ALL,n=2,subject="xyz")) == 2)


# ── generate_report ───────────────────────────────────────────
print("\n── generate_report ─────────────────────────────────────")
report = generate_report(priya)
test("returns string",            isinstance(report, str))
test("contains name",             "Priya" in report)
test("contains roll",             "R002" in report)
test("grade shown when flag=True",any(g in generate_report(priya,include_grade=True) for g in "ABCD"))

v_report = generate_report(amit, verbose=True)
test("verbose shows subject names", "math" in v_report.lower() or "python" in v_report.lower())

nv_report = generate_report(amit, verbose=False)
test("non-verbose hides bars",    "█" not in nv_report)

test("empty dict → error string", "error" in generate_report({}).lower() or "Error" in generate_report({}))
test("None → error string",       "error" in generate_report(None).lower() or "Error" in generate_report(None))


# ── classify_students ─────────────────────────────────────────
print("\n── classify_students ───────────────────────────────────")
cls = classify_students(ALL)
test("keys are A B C D",          set(cls.keys()) == {"A","B","C","D"})
test("Priya(avg≈91) in A",        any(s["name"]=="Priya" for s in cls["A"]))
test("Dev(avg≈41) in D",          any(s["name"]=="Dev" for s in cls["D"]))
test("total count preserved",     sum(len(v) for v in cls.values()) == len(ALL))

empty_cls = classify_students([])
test("empty input → all bands empty", all(len(v)==0 for v in empty_cls.values()))
test("all keys present on empty",     set(empty_cls.keys()) == {"A","B","C","D"})

single_cls = classify_students([priya])
test("all keys present with 1 student", set(single_cls.keys()) == {"A","B","C","D"})

ghost = {"name":"Ghost","roll":"R000","marks":{},"attendance":100.0}
ghost_cls = classify_students([ghost])
test("no-marks student falls into D",   any(x["name"]=="Ghost" for x in ghost_cls["D"]))


# ── Summary ───────────────────────────────────────────────────
total = passed + failed
print(f"\n{'═'*50}")
print(f"  Results: {passed}/{total} passed  |  {failed} failed")
print(f"{'═'*50}\n")
if failed:
    sys.exit(1)
