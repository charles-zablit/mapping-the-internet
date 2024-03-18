import json


def convert_to_csv(input_file: str, output_file: str):
    output = []

    with open(input_file) as f:
        content: dict = json.load(f)
    count = 0
    for page in content:
        links = set(page["links"])
        node_link = page["url"].split("/")[-1]
        count += len(links)
        output.append(f"{node_link};{';'.join(links)}\n")
    print("number of edges", count, "number of nodes", len(content))
    with open(output_file, "w") as f:
        f.writelines(output)


def convert_to_dot(
    input_file: str,
    output_file: str,
):
    output = ["digraph wikipedia {\n"]
    id_table = {}

    with open(input_file) as f:
        content: list[dict] = json.load(f)
    content = content[:-1]
    count = 0
    for page in content:
        id_table[page["url"].split("/")[-1]] = str(len(id_table))

    for page in content:
        title = page["title"].replace('"', '\\"')
        links = [
            id_table.get(link)
            for link in set(page["links"])
            if id_table.get(link)
        ]
        node_id = id_table[page["url"].split("/")[-1]]
        count += len(links)
        output.append(f"{node_id} -> {{{';'.join(links)}}};\n")
        output.append(f"""{node_id} [label = "{title}"];\n""")
    output.append("}")
    print("number of edges", count, "number of nodes", len(content))

    with open(output_file, "w") as f:
        f.writelines(output)


if __name__ == "__main__":
    convert_to_dot("output.json", "graph.dot")
