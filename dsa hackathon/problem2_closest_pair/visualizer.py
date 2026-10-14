"""
Visualization for Problem 2: Closest Pair of Points Comparative Analysis
1. Plots points, closest pairs (BF and DC), vertical divider line, and the 2d strip region.
2. Plots Running-Time vs N comparative curve.
3. Animates recursive splitting and strip search.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from typing import List, Tuple
from closest_pair import (
    Point, closest_pair_brute_force, closest_pair_divide_and_conquer,
    generate_random_points, benchmark_suite
)


def plot_closest_pair(points: List[Point], output_path: str = "outputs/problem2_closest_pair.png"):
    bf_d, bf_p1, bf_p2 = closest_pair_brute_force(points)
    dc_d, dc_p1, dc_p2, trace = closest_pair_divide_and_conquer(points, record_steps=True)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, color='#455A64', alpha=0.7, s=40, label='Data Points', zorder=3)

    # Dividing line and strip
    mid_x = trace.get("final_mid_x", (max(xs) + min(xs)) / 2)
    d = dc_d
    y_min, y_max = min(ys) - 50, max(ys) + 50
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(min(xs) - 50, max(xs) + 50)

    # Draw Strip region (width 2d: [mid_x - d, mid_x + d])
    strip_rect = patches.Rectangle((mid_x - d, y_min), 2 * d, y_max - y_min,
                                   facecolor='#FFF59D', alpha=0.35, edgecolor='#FBC02D',
                                   linestyle='--', linewidth=1.5, label=f'Strip Region [x_mid ± d] (width={2*d:.2f})', zorder=2)
    ax.add_patch(strip_rect)

    # Dividing line
    ax.axvline(mid_x, color='#D32F2F', linestyle='-', linewidth=2, label=f'Dividing Line (x={mid_x:.2f})', zorder=2)

    # Highlight BF closest pair
    if bf_p1 and bf_p2:
        ax.plot([bf_p1[0], bf_p2[0]], [bf_p1[1], bf_p2[1]], color='#1976D2', linewidth=3, linestyle='-',
                marker='o', markersize=9, label=f'Brute-Force Pair (d={bf_d:.4f})', zorder=6)

    # Highlight DC closest pair
    if dc_p1 and dc_p2:
        ax.plot([dc_p1[0], dc_p2[0]], [dc_p1[1], dc_p2[1]], color='#388E3C', linewidth=2, linestyle=':',
                marker='s', markersize=6, label=f'Divide & Conquer Pair (d={dc_d:.4f})', zorder=7)

    ax.set_title(f"Closest Pair of Points (N={len(points)}) | Min Distance = {dc_d:.6f}", fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel("X coordinate", fontsize=11)
    ax.set_ylabel("Y coordinate", fontsize=11)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, linestyle=':', alpha=0.6)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Closest pair visualization saved to: {output_path}")


def plot_runtime_comparison(output_path: str = "outputs/problem2_runtime_vs_n.png"):
    sizes = [10, 50, 100, 250, 500, 1000, 1500, 2000, 3000, 4000]
    bench_data = benchmark_suite(sizes)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=150)

    # Linear scale
    ax1.plot(bench_data["N"], bench_data["bf_time_ms"], 'o-', color='#E53935', linewidth=2.5, label='Brute-Force O(N²)')
    ax1.plot(bench_data["N"], bench_data["dc_time_ms"], 's-', color='#1E88E5', linewidth=2.5, label='Divide & Conquer O(N log N)')
    ax1.set_title("Execution Time vs Input Size (Linear Scale)", fontsize=13, fontweight='bold')
    ax1.set_xlabel("Input Size N", fontsize=11)
    ax1.set_ylabel("Execution Time (ms)", fontsize=11)
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Log-Log scale
    ax2.plot(bench_data["N"], bench_data["bf_time_ms"], 'o-', color='#E53935', linewidth=2.5, label='Brute-Force O(N²)')
    ax2.plot(bench_data["N"], bench_data["dc_time_ms"], 's-', color='#1E88E5', linewidth=2.5, label='Divide & Conquer O(N log N)')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("Execution Time vs Input Size (Log-Log Scale)", fontsize=13, fontweight='bold')
    ax2.set_xlabel("Input Size N (log scale)", fontsize=11)
    ax2.set_ylabel("Execution Time (ms, log scale)", fontsize=11)
    ax2.legend()
    ax2.grid(True, which='both', linestyle=':', alpha=0.6)

    plt.suptitle("Problem 2: Performance Comparative Analysis (Brute-Force vs Divide-and-Conquer)", fontsize=15, fontweight='bold')
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Runtime comparative plot saved to: {output_path}")


def create_recursive_split_animation(points: List[Point], output_gif: str = "outputs/problem2_animation.gif"):
    """Animates the recursive dividing lines and final strip search."""
    pts_sorted = sorted(points, key=lambda p: p[0])
    N = len(pts_sorted)
    
    # Collect divide steps
    steps = []
    def record_tree(pts, depth=0):
        if len(pts) <= 3:
            return
        m = len(pts) // 2
        mid_x = pts[m][0]
        steps.append((mid_x, depth, pts))
        record_tree(pts[:m], depth + 1)
        record_tree(pts[m:], depth + 1)

    record_tree(pts_sorted)

    fig, ax = plt.subplots(figsize=(9, 6), dpi=100)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    def render_step(i):
        ax.clear()
        ax.scatter(xs, ys, color='#546E7A', s=35, alpha=0.7)
        ax.set_title(f"Divide & Conquer Split Step {i+1}/{len(steps)}", fontsize=12, fontweight='bold')
        ax.grid(True, linestyle=':', alpha=0.5)

        # Plot all dividers up to step i
        for idx in range(i + 1):
            mx, dph, subpts = steps[idx]
            color = plt.cm.plasma(dph / 5.0)
            ax.axvline(mx, color=color, linestyle='--', linewidth=1.5, alpha=0.8, label=f'Depth {dph}' if idx == i else "")

    anim = animation.FuncAnimation(fig, render_step, frames=min(len(steps), 15), interval=500, repeat=False)
    os.makedirs(os.path.dirname(os.path.abspath(output_gif)), exist_ok=True)
    try:
        anim.save(output_gif, writer='pillow', fps=2)
        print(f"Divide & Conquer split animation saved to: {output_gif}")
    except Exception as e:
        print(f"Could not save animation GIF: {e}")
    plt.close()


if __name__ == "__main__":
    sample_pts = generate_random_points(60, coord_range=500, seed=42)
    plot_closest_pair(sample_pts, "outputs/problem2_closest_pair.png")
    create_recursive_split_animation(sample_pts, "outputs/problem2_animation.gif")
    plot_runtime_comparison("outputs/problem2_runtime_vs_n.png")
