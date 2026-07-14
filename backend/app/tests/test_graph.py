from app.graph.workflow import build_graph


def test_graph_has_all_expected_nodes():
    graph = build_graph()
    nodes = list(graph.nodes.keys())

    expected = {
        "__start__",
        "metrics_start",
        "validate",
        "preprocess",
        "detect",
        "extract_mouth",
        "tensorize",
        "infer",
        "decode",
        "metrics_end",
        "error",
    }

    assert set(nodes) == expected
