"""
Visualization for Problem 1: Maze with Keys and Doors
Renders colored grid, path overlay, key-inventory tracking, and generates animated walkthrough.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from typing import List, Tuple, Optional
from maze_solver import MazeSolver

# Key-Door distinct color palette (up to 6 pairs)
KEY_DOOR_COLORS = [
    "#FFD700",  # a/A: Gold / Yellow
    "#1E90FF",  # b/B: Dodger Blue
    "#FF1493",  # c/C: Deep Pink / Magenta
    "#00CED1",  # d/D: Dark Turquoise / Cyan
    "#9400D3",  # e/E: Dark Violet / Purple
    "#FF8C00",  # f/F: Dark Orange
]

COLOR_MAP = {
    '.': '#FFFFFF',  # White (open)
    '#': '#2B2B2B',  # Black / Dark Charcoal (wall)
    'S': '#2ECC71',  # Green (start)
    'E': '#E74C3C',  # Red (exit)
}


def get_cell_color(cell: str) -> str:
    if cell in COLOR_MAP:
        return COLOR_MAP[cell]
    if 'a' <= cell <= 'f':
        idx = ord(cell) - ord('a')
        return KEY_DOOR_COLORS[idx % len(KEY_DOOR_COLORS)]
    if 'A' <= cell <= 'F':
        idx = ord(cell) - ord('A')
        return KEY_DOOR_COLORS[idx % len(KEY_DOOR_COLORS)]
    return '#E0E0E0'


def draw_static_maze(grid: List[List[str]], path: Optional[List[Tuple[int, int, int]]] = None, output_image: str = "outputs/problem1_maze.png"):
    N = len(grid)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.set_xlim(0, N)
    ax.set_ylim(N, 0)
    ax.set_xticks(range(N + 1))
    ax.set_yticks(range(N + 1))
    ax.grid(True, color='#B0BEC5', linewidth=0.8)

    for r in range(N):
        for c in range(N):
            cell = grid[r][c].strip()
            bg_color = get_cell_color(cell)
            rect = patches.Rectangle((c, r), 1, 1, facecolor=bg_color, edgecolor='#37474F', linewidth=0.5)
            ax.add_patch(rect)

            # Draw cell text
            if cell in ('S', 'E'):
                ax.text(c + 0.5, r + 0.5, cell, ha='center', va='center', fontsize=12, fontweight='bold', color='white')
            elif 'a' <= cell <= 'f':
                ax.text(c + 0.5, r + 0.5, f"key:{cell}", ha='center', va='center', fontsize=9, fontweight='bold', color='#1A237E')
            elif 'A' <= cell <= 'F':
                ax.text(c + 0.5, r + 0.5, f"DOOR:{cell}", ha='center', va='center', fontsize=8, fontweight='bold', color='#FFFFFF')

    # Draw path
    if path and len(path) > 1:
        path_coords = [(c + 0.5, r + 0.5) for r, c, _ in path]
        xs, ys = zip(*path_coords)
        ax.plot(xs, ys, color='#9C27B0', linewidth=3.5, linestyle='-', marker='o', markersize=4, label='Shortest Path', zorder=5)

    ax.set_title("Problem 1: Maze with Keys and Doors Solution Path", fontsize=14, fontweight='bold', pad=15)
    os.makedirs(os.path.dirname(os.path.abspath(output_image)), exist_ok=True)
    plt.savefig(output_image, bbox_inches='tight')
    plt.close()
    print(f"Static maze visualization saved to: {output_image}")


def create_maze_animation(grid: List[List[str]], path: List[Tuple[int, int, int]], T: int, output_gif: str = "outputs/problem1_animation.gif"):
    """
    Animates key pick-ups (key disappears, inventory panel updates)
    and door openings (door turns from its colour to white with an unlock mark).
    """
    if not path:
        return

    N = len(grid)
    fig, (ax_maze, ax_panel) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [3, 1]}, dpi=100)

    # Initial grid clone
    current_grid = [row[:] for row in grid]

    def render_frame(step_idx):
        ax_maze.clear()
        ax_panel.clear()

        r_curr, c_curr, mask_curr = path[step_idx]

        # Update dynamic grid state up to step_idx
        # If we passed over a key, mark it collected; if door passed, mark unlocked
        display_grid = [row[:] for row in grid]
        for idx in range(step_idx + 1):
            pr, pc, pmask = path[idx]
            orig = grid[pr][pc].strip()
            if 'a' <= orig <= 'f':
                display_grid[pr][pc] = '.'  # Key disappears into inventory
            elif 'A' <= orig <= 'F':
                display_grid[pr][pc] = f"OPEN:{orig}"  # Unlocked door turns white

        # Draw maze
        ax_maze.set_xlim(0, N)
        ax_maze.set_ylim(N, 0)
        ax_maze.set_xticks([])
        ax_maze.set_yticks([])

        for r in range(N):
            for c in range(N):
                cell = display_grid[r][c].strip()
                if cell.startswith('OPEN:'):
                    bg_color = '#FFFFFF'  # Door turns white when unlocked
                else:
                    bg_color = get_cell_color(cell)

                rect = patches.Rectangle((c, r), 1, 1, facecolor=bg_color, edgecolor='#37474F', linewidth=0.5)
                ax_maze.add_patch(rect)

                if cell in ('S', 'E'):
                    ax_maze.text(c + 0.5, r + 0.5, cell, ha='center', va='center', fontsize=11, fontweight='bold', color='white')
                elif 'a' <= cell <= 'f':
                    ax_maze.text(c + 0.5, r + 0.5, f"key:{cell}", ha='center', va='center', fontsize=9, fontweight='bold', color='#1A237E')
                elif 'A' <= cell <= 'F':
                    ax_maze.text(c + 0.5, r + 0.5, f"DOOR:{cell}", ha='center', va='center', fontsize=8, fontweight='bold', color='#FFFFFF')
                elif cell.startswith('OPEN:'):
                    door_letter = cell.split(':')[1]
                    ax_maze.text(c + 0.5, r + 0.5, f"OPEN:{door_letter}", ha='center', va='center', fontsize=7, fontweight='bold', color='#2E7D32')

        # Trace path traveled so far
        past_coords = [(c + 0.5, r + 0.5) for r, c, _ in path[:step_idx + 1]]
        if past_coords:
            xs, ys = zip(*past_coords)
            ax_maze.plot(xs, ys, color='#AB47BC', linewidth=2.5, alpha=0.8)

        # Draw agent current position
        agent = patches.Circle((c_curr + 0.5, r_curr + 0.5), 0.35, facecolor='#FFEB3B', edgecolor='#D84315', linewidth=2, zorder=10)
        ax_maze.add_patch(agent)
        ax_maze.set_title(f"Step {step_idx}/{len(path)-1} | Pos: ({r_curr}, {c_curr})", fontsize=12, fontweight='bold')

        # Draw inventory panel
        ax_panel.set_xlim(0, 1)
        ax_panel.set_ylim(0, 1)
        ax_panel.axis('off')
        ax_panel.text(0.5, 0.95, "Inventory Panel", ha='center', va='top', fontsize=13, fontweight='bold')
        ax_panel.text(0.5, 0.88, f"Keys Held (T={T}):", ha='center', va='top', fontsize=11)

        for i in range(T):
            k_char = chr(ord('a') + i)
            d_char = chr(ord('A') + i)
            held = bool(mask_curr & (1 << i))
            status_text = f"Key '{k_char}': {'[ACQUIRED]' if held else '[MISSING]'}"
            color = KEY_DOOR_COLORS[i % len(KEY_DOOR_COLORS)]
            rect_preview = patches.Rectangle((0.08, 0.76 - i * 0.11), 0.12, 0.08, facecolor=color, edgecolor='#000')
            ax_panel.add_patch(rect_preview)
            ax_panel.text(0.24, 0.80 - i * 0.11, status_text, va='center', fontsize=10, fontweight='bold' if held else 'normal')

        ax_panel.text(0.5, 0.12, f"Total Distance: {step_idx}", ha='center', fontsize=11, fontweight='bold')

    anim = animation.FuncAnimation(fig, render_frame, frames=len(path), interval=250, repeat=False)
    os.makedirs(os.path.dirname(os.path.abspath(output_gif)), exist_ok=True)
    try:
        anim.save(output_gif, writer='pillow', fps=4)
        print(f"Animated walkthrough GIF saved to: {output_gif}")
    except Exception as e:
        print(f"Note: Could not save GIF ({e}). Static rendering is available.")
    plt.close()


if __name__ == "__main__":
    solver = MazeSolver.generate_random_maze(10, 3, seed=42)
    length, path, marked = solver.solve()
    print("Solved path length:", length)
    draw_static_maze(solver.grid, path, "outputs/problem1_maze.png")
    create_maze_animation(solver.grid, path, solver.T, "outputs/problem1_animation.gif")
