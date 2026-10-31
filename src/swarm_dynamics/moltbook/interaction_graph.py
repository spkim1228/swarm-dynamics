import networkx as nx

from pathlib import Path

from swarm_dynamics.moltbook.compile_data import COOKED_DIR
from swarm_dynamics.tools import interaction_graph as ig

GRAPH_HTML = COOKED_DIR / "interaction_graph.html"
STATS = ["n_comments", "score", "authored"]
TOOLTIP_POSTS = 20


def build_graph(data_dir: Path = COOKED_DIR, min_weight: int = 200) -> nx.Graph:
    """Co-participation graph: agents linked by the posts they both authored or commented on."""
    return ig.build_graph(
        f"""
        SELECT x.post_id AS unit, ag.name AS agent, sum(x.n_comments) AS n_comments,
               sum(x.score) AS score, bool_or(x.authored) AS authored
        FROM (
            SELECT post_id, agent_id, 1 AS n_comments, score, false AS authored FROM '{data_dir}/comments.parquet'
            UNION ALL
            SELECT id, agent_id, 0, score, true FROM '{data_dir}/posts.parquet'
        ) x JOIN '{data_dir}/agents.parquet' ag ON ag.id = x.agent_id
        GROUP BY 1, 2
        """,
        STATS,
        min_weight,
    )


if __name__ == "__main__":
    g = build_graph()
    print(f"{g.number_of_nodes()} agents, {g.number_of_edges()} edges")
    print(f"Wrote {ig.render(g, GRAPH_HTML, STATS, 'posts', TOOLTIP_POSTS)}")
