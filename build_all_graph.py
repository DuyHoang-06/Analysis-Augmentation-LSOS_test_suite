import json
import os
import networkx as nx
import matplotlib.pyplot as plt


INPUT_JSON = "all_grouped_tests.json"
OUTPUT_DIR = "graphs"


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_class_graph(class_name, test_cases):
    graph = nx.DiGraph()

    graph.add_node(class_name, type="class")

    for tc in test_cases:

        test_name = tc.get("test_name")

        if not test_name:
            continue

        graph.add_node(test_name, type="test")
        graph.add_edge(class_name, test_name)

        # thêm function nodes
        for func in tc.get("called_functions", []):

            graph.add_node(func, type="function")
            graph.add_edge(test_name, func)

    return graph


def draw_graph(graph, output_path):

    plt.figure(figsize=(16, 12))

    pos = nx.spring_layout(
        graph,
        seed=42,
        k=1.5
    )

    node_types = nx.get_node_attributes(graph, "type")

    class_nodes = [
        n for n, t in node_types.items()
        if t == "class"
    ]

    test_nodes = [
        n for n, t in node_types.items()
        if t == "test"
    ]

    function_nodes = [
        n for n, t in node_types.items()
        if t == "function"
    ]

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=class_nodes,
        node_size=1500,
        alpha=0.9,
        node_color="orange",
        label="Class"
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=test_nodes,
        node_size=1000,
        alpha=0.9,
        node_color="skyblue",
        label="Test"
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=function_nodes,
        node_size=700,
        alpha=0.8,
        node_color="lightgreen",
        label="Function"
    )

    nx.draw_networkx_edges(
        graph,
        pos,
        arrows=True,
        alpha=0.5
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=7
    )

    plt.axis("off")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    data = load_data(INPUT_JSON)

    total = 0

    for class_name, test_cases in data.items():

        graph = build_class_graph(
            class_name,
            test_cases
        )

        output_file = os.path.join(
            OUTPUT_DIR,
            f"{class_name}.png"
        )

        draw_graph(
            graph,
            output_file
        )

        print(
            f"[OK] {class_name} -> "
            f"{graph.number_of_nodes()} nodes, "
            f"{graph.number_of_edges()} edges"
        )

        total += 1

    print(f"\nGenerated {total} graph files.")


if __name__ == "__main__":
    main()