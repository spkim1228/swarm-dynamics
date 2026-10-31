import networkx as nx

from pathlib import Path

from swarm_dynamics.ai_village.compile_data import FULL_DIR
from swarm_dynamics.tools import interaction_graph as ig

GRAPH_HTML = FULL_DIR.parent / "interaction_graph.html"
STATS = ["n_messages", "chars"]
TOOLTIP_UNITS = 20


def build_graph(data_dir: Path = FULL_DIR, min_weight: int = 1) -> nx.Graph:
    """Co-participation graph: agents linked by the room-days (same room, same day) they both spoke in."""
    return ig.build_graph(
        f"""
        WITH rooms AS (
            SELECT DISTINCT data.roomId::VARCHAR AS id, data.roomName::VARCHAR AS name
            FROM '{data_dir}/events.parquet' WHERE data.roomName IS NOT NULL
        )
        SELECT strftime(m.created_at, '%Y-%m-%d') || ' #' || coalesce(json_extract_string(r.name, '$'), left(m.room_id::VARCHAR, 8)) AS unit,
               ag.name AS agent, count(*) AS n_messages, sum(length(m.content)) AS chars
        FROM '{data_dir}/chat_messages.parquet' m
        JOIN '{data_dir}/agents.parquet' ag ON ag.id = m.agent_speaker_id
        LEFT JOIN rooms r ON json_extract_string(r.id, '$') = m.room_id::VARCHAR
        WHERE m.speaker_type = 'agent'
        GROUP BY 1, 2
        """,
        STATS,
        min_weight,
    )


if __name__ == "__main__":
    g = build_graph()
    print(f"{g.number_of_nodes()} agents, {g.number_of_edges()} edges")
    print(f"Wrote {ig.render(g, GRAPH_HTML, STATS, 'room-days', TOOLTIP_UNITS)}")
