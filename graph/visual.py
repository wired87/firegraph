import os
import sys
import networkx as nx
from pyvis.network import Network

# Custom styles: node type -> color, shape, size
_NODE_STYLES = {
    "MODULE": {"color": "#4a90d9", "shape": "box", "size": 28},
    "CLASS": {"color": "#7b68ee", "shape": "diamond", "size": 24},
    "METHOD": {"color": "#50c878", "shape": "dot", "size": 18},
    "PARAM": {"color": "#f0e68c", "shape": "triangle", "size": 14},
    "CLASS_VAR": {"color": "#daa520", "shape": "star", "size": 16},
    "FOLDER": {"color": "#20b2aa", "shape": "box", "size": 22},
    "TECHNIQUE": {"color": "#e74c3c", "shape": "hexagon", "size": 20},
}
_DEFAULT_NODE = {"color": "#888888", "shape": "dot", "size": 16}

# Hash-based color palette for edges (distinct color per rel)
_PALETTE = [
    "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7", "#fd79a8",
    "#a29bfe", "#00b894", "#e17055", "#0984e3", "#6c5ce7", "#fdcb6e",
]


def _rel_color(rel: str) -> str:
    """Deterministic color per relation type from palette."""
    return _PALETTE[hash(rel) % len(_PALETTE)]


def _style_node(ntype: str, nid) -> dict:
    s = _NODE_STYLES.get(ntype, _DEFAULT_NODE)
    return {"label": str(nid), "title": f"{ntype}: {nid}", **s}


def create_g_visual(G, dest_path=None, ds=True):
    """
    Build pyvis Network from graph G with custom styles.
    ds=True: datastore format (nodes with graph_item, edges as special nodes).
    ds=False: direct format (G.nodes + G.edges, e.g. from StructInspector).
    """
    print("create_g_visual G:", G, file=sys.stderr)
    try:
        new_G = nx.MultiGraph()
        if ds:
            for nid, attrs in G.nodes(data=True):
                if attrs.get("graph_item") == "node":
                    ntype = attrs.get("type", "NODE")
                    new_G.add_node(nid, **_style_node(ntype, nid))
            for nid, attrs in G.nodes(data=True):
                if attrs.get("graph_item") == "edge":
                    src, trgt = attrs.get("src"), attrs.get("trgt")
                    if src and trgt and new_G.has_node(src) and new_G.has_node(trgt):
                        rel = attrs.get("rel", "edge")
                        new_G.add_edge(src, trgt, color=_rel_color(rel), title=rel)
        else:
            for nid, attrs in G.nodes(data=True):
                ntype = attrs.get("type", "NODE")
                new_G.add_node(nid, **_style_node(ntype, nid))
            for src, trgt, attrs in G.edges(data=True):
                if new_G.has_node(src) and new_G.has_node(trgt):
                    rel = attrs.get("rel", "link")
                    new_G.add_edge(src, trgt, color=_rel_color(rel), width=1.2, title=rel)

        options = '''
            const options = {
              "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "font": { "size": 14, "face": "Segoe UI", "color": "#ffffff" },
                "shadow": { "enabled": true, "color": "rgba(0,0,0,0.2)", "size": 10, "x": 2, "y": 2 }
              },
              "edges": {
                "smooth": { "type": "continuous", "roundness": 0.5 },
                "font": { "size": 11, "color": "#cccccc" }
              },
              "physics": {
                "barnesHut": {
                  "gravitationalConstant": -3000,
                  "centralGravity": 0.1,
                  "springLength": 150,
                  "springConstant": 0.04,
                  "damping": 0.09
                }
              }
            }
            '''

        net = Network(
            notebook=False,
            cdn_resources="in_line",
            height="1000px",
            width="100%",
            bgcolor="#1a1a2e",
            font_color="white",
        )

        net.barnes_hut()
        net.toggle_physics(True)
        net.set_options(options)

        net.from_nx(new_G)

        # Force HTML generation
        net.html = net.generate_html()
        if dest_path is not None:
            # Ensure parent dir exists (fix: Err create_g_visual [Errno 2] No such file or directory)
            parent = os.path.dirname(dest_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(dest_path, 'w', encoding="utf-8") as f:
                f.write(net.html)
            print("html created and saved under:", dest_path, file=sys.stderr)
        else:
            return net.html
    except Exception as e:
        print("Err create_g_visual:", e, file=sys.stderr)