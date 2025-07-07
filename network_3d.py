from __future__ import annotations
import csv
from typing import Iterable, Tuple

import networkx as nx
import plotly.graph_objects as go


def load_edges(path: str) -> Iterable[Tuple[str, str, float, str, float]]:
    """Yield edges from ``path`` with justification information."""
    with open(path, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                score = float(row['match_score'])
                jscore = float(row.get('justification_score', '0'))
            except (ValueError, KeyError):
                continue
            justification = row.get('justification', '')
            yield row['saudi_entity'], row['swedish_entity'], score, justification, jscore


def build_graph(edges: Iterable[Tuple[str, str, float, str, float]]) -> nx.Graph:
    G = nx.Graph()
    for sa, sw, score, justification, jscore in edges:
        G.add_node(sa, group='saudi')
        G.add_node(sw, group='swedish')
        G.add_edge(sa, sw, weight=score, justification=justification, jscore=jscore)
    return G


def plot_3d_network(G: nx.Graph, html_path: str = 'network_3d.html') -> None:
    pos = nx.spring_layout(G, dim=3, weight='weight', seed=42)

    # scale factors based on justification scores
    j_scores = [d['jscore'] for _, _, d in G.edges(data=True)]
    max_j = max(j_scores) if j_scores else 1.0

    edge_traces = []
    for u, v, data in G.edges(data=True):
        x0, y0, z0 = pos[u]
        x1, y1, z1 = pos[v]
        width = 1 + 4 * data['jscore'] / max_j
        edge_traces.append(
            go.Scatter3d(
                x=[x0, x1, None],
                y=[y0, y1, None],
                z=[z0, z1, None],
                mode='lines',
                line=dict(width=width, color='#888'),
                hoverinfo='text',
                text=f'{u} → {v}',
                customdata=[data.get('justification', '')],
            )
        )

    node_x = [pos[n][0] for n in G.nodes]
    node_y = [pos[n][1] for n in G.nodes]
    node_z = [pos[n][2] for n in G.nodes]
    node_text = list(G.nodes)

    node_color = ['tomato' if G.nodes[n]['group'] == 'saudi' else 'skyblue' for n in G.nodes]
    node_size = []
    for n in G.nodes:
        scores = [G.edges[n, nb]['jscore'] for nb in G.neighbors(n)]
        avg = sum(scores) / len(scores) if scores else 0.0
        node_size.append(6 + 6 * avg / max_j)

    node_trace = go.Scatter3d(
        x=node_x,
        y=node_y,
        z=node_z,
        mode='markers',
        marker=dict(size=node_size, color=node_color),
        text=node_text,
        hoverinfo='text',
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(showlegend=False,
                      margin=dict(l=0, r=0, b=0, t=0),
                      clickmode='event')

    html = fig.to_html(include_plotlyjs='cdn', full_html=True, div_id='graph')
    html += (
        "<div id='justification' style='margin-top:10px;font-family:sans-serif;'></div>"
        "<script>var p=document.getElementById('graph');p.on('plotly_click',function(d){var cd=d.points[0].customdata;if(cd){document.getElementById('justification').innerText=cd;}});</script>"
    )
    with open(html_path, 'w', encoding='utf-8') as fh:
        fh.write(html)


if __name__ == '__main__':
    graph = build_graph(load_edges('network_edges.csv'))
    plot_3d_network(graph)
