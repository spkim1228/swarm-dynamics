import networkx as nx

from pathlib import Path

from swarm_dynamics.collusion.clean_main import COOKED_DIR, EDITS_PATH
from swarm_dynamics.tools import interaction_graph as ig

GRAPH_HTML = COOKED_DIR / "interaction_graph.html"
STATS = ["n_edits", "lines_added", "lines_removed"]


def build_graph(path: Path = EDITS_PATH, min_weight: int = 3) -> nx.Graph:
    """Co-edit graph: agents linked by the wiki pages they both edited (unlabeled edits dropped)."""
    return ig.build_graph(
        f"""
        SELECT page_key AS unit, label AS agent, count(*) AS n_edits,
               sum(n_lines_added) AS lines_added, sum(n_lines_removed) AS lines_removed
        FROM read_json('{path}', format='newline_delimited', columns={{
            'page_key': 'VARCHAR', 'label': 'VARCHAR', 'n_lines_added': 'BIGINT', 'n_lines_removed': 'BIGINT'}})
        WHERE label <> ''
        GROUP BY 1, 2
        """,
        STATS,
        min_weight,
    )


if __name__ == "__main__":
    g = build_graph()
    print(f"{g.number_of_nodes()} agents, {g.number_of_edges()} edges")
    print(f"Wrote {ig.render(g, GRAPH_HTML, STATS, 'pages')}")
