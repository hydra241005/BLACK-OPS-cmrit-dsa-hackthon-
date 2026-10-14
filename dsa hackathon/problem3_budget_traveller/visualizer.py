"""
Visualization for Problem 3: Budget Traveller with Coupons
Uses NetworkX and Matplotlib to draw the flight network, highlight path,
and animate journey showing coupon application and price transition.
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from typing import List, Dict, Any
from budget_traveller import BudgetTraveller


def plot_flight_network(traveller: BudgetTraveller, path: List[Dict[str, Any]], output_path: str = "outputs/problem3_flight_network.png"):
    G = nx.DiGraph()
    for e in traveller.edges:
        G.add_edge(e.u, e.v, weight=e.price)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    pos = nx.spring_layout(G, seed=42, k=1.8)

    # Identify node categories
    path_nodes = set()
    for step in path:
        path_nodes.add(step['from'])
        path_nodes.add(step['to'])

    start_node = 1
    dest_node = traveller.N
    intermediate_nodes = [node for node in path_nodes if node != start_node and node != dest_node]
    other_nodes = [node for node in G.nodes if node not in path_nodes]

    # Draw nodes
    # Start = Green, Destination = Red, Intermediate = Orange, Others = Light Slate
    nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='#4CAF50', node_size=800, label='Start (City 1)', ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=[dest_node], node_color='#F44336', node_size=800, label=f'Destination (City {dest_node})', ax=ax)
    if intermediate_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=intermediate_nodes, node_color='#FF9800', node_size=700, label='Intermediate Stops', ax=ax)
    if other_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=other_nodes, node_color='#B0BEC5', node_size=500, label='Other Cities', ax=ax)

    # Draw standard edges
    path_edge_set = set((s['from'], s['to']) for s in path)
    normal_edges = [e for e in G.edges if e not in path_edge_set]
    nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color='#CFD8DC', width=1.5, arrowsize=14, ax=ax)

    # Draw path edges
    coupon_edges = [(s['from'], s['to']) for s in path if s['coupon']]
    no_coupon_path_edges = [(s['from'], s['to']) for s in path if not s['coupon']]

    if no_coupon_path_edges:
        nx.draw_networkx_edges(G, pos, edgelist=no_coupon_path_edges, edge_color='#2196F3', width=3.5, arrowsize=20, label='Flight (Standard)', ax=ax)
    if coupon_edges:
        nx.draw_networkx_edges(G, pos, edgelist=coupon_edges, edge_color='#FFD700', width=4.5, arrowsize=24, label='Flight (Coupon 50% Off)', ax=ax)

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', font_color='white', ax=ax)
    edge_labels = {(u, v): f"${d['weight']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)

    total_cost = sum(s['paid'] for s in path) if path else -1
    ax.set_title(f"Problem 3: Budget Flight Network | Optimal Cost: ${total_cost} | Stops: {len(path)-1} (Max K={traveller.K}) | Coupons: {sum(1 for s in path if s['coupon'])}/{traveller.C}", fontsize=12, fontweight='bold', pad=15)
    ax.legend(loc='lower left', framealpha=0.9)
    ax.axis('off')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"Flight network plot saved to: {output_path}")


def animate_journey(traveller: BudgetTraveller, path: List[Dict[str, Any]], output_gif: str = "outputs/problem3_journey_animation.gif"):
    """
    Animates the journey step-by-step:
    - Running cost and stops counter
    - Changes flight color to gold when coupon is applied
    - Shows original price -> discounted price
    """
    if not path:
        return

    G = nx.DiGraph()
    for e in traveller.edges:
        G.add_edge(e.u, e.v, weight=e.price)

    pos = nx.spring_layout(G, seed=42, k=1.8)

    fig, (ax_graph, ax_info) = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={'width_ratios': [2.8, 1.2]}, dpi=100)

    start_node = 1
    dest_node = traveller.N

    def update_frame(step_idx):
        ax_graph.clear()
        ax_info.clear()

        # Nodes
        curr_step = path[step_idx]
        current_city = curr_step['to']

        nx.draw_networkx_nodes(G, pos, nodelist=[start_node], node_color='#4CAF50', node_size=700, ax=ax_graph)
        nx.draw_networkx_nodes(G, pos, nodelist=[dest_node], node_color='#F44336', node_size=700, ax=ax_graph)
        other_n = [n for n in G.nodes if n not in (start_node, dest_node)]
        nx.draw_networkx_nodes(G, pos, nodelist=other_n, node_color='#ECEFF1', node_size=500, ax=ax_graph)

        # Highlight current city
        nx.draw_networkx_nodes(G, pos, nodelist=[current_city], node_color='#AB47BC', node_size=900, ax=ax_graph)

        # Draw base edges
        nx.draw_networkx_edges(G, pos, edge_color='#CFD8DC', width=1.5, arrowsize=12, ax=ax_graph)

        # Draw traversed edges up to step_idx
        for idx in range(step_idx + 1):
            st = path[idx]
            color = '#FFD700' if st['coupon'] else '#2196F3'
            nx.draw_networkx_edges(G, pos, edgelist=[(st['from'], st['to'])], edge_color=color, width=4.0, arrowsize=22, ax=ax_graph)

        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax_graph)
        edge_labels = {(u, v): f"${d['weight']}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax_graph)

        ax_graph.set_title(f"Leg {step_idx + 1}/{len(path)}: City {curr_step['from']} -> City {curr_step['to']}", fontsize=12, fontweight='bold')
        ax_graph.axis('off')

        # Info panel
        ax_info.set_xlim(0, 1)
        ax_info.set_ylim(0, 1)
        ax_info.axis('off')
        ax_info.text(0.5, 0.95, "Journey Dashboard", ha='center', va='top', fontsize=13, fontweight='bold')

        running_cost = sum(path[i]['paid'] for i in range(step_idx + 1))
        coupons_used = sum(1 for i in range(step_idx + 1) if path[i]['coupon'])

        ax_info.text(0.1, 0.82, f"Current City: {current_city}", fontsize=11, fontweight='bold')
        ax_info.text(0.1, 0.74, f"Stops Made: {step_idx} / Max {traveller.K}", fontsize=11)
        ax_info.text(0.1, 0.66, f"Coupons Used: {coupons_used} / {traveller.C}", fontsize=11)
        ax_info.text(0.1, 0.58, f"Running Cost: ${running_cost}", fontsize=12, fontweight='bold', color='#1565C0')

        # Current leg coupon info
        ax_info.text(0.1, 0.45, "Latest Flight:", fontsize=11, fontweight='bold')
        if curr_step['coupon']:
            ax_info.text(0.1, 0.37, "COUPON APPLIED!", fontsize=11, fontweight='bold', color='#E65100')
            ax_info.text(0.1, 0.29, f"Price: ${curr_step['orig_price']} -> ${curr_step['paid']}", fontsize=12, fontweight='bold', color='#D84315')
        else:
            ax_info.text(0.1, 0.37, "Standard Ticket", fontsize=10)
            ax_info.text(0.1, 0.29, f"Price: ${curr_step['paid']}", fontsize=11)

    anim = animation.FuncAnimation(fig, update_frame, frames=len(path), interval=800, repeat=False)
    os.makedirs(os.path.dirname(os.path.abspath(output_gif)), exist_ok=True)
    try:
        anim.save(output_gif, writer='pillow', fps=1.5)
        print(f"Journey animation saved to: {output_gif}")
    except Exception as e:
        print(f"Could not save journey GIF: {e}")
    plt.close()


if __name__ == "__main__":
    sample_edges = [
        (1, 2, 300), (1, 3, 700), (2, 3, 100), (2, 4, 400),
        (3, 4, 200), (4, 5, 500), (3, 5, 800), (2, 5, 1200)
    ]
    traveller = BudgetTraveller(N=5, K=2, C=1, edges=sample_edges)
    cost, path = traveller.solve()
    print("Cost:", cost)
    plot_flight_network(traveller, path, "outputs/problem3_flight_network.png")
    animate_journey(traveller, path, "outputs/problem3_journey_animation.gif")
