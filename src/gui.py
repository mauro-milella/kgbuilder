import json
import networkx as nx
from pyvis.network import Network

import streamlit as st
import streamlit.components.v1 as components

from src.model import Model
from src.state import AppState


class GraphAppUI:

    def __init__(self):
        self.model = Model()

        if "app_state" not in st.session_state:
            st.session_state.app_state = AppState()

    @property
    def state(self):
        return st.session_state.app_state

    def _render_graph(self):
        graph = self.state.get_graph()

        if graph is None or graph.number_of_nodes() == 0:
            st.info("There is no graph to display.")
            return

        net = Network(height="500px", width="100%", directed=True)

        for node in graph.nodes():
            net.add_node(node, label=str(node))

        for u, v, data in graph.edges(data=True):
            net.add_edge(u, v, label=data.get("label", ""))

        # TODO: make this a temporary file
        net.save_graph("graph.html")

        with open("graph.html", "r", encoding="utf-8") as f:
            html = f.read()

        components.html(html, height=520)

    def _upload_graph(self):
        uploaded = st.file_uploader("Upload Graph JSON", type=["json"])

        if uploaded is not None:
            try:
                content = uploaded.read().decode("utf-8")
                self.state.deserialize_graph(content)
                st.success("Graph loaded successfully.")
            except Exception as e:
                st.error(f"Failed to load graph: {e}")

    def _save_graph(self):
        if st.button("Save Graph"):
            data = self.state.serialize_graph()
            st.download_button(
                label="Download Graph JSON",
                data=data,
                file_name="graph.json",
                mime="application/json"
            )

    def _extract_text(self):
        text = st.text_area("Input text")

        if st.button("Extract Graph"):
            if not text.strip():
                st.warning("Hey, enter some text here.")
                return

            try:
                result = self.model.extract(text)

                entities = result.get("entities", [])
                relations = result.get("relations", [])

                for r in relations:
                    self.state.add_edge(
                        r["source"],
                        r["relation"],
                        r["target"]
                    )

                self.state.append_log(text, entities, relations)

                st.success(f"Extracted {len(entities)} entities and {
                           len(relations)} relations.")

                st.rerun()

            except Exception as e:
                st.error(f"Extraction failed: {e}")

    def _render_logs(self):
        st.subheader("Logging")

        logs = self.state.get_logs()

        if not logs:
            st.info("No extraction logs yet.")
            return

        for (i, entry) in enumerate(reversed(logs), 1):
            with st.expander(
                    f"Extraction #{len(logs) - i + 1}", expanded=False):
                st.markdown("**Input Text**")
                st.write(entry["text"])

                st.markdown("**Entities**")
                st.write(entry["entities"])

                st.markdown("**Relations**")
                st.write(entry["relations"])

    def build(self):
        st.set_page_config(layout="wide")
        st.title("Graph Builder")

        col1, col2 = st.columns([1, 2], gap="large")

        with col1:
            st.subheader("Controls")
            self._extract_text()
            self._upload_graph()
            self._save_graph()

        with col2:
            st.subheader("Inspection")
            self._render_graph()

        st.divider()

        self._render_logs()

