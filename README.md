# CSE Hackathon on Data Structures and Algorithms
**Department of Computer Science and Engineering, CMRIT, Bangalore**  
**Date:** 14-OCT-2026

---

## 📋 Overview of Solutions

This repository provides complete, rigorously tested, and benchmarked solutions for all four hackathon problems in **both Python and Java**, complete with automated test suites, command-line interfaces, CSV input/output handling, Matplotlib/NetworkX visualizers, and a unified interactive Web Visualizer suite.

| Problem | Title | Primary Algorithm | Time Complexity | Space Complexity | Implementations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Problem 1** | Maze with Keys and Doors | State-Space BFS + Bitmasking | $O(N^2 \cdot 2^T)$ | $O(N^2 \cdot 2^T)$ | Python, Java, Web GUI |
| **Problem 2** | Closest Pair of Points Comparative Analysis | Divide & Conquer ($O(N \log N)$) vs Brute-Force ($O(N^2)$) | $O(N \log N)$ vs $O(N^2)$ | $O(N)$ vs $O(1)$ | Python, Java, Web GUI |
| **Problem 3** | Budget Traveller with Coupons | Layered Dynamic Programming / State Dijkstra | $O((K+1)(C+1) \cdot M)$ | $O((K+1)(C+1) \cdot N)$ | Python, Java, Web GUI |
| **Problem 4** | Exam Timetable Scheduling | Exact Branch-and-Bound + DSATUR & Welsh-Powell | Exact: $O(k^N)$ (pruned)<br>DSATUR: $O(N^2)$ | $O(N + M)$ | Python, Java, Web GUI |

---

## 📁 Repository Structure

```
dsa hackathon/
├── README.md                               # Project documentation & instructions
├── run_all.py                              # Master automated test & benchmark runner
├── web_visualizer/                         # Unified Interactive Browser Visualizer
│   ├── index.html                          # Single-page application with tabs for all 4 problems
│   ├── style.css                           # Modern responsive dark theme styling
│   └── app.js                              # Live Canvas animations, solvers, and charts
├── sample_data/                            # Input CSV files for all problems
│   ├── maze_sample.csv                     # Problem 1 input grid
│   ├── flights_sample.csv                  # Problem 3 flight connections (u, v, price)
│   └── conflicts_sample.csv                # Problem 4 exam conflict pairs
├── outputs/                                # Generated solution CSVs, plots, and animated GIFs
│   ├── problem1_maze.png                   # Problem 1 static grid & path
│   ├── problem1_animation.gif              # Problem 1 walkthrough GIF with inventory updates
│   ├── problem2_closest_pair.png           # Problem 2 plane with dividing line & 2d strip
│   ├── problem2_runtime_vs_n.png           # Problem 2 O(N^2) vs O(N log N) runtime curves
│   ├── problem2_animation.gif              # Problem 2 recursive split animation
│   ├── problem3_flight_network.png         # Problem 3 flight network diagram
│   ├── problem3_journey_animation.gif      # Problem 3 animated travel & coupon discount
│   ├── problem4_graph_and_timetable.png    # Problem 4 coloured conflict graph & timetable grid
│   └── problem4_comparison_charts.png      # Problem 4 comparative chart (Slots & Runtime vs N)
├── problem1_maze/
│   ├── maze_solver.py                      # Python state-space BFS solver & maze generator
│   ├── MazeSolver.java                     # Java state-space BFS solver & CSV exporter
│   ├── visualizer.py                       # Matplotlib grid visualizer & GIF animator
│   └── test_maze.py                        # Corner cases unit test suite
├── problem2_closest_pair/
│   ├── closest_pair.py                     # Python Brute-Force & Divide-and-Conquer solvers
│   ├── ClosestPair.java                    # Java comparative implementation & benchmark
│   ├── visualizer.py                       # Strip plotter, runtime benchmark, & split animation
│   └── test_closest_pair.py                # Corner case test suite (duplicates, collinear, etc.)
├── problem3_budget_traveller/
│   ├── budget_traveller.py                 # Python Layered DP / State Dijkstra solver
│   ├── BudgetTraveller.java                # Java implementation & CSV exporter
│   ├── visualizer.py                       # NetworkX graph visualizer & journey animator
│   └── test_budget_traveller.py            # Corner case test suite
└── problem4_exam_scheduling/
    ├── exam_scheduler.py                   # Python Welsh-Powell, DSATUR, & Exact Branch & Bound
    ├── ExamScheduler.java                  # Java implementation with Lower Bound derivation
    ├── visualizer.py                       # NetworkX graph coloring & timetable visualizer
    └── test_exam_scheduler.py              # Corner case test suite (K_n, empty, bipartite, etc.)
```

---

## 🚀 Quick Start

### 1. Run Everything End-to-End
Execute the master runner to run all unit tests, execute both Python and Java solvers, run performance benchmarks, and generate all output plots and CSVs:
```bash
python run_all.py
```

### 2. Launch the Interactive Web Visualizer
Simply open `web_visualizer/index.html` in any web browser:
```bash
# On Windows PowerShell:
Start-Process web_visualizer/index.html
```
The browser interface provides real-time canvas animation, parameter controls, inventory panels, and comparison charts for all 4 problems!

---

## 💻 Detailed Running Instructions

### Problem 1: Maze with Keys and Doors
- **Run Python Solver:**
  ```bash
  python problem1_maze/maze_solver.py --generate --N 12 --T 3 --output-csv outputs/p1_solution.csv
  # Or with custom CSV:
  python problem1_maze/maze_solver.py --csv sample_data/maze_sample.csv --T 3
  ```
- **Generate Visualizations:**
  ```bash
  python problem1_maze/visualizer.py
  ```
- **Run Java Solver:**
  ```bash
  javac problem1_maze/MazeSolver.java
  java problem1_maze.MazeSolver --T 3
  ```
- **Run Tests:**
  ```bash
  python -m unittest problem1_maze/test_maze.py
  ```

---

### Problem 2: Closest Pair of Points Comparative Analysis
- **Run Comparison on $N$ points:**
  ```bash
  python problem2_closest_pair/closest_pair.py --N 200
  ```
- **Run Benchmark Suite & Generate Runtime vs $N$ Plot:**
  ```bash
  python problem2_closest_pair/visualizer.py
  ```
- **Run Java Benchmark:**
  ```bash
  javac problem2_closest_pair/ClosestPair.java
  java problem2_closest_pair.ClosestPair 1000
  ```
- **Run Corner Case Tests:**
  ```bash
  python -m unittest problem2_closest_pair/test_closest_pair.py
  ```

---

### Problem 3: Budget Traveller with Coupons
- **Run Python Solver:**
  ```bash
  python problem3_budget_traveller/budget_traveller.py --generate --N 7 --K 3 --C 2
  # Or with custom CSV:
  python problem3_budget_traveller/budget_traveller.py --csv sample_data/flights_sample.csv --K 2 --C 1
  ```
- **Generate Graph & Journey Animation:**
  ```bash
  python problem3_budget_traveller/visualizer.py
  ```
- **Run Java Solver:**
  ```bash
  javac problem3_budget_traveller/BudgetTraveller.java
  java problem3_budget_traveller.BudgetTraveller
  ```
- **Run Corner Case Tests:**
  ```bash
  python -m unittest problem3_budget_traveller/test_budget_traveller.py
  ```

---

### Problem 4: Exam Timetable Scheduling (Graph Colouring)
- **Run Schedulers (Welsh-Powell, DSATUR, Exact B&B):**
  ```bash
  python problem4_exam_scheduling/exam_scheduler.py --N 12 --R 3 --density 0.35
  ```
- **Generate Graph, Timetable Matrix, & Comparison Chart:**
  ```bash
  python problem4_exam_scheduling/visualizer.py
  ```
- **Run Java Schedulers:**
  ```bash
  javac problem4_exam_scheduling/ExamScheduler.java
  java problem4_exam_scheduling.ExamScheduler
  ```
- **Run Corner Case Tests:**
  ```bash
  python -m unittest problem4_exam_scheduling/test_exam_scheduler.py
  ```
