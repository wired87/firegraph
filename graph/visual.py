import os
import sys
import networkx as nx
from pyvis.network import Network


def create_g_visual(G, dest_path=None, ds=True):
    """
    Build pyvis Network from graph G.
    ds=True: datastore format (nodes with graph_item, edges as special nodes).
    ds=False: direct format (G.nodes + G.edges, e.g. from StructInspector).
    """
    print("create_g_visual G:", G, file=sys.stderr)
    try:
        new_G = nx.Graph()
        if ds:
            # Datastore format: filter by graph_item
            for nid, attrs in G.nodes(data=True):
                if attrs.get("graph_item") == "node":
                    new_G.add_node(nid, **dict(type=attrs.get("type", "")))
            for nid, attrs in G.nodes(data=True):
                if attrs.get("graph_item") == "edge":
                    src, trgt = attrs.get("src"), attrs.get("trgt")
                    if src and trgt and new_G.has_node(src) and new_G.has_node(trgt):
                        new_G.add_edge(src, trgt, id=attrs.get("id"), type="edge")
        else:
            # Direct format: use nodes and edges as-is
            for nid, attrs in G.nodes(data=True):
                ntype = attrs.get("type", "NODE")
                new_G.add_node(nid, **dict(type=ntype, label=str(nid)))
            for src, trgt, attrs in G.edges(data=True):
                if new_G.has_node(src) and new_G.has_node(trgt):
                    rel = attrs.get("rel", "link")
                    new_G.add_edge(src, trgt, id=attrs.get("eid", f"{src}_{rel}_{trgt}"), type=rel)

        options = '''
            const options = {
              "nodes": {
                "borderWidthSelected": 21,
                "font": {
                  "size": 20,
                  "face": "verdana"
                }
              }
            }
            '''

        net = Network(
            notebook=False,
            cdn_resources='in_line',
            height='1000px',
            width='100%',
            bgcolor="#222222",
            font_color="white"
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