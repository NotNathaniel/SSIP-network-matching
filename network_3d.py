from __future__ import annotations
import csv
from typing import Iterable, Tuple

import networkx as nx
import plotly.graph_objects as go


def load_edges(path: str) -> Iterable[Tuple[str, str, float]]:
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                score = float(row['match_score'])
            except (ValueError, KeyError):
                continue
            yield row['saudi_entity'], row['swedish_entity'], score


def build_graph(edges: Iterable[Tuple[str, str, float]]) -> nx.Graph:
    G = nx.Graph()
    for sa, sw, score in edges:
        G.add_node(sa, group='saudi')
        G.add_node(sw, group='swedish')
        G.add_edge(sa, sw, weight=score)
    return G


def plot_3d_network(G: nx.Graph, html_path: str = 'network_3d.html') -> None:
    pos = nx.spring_layout(G, dim=3, weight='weight', seed=42)
    edge_x, edge_y, edge_z = [], [], []
    for u, v in G.edges():
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
    edge_trace = go.Scatter3d(x=edge_x, y=edge_y, z=edge_z,
                              mode='lines',
                              line=dict(width=1, color='#888'),
                              hoverinfo='none')
    node_x = [pos[n][0] for n in G.nodes]
    node_y = [pos[n][1] for n in G.nodes]
    node_z = [pos[n][2] for n in G.nodes]
    node_text = list(G.nodes)
    node_trace = go.Scatter3d(x=node_x, y=node_y, z=node_z,
                              mode='markers',
                              marker=dict(size=4, color='skyblue'),
                              text=node_text,
                              hoverinfo='text')
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False,
                      margin=dict(l=0, r=0, b=0, t=0))
    fig.write_html(html_path)


if __name__ == '__main__':
    graph = build_graph(load_edges('network_edges.csv'))
    plot_3d_network(graph)
