from networkx.readwrite import json_graph
import json
import networkx as nx


class AppState():

    def __init__(self, graph=None):
        if graph is not None and not isinstance(graph, nx.Graph):
            raise TypeError("graph must be a networkx Graph")

        self.graph = graph
        self.logs = []

    def get_graph(self):
        return self.graph

    def set_graph(self, graph):
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph must be a networkx Graph")

        self.graph = graph

    def add_edge(self, source: str, relation: str, target: str):
        for i in [source, relation, target]:
            if not isinstance(i, str):
                raise TypeError("arguments must be strings")

        if self.graph is None:
            self.graph = nx.DiGraph()

        self.graph.add_node(source)
        self.graph.add_node(target)
        self.graph.add_edge(
            source,
            target,
            label=relation
        )

    def add_edges(self, graph_json: dict):
        # TODO
        pass

    def serialize_graph(self):
        if self.graph is None:
            return json.dumps({"nodes": [], "edges": []})

        data = json_graph.node_link_data(self.graph)

        print("Dumped graph:")
        print(data)

        return json.dumps(data)

    def deserialize_graph(self, graph_json: str):
        if not isinstance(graph_json, str):
            raise TypeError("graph_json must be a string")

        data = json.loads(graph_json)

        self.graph = json_graph.node_link_graph(data)

        return self.graph

    def get_logs(self):
        return self.logs

    def append_log(self, text: str, entities, relations):
        self.logs.append({
            "text": text,
            "entities": entities,
            "relations": relations
        })

