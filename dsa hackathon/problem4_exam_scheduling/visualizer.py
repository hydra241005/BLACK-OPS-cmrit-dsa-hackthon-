"""
Visualization for Problem 4: Exam Timetable Scheduling
1. Conflict graph with nodes coloured according to their assigned slot.
2. Final timetable rendered as a colored grid/matrix.
3. Comparison chart of slots used and running time for each algorithm as N increases.
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any
from exam_scheduler import ExamScheduler, compare_algorithms

SLOT_COLORS = [
    '#E53935',  # Slot 1: Red
    '#1E88E5',  # Slot 2: Blue
    '#43A047',  # Slot 3: Green
    '#FB8C00',  # Slot 4: Orange
    '#8E24AA',  # Slot 5: Purple
    '#00ACC1',  # Slot 6: Cyan
    '#FDD835',  # Slot 7: Yellow
    '#D81B60',  # Slot 8: Magenta
    '#3949AB',  # Slot 9: Indigo
    '#7CB342',  # Slot 10: Light Green
    '#6D4C41',  # Slot 11: Brown
    '#546E7A',  # Slot 12: Blue Grey
]

def get_slot_color(slot: int) -> str:
    return SLOT_COLORS[(slot - 1) % len(SLOT_COLORS)]


def plot_colored_graph_and_timetable(scheduler: ExamScheduler, coloring: Dict[int, int], output_path: str = "outputs/problem4_graph_and_timetable.png"):
    G = nx.Graph()
    for i in range(1, scheduler.N + 1):
        G.add_node(i)
    for u, v in scheduler.conflicts:
        G.add_edge(u, v)

    fig, (ax_graph, ax_table) = plt.subplots(1, 2, figsize=(14, 7), gridspec_kw={'width_ratios': [1.3, 1]}, dpi=150)
    pos = nx.spring_layout(G, seed=42, k=1.4)

    node_colors = [get_slot_color(coloring[n]) for n in G.nodes()]

    # Draw Graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=650, edgecolors='#263238', linewidths=1.5, ax=ax_graph)
    nx.draw_networkx_edges(G, pos, edge_color='#90A4AE', width=1.5, alpha=0.8, ax=ax_graph)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='white', ax=ax_graph)

    num_slots = max(coloring.values()) if coloring else 0
    ax_graph.set_title(f"Conflict Graph ({scheduler.N} Courses, {len(scheduler.conflicts)} Conflicts)\nColoured by Slot ({num_slots} Slots Total, Cap R={scheduler.R})", fontsize=12, fontweight='bold')
    ax_graph.axis('off')

    # Draw Timetable Grid
    slots_map: Dict[int, List[int]] = {}
    for c, s in coloring.items():
        slots_map.setdefault(s, []).append(c)

    ax_table.set_xlim(0, scheduler.R + 1)
    ax_table.set_ylim(num_slots + 1, 0)
    ax_table.axis('off')

    # Draw table header
    ax_table.text(0.5, 0.5, "Slot", ha='center', va='center', fontsize=11, fontweight='bold', color='#1A237E')
    for h in range(scheduler.R):
        ax_table.text(h + 1.5, 0.5, f"Hall {h+1}", ha='center', va='center', fontsize=11, fontweight='bold', color='#1A237E')

    # Draw grid cells
    for s in range(1, num_slots + 1):
        courses = sorted(slots_map.get(s, []))
        slot_col = get_slot_color(s)

        # Slot label box
        rect_slot = patches.Rectangle((0.1, s + 0.1), 0.8, 0.8, facecolor=slot_col, edgecolor='#37474F', linewidth=1.2, alpha=0.9)
        ax_table.add_patch(rect_slot)
        ax_table.text(0.5, s + 0.5, f"Slot {s}", ha='center', va='center', fontsize=9, fontweight='bold', color='white')

        # Hall boxes
        for h in range(scheduler.R):
            c_text = f"C{courses[h]}" if h < len(courses) else "-"
            box_col = slot_col if h < len(courses) else '#ECEFF1'
            text_col = 'white' if h < len(courses) else '#9E9E9E'

            rect_hall = patches.Rectangle((h + 1.1, s + 0.1), 0.8, 0.8, facecolor=box_col, edgecolor='#B0BEC5', linewidth=1, alpha=0.85 if h < len(courses) else 0.5)
            ax_table.add_patch(rect_hall)
            ax_table.text(h + 1.5, s + 0.5, c_text, ha='center', va='center', fontsize=10, fontweight='bold', color=text_col)

    ax_table.set_title("Final Examination Timetable Grid", fontsize=12, fontweight='bold')

    plt.suptitle("Problem 4: Exam Timetable Scheduling Solution", fontsize=14, fontweight='bold')
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Graph and timetable visualization saved to: {output_path}")


def plot_algorithm_comparison(output_path: str = "outputs/problem4_comparison_charts.png"):
    """
    Compares Welsh-Powell, DSATUR, and Exact Branch-and-Bound
    across increasing course counts N: slots used and running time.
    """
    sizes = [6, 10, 14, 18, 22, 26, 30]
    R = 3
    density = 0.35

    wp_slots_list = []
    ds_slots_list = []
    ex_slots_list = []

    wp_time_list = []
    ds_time_list = []
    ex_time_list = []

    print("\n--- Running Problem 4 Benchmark Comparison ---")
    for n in sizes:
        sched = ExamScheduler.generate_random_conflict_graph(n, R, density, seed=n * 3 + 7)
        res = compare_algorithms(sched)

        wp_slots_list.append(res["Welsh_Powell"]["slots"])
        ds_slots_list.append(res["DSATUR"]["slots"])
        ex_slots_list.append(res["Exact_Branch_Bound"]["slots"])

        wp_time_list.append(res["Welsh_Powell"]["time_ms"])
        ds_time_list.append(res["DSATUR"]["time_ms"])
        ex_time_list.append(res["Exact_Branch_Bound"]["time_ms"])

        print(f"N={n:2d} | WP Slots: {res['Welsh_Powell']['slots']} | DSATUR Slots: {res['DSATUR']['slots']} | Exact Slots: {res['Exact_Branch_Bound']['slots']}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=150)

    # 1. Slots Used Chart
    ax1.plot(sizes, wp_slots_list, 'o--', color='#E53935', linewidth=2, label='Welsh-Powell Heuristic')
    ax1.plot(sizes, ds_slots_list, 's-', color='#1E88E5', linewidth=2.2, label='DSATUR Heuristic')
    ax1.plot(sizes, ex_slots_list, '^-', color='#43A047', linewidth=2.5, label='Exact Branch & Bound (Optimal)')
    ax1.set_title("Slots Required vs Course Count (N)", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Number of Courses (N)", fontsize=11)
    ax1.set_ylabel("Total Time Slots Needed", fontsize=11)
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)

    # 2. Running Time Chart
    ax2.plot(sizes, wp_time_list, 'o--', color='#E53935', linewidth=2, label='Welsh-Powell Heuristic')
    ax2.plot(sizes, ds_time_list, 's-', color='#1E88E5', linewidth=2.2, label='DSATUR Heuristic')
    ax2.plot(sizes, ex_time_list, '^-', color='#43A047', linewidth=2.5, label='Exact Branch & Bound')
    ax2.set_yscale('log')
    ax2.set_title("Running Time vs Course Count (Log Scale)", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Number of Courses (N)", fontsize=11)
    ax2.set_ylabel("Execution Time (ms, log scale)", fontsize=11)
    ax2.legend()
    ax2.grid(True, which='both', linestyle=':', alpha=0.6)

    plt.suptitle("Problem 4: Algorithm Comparative Analysis (Slots and Runtime)", fontsize=15, fontweight='bold')
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Algorithm comparison charts saved to: {output_path}")


if __name__ == "__main__":
    scheduler = ExamScheduler.generate_random_conflict_graph(12, 3, 0.3, seed=42)
    comp = compare_algorithms(scheduler)
    best_coloring = comp["Exact_Branch_Bound"]["coloring"]
    plot_colored_graph_and_timetable(scheduler, best_coloring, "outputs/problem4_graph_and_timetable.png")
    plot_algorithm_comparison("outputs/problem4_comparison_charts.png")
