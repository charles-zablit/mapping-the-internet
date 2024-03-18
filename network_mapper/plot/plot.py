import argparse
import csv
import json
import pathlib
from typing import Dict, Tuple

import geoip2.database
import geoip2.errors
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from mpl_toolkits.basemap import Basemap


def read_json(path: pathlib.Path) -> Dict[str, Dict[str, int]]:
    with open(path, "r") as f:
        return json.load(f)


def read_countries(path: pathlib.Path) -> Dict[str, Tuple[float, float]]:
    res = {}
    with open(path, "r") as f:
        csv_reader = csv.reader(
            f,
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            skipinitialspace=True,
        )
        for row in csv_reader:
            if csv_reader.line_num == 1:
                continue
            res[row[1]] = (float(row[4]), float(row[5]))
    return res


def main(db_path: str, edges_path: str, targets_path: str) -> None:
    countries = read_countries(pathlib.Path("./countries.csv"))
    path = pathlib.Path(edges_path)
    data = read_json(path)
    ip_targets = set()
    path = pathlib.Path(targets_path)
    with open(path, "r") as f:
        for line in f:
            ip_targets.add(line.strip())

    reader = geoip2.database.Reader(db_path)
    graph = nx.DiGraph()
    pos = {}
    for src_ip, targets in data.items():
        graph.add_node(src_ip)
        for target_ip, count in targets.items():
            graph.add_node(target_ip)
            graph.add_edge(src_ip, target_ip, weight=np.log2(count))
    nodes = list(graph.nodes)
    for node in nodes:
        try:
            response = reader.country(node)
            (lat, lon) = countries[response.country.iso_code]
            # pos[node] = (response.location.longitude, response.location.latitude)
            pos[node] = (lon, lat)
        except geoip2.errors.AddressNotFoundError:
            print("Address not found")
            graph.remove_node(node)
    plt.figure(figsize=(12, 6))
    m = Basemap(
        projection="cyl",
        resolution="l",
        suppress_ticks=True,
    )
    node_color = ["r" if node in ip_targets else "g" for node in graph.nodes]
    node_size = [50 if node in ip_targets else 20 for node in graph.nodes]
    nx.draw_networkx_nodes(
        G=graph,
        pos=pos,
        node_color=node_color,
        alpha=0.8,
        node_size=node_size,
    )
    r_patch = mpatches.Patch(color="r", label="Targets")
    g_patch = mpatches.Patch(color="g", label="Routers")
    plt.legend(handles=[r_patch, g_patch])
    _, weights = zip(*nx.get_edge_attributes(graph, "weight").items())
    nx.draw_networkx_edges(
        G=graph,
        pos=pos,
        edge_color=weights,
        alpha=0.2,
        arrows=False,
        edge_cmap=matplotlib.cm.turbo,
        edge_vmin=3,
        edge_vmax=7,
    )
    m.drawcountries(linewidth=0.5)
    m.drawstates(linewidth=0.2)
    m.drawcoastlines(linewidth=1)
    plt.title(
        f"Internet Map\n{len(ip_targets)} targets, {len(graph.nodes)} nodes, {len(graph.edges)} edges"
    )
    plt.tight_layout()
    plt.savefig("./map_1.png", format="png", dpi=300)
    plt.show()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--db-path", type=str, help="Path to the GeoLite2-City.mmdb")
    args.add_argument(
        "--edges-path", type=str, help="Path to the edges file", default="../edges.json"
    )
    args.add_argument(
        "--targets-path",
        type=str,
        help="Path to the targets file",
        default="../done.csv",
    )
    args = args.parse_args()

    main(args.db_path, args.edges_path, args.targets_path)
