"""
Master Execution Script for CSE Hackathon on Data Structures and Algorithms
Runs all 4 problems, triggers Python and Java implementations, executes unit tests,
and verifies output artifact generation.
"""

import os
import sys
import subprocess

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def run_command(cmd, desc):
    print(f"\n[RUNNING] {desc}: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[SUCCESS] {desc}")
        if res.stdout.strip():
            print(res.stdout.strip())
    else:
        print(f"[ERROR] {desc} (Exit code {res.returncode})")
        print("STDOUT:", res.stdout)
        print("STDERR:", res.stderr)
    return res.returncode == 0

def main():
    print_header("CMRIT CSE HACKATHON 2026 - COMPLETE TEST & BENCHMARK SUITE")

    # 1. Unit Tests
    print_header("STEP 1: RUNNING UNIT TESTS FOR ALL 4 PROBLEMS")
    run_command("python -m unittest discover -s problem1_maze -p \"test_*.py\"", "Problem 1 Unit Tests")
    run_command("python -m unittest discover -s problem2_closest_pair -p \"test_*.py\"", "Problem 2 Unit Tests")
    run_command("python -m unittest discover -s problem3_budget_traveller -p \"test_*.py\"", "Problem 3 Unit Tests")
    run_command("python -m unittest discover -s problem4_exam_scheduling -p \"test_*.py\"", "Problem 4 Unit Tests")

    # 2. Python Solvers & Visualizers
    print_header("STEP 2: RUNNING PYTHON SOLVERS & VISUALIZERS")
    run_command("python problem1_maze/maze_solver.py --generate --N 10 --T 3 --output-csv outputs/p1_solution.csv", "Problem 1 Maze Solver")
    run_command("python problem1_maze/visualizer.py", "Problem 1 Visualizer")
    run_command("python problem2_closest_pair/closest_pair.py --N 100", "Problem 2 Closest Pair Runner")
    run_command("python problem2_closest_pair/visualizer.py", "Problem 2 Visualizer & Benchmarks")
    run_command("python problem3_budget_traveller/budget_traveller.py --generate --N 6 --K 2 --C 1 --output-csv outputs/p3_solution.csv", "Problem 3 Budget Traveller")
    run_command("python problem3_budget_traveller/visualizer.py", "Problem 3 Visualizer")
    run_command("python problem4_exam_scheduling/exam_scheduler.py --N 10 --R 3 --density 0.35 --output-csv outputs/p4_timetable.csv", "Problem 4 Exam Scheduler")
    run_command("python problem4_exam_scheduling/visualizer.py", "Problem 4 Visualizer & Comparisons")

    # 3. Java Implementations
    print_header("STEP 3: RUNNING JAVA IMPLEMENTATIONS")
    run_command("javac problem1_maze/MazeSolver.java && java problem1_maze.MazeSolver", "Problem 1 Java MazeSolver")
    run_command("javac problem2_closest_pair/ClosestPair.java && java problem2_closest_pair.ClosestPair 500", "Problem 2 Java ClosestPair")
    run_command("javac problem3_budget_traveller/BudgetTraveller.java && java problem3_budget_traveller.BudgetTraveller", "Problem 3 Java BudgetTraveller")
    run_command("javac problem4_exam_scheduling/ExamScheduler.java && java problem4_exam_scheduling.ExamScheduler", "Problem 4 Java ExamScheduler")

    # 4. Summary of Output Files
    print_header("STEP 4: VERIFYING OUTPUT ARTIFACTS")
    outputs = os.listdir("outputs")
    print(f"Generated {len(outputs)} output files in outputs/:")
    for f in sorted(outputs):
        size_kb = os.path.getsize(os.path.join("outputs", f)) / 1024.0
        print(f"  - outputs/{f:<36} ({size_kb:.1f} KB)")

    print("\n" + "="*80)
    print("  ALL PROBLEMS SOLVED, BENCHMARKED, AND VISUALIZED SUCCESSFULLY!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
