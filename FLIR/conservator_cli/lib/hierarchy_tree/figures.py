from matplotlib import pyplot, colors
from networkx import DiGraph
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

from FLIR.conservator_cli.lib.hierarchy_tree.graphs import get_depth_for_each_node


def plot_graph(graph: DiGraph, dst_path: str, s=30, font_size=10, dpi=300):

    depth_to_node = get_depth_for_each_node(graph, 'entity.n.01')
    hsv_to_color = {color: colors.rgb_to_hsv(colors.to_rgb(color)) for color in colors.TABLEAU_COLORS.keys()}
    chosen_colors = sorted(hsv_to_color.items(), key=lambda x: x[1][0], reverse=True)
    chosen_colors = [i[0] for i in chosen_colors]

    pyplot.figure(figsize=(s, s))
    nx.draw(
        graph,
        pos=graphviz_layout(graph, prog='fdp'), # possible layouts: neato, dot, twopi, circo, fdp, nop, wc, acyclic, gvpr, gvcolor, ccomps, sccmap, tred, sfdp, unflatten
        with_labels=True,
        node_size=[1200 - 50 * depth_to_node[node] for node in graph.nodes()],
        node_color=[chosen_colors[depth_to_node[node] // 2] for node in graph.nodes()],
        font_size=font_size,
    )
    # pyplot.show()
    pyplot.savefig(dst_path, dpi=dpi)
