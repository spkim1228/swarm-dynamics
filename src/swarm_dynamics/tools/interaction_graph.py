import duckdb
import networkx as nx

from pathlib import Path
from pyvis.network import Network


def build_graph(participation_sql: str, stats: list[str], min_weight: int = 1) -> nx.Graph:
    """Undirected co-participation graph: agents are nodes, an edge links two agents
    that took part in the same unit (page, post, room-day, ...), weighted by the
    number of units they share.

    participation_sql must return one row per (unit, agent) with columns
    `unit`, `agent`, then one column per name in `stats`. Pairs are counted in
    DuckDB so large datasets stay out of Python. Each edge keeps a `units` dict of
    {unit: {agent: [stat, ...]}} so the strength of every interaction can be inspected.
    """
    con = duckdb.connect()
    con.execute(f"CREATE TABLE part AS SELECT * FROM ({participation_sql}) WHERE agent IS NOT NULL")
    con.execute(f"""
        CREATE TABLE edges AS
        SELECT a.agent AS a, b.agent AS b FROM part a JOIN part b ON a.unit = b.unit AND a.agent < b.agent
        GROUP BY 1, 2 HAVING count(*) >= {min_weight}
    """)
    cols = ", ".join([f"pa.{s}" for s in stats] + [f"pb.{s}" for s in stats])
    rows = con.execute(f"""
        SELECT e.a, e.b, pa.unit, {cols}
        FROM edges e
        JOIN part pa ON pa.agent = e.a
        JOIN part pb ON pb.agent = e.b AND pb.unit = pa.unit
    """).fetchall()

    k = len(stats)
    g = nx.Graph()
    for a, b, unit, *s in rows:
        if not g.has_edge(a, b):
            g.add_edge(a, b, units={})
        g[a][b]["units"][unit] = {a: s[:k], b: s[k:]}
    for _, _, d in g.edges(data=True):
        d["weight"] = len(d["units"])
    return g


def render(g: nx.Graph, out_path: Path, stats: list[str], unit_name: str = "units", tooltip_limit: int | None = None) -> Path:
    """Write the graph to a pyvis HTML page. Edge tooltips list shared units with each
    agent's stats, most active first (by the first stat), capped at tooltip_limit."""
    # in_line embeds the JS/CSS so the page doesn't depend on a lib/ folder beside it.
    net = Network(height="900px", width="100%", select_menu=True, filter_menu=True, cdn_resources="in_line")
    for n in g.nodes:
        w = g.degree(n, weight="weight")
        net.add_node(n, label=n, value=w, title=f"{n}\nshared {unit_name}: {w}")
    for a, b, d in g.edges(data=True):
        lines = [f"{a} — {b}: {d['weight']} shared {unit_name}", f"{unit_name} | {', '.join(stats)}"]
        units = sorted(d["units"].items(), key=lambda kv: -(kv[1][a][0] + kv[1][b][0]))[:tooltip_limit]
        for unit, s in units:
            lines.append(f"{unit} | {a}: {', '.join(map(str, s[a]))} ; {b}: {', '.join(map(str, s[b]))}")
        if tooltip_limit and d["weight"] > tooltip_limit:
            lines.append(f"... {d['weight'] - tooltip_limit} more")
        net.add_edge(a, b, value=d["weight"], title="\n".join(lines))
    net.barnes_hut()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    net.write_html(str(out_path), notebook=False)
    return out_path
