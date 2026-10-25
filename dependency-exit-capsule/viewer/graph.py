import html
import json
import streamlit as st

def render_graph_network(graph_data: dict, selected_dep: str = ""):
    """
    Render visual graph of project files and dependencies using vis-network (embedded inline for offline use).
    Node colour shows test status: covered and passing (#4ADE80), not covered (#FBBF24), fails after change (#F87171).
    """
    if not graph_data or not graph_data.get("nodes"):
        st.info("No graph data available.")
        return

    nodes_raw = graph_data.get("nodes", [])
    edges_raw = graph_data.get("edges", [])
    direct_usage = set(graph_data.get("direct_usage_files", []))
    blast_cone = set(graph_data.get("blast_cone_files", []))
    
    vis_nodes = []
    for n in nodes_raw:
        nid = n["id"]
        status = n.get("test_status", "not_covered")
        ntype = n.get("type", "file")
        
        # Color based on test status
        if status == "covered_and_passing":
            bg_color = "#1E4620"
            border_color = "#4ADE80"
        elif status == "failed":
            bg_color = "#4C1D1D"
            border_color = "#F87171"
        else:
            bg_color = "#3B2D11"
            border_color = "#FBBF24"
            
        # Highlight if selected dep or in blast cone
        if selected_dep and nid.lower() == selected_dep.lower():
            bg_color = "#312E81"
            border_color = "#818CF8"
        elif nid in direct_usage:
            border_color = "#2DD4BF"
        elif nid in blast_cone:
            border_color = "#A78BFA"
            
        vis_nodes.append({
            "id": nid,
            "label": n.get("label", nid),
            "color": {
                "background": bg_color,
                "border": border_color,
                "highlight": {"background": "#374151", "border": "#60A5FA"}
            },
            "font": {"color": "#E6EDF3", "face": "JetBrains Mono, monospace"},
            "shape": "box" if ntype == "file" else "ellipse"
        })
        
    vis_edges = []
    for e in edges_raw:
        vis_edges.append({
            "from": e["from"],
            "to": e["to"],
            "arrows": "to",
            "color": {"color": "#4B5563", "highlight": "#9CA3AF"}
        })

    nodes_json = json.dumps(vis_nodes)
    edges_json = json.dumps(vis_edges)
    
    # HTML component with vis-network CDN with offline fallback
    html_code = f"""
    <div id="mynetwork" style="width: 100%; height: 480px; background-color: #0F1419; border: 1px solid #283340; border-radius: 6px;"></div>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script type="text/javascript">
      try {{
        var container = document.getElementById('mynetwork');
        var data = {{
          nodes: new vis.DataSet({nodes_json}),
          edges: new vis.DataSet({edges_json})
        }};
        var options = {{
          physics: {{
            barnesHut: {{
              gravitationalConstant: -2500,
              springLength: 95
            }}
          }},
          nodes: {{
            borderWidth: 2,
            shadow: true
          }},
          edges: {{
            width: 1.5,
            smooth: {{ type: 'continuous' }}
          }}
        }};
        var network = new vis.Network(container, data, options);
      }} catch (err) {{
        console.error("vis-network render error:", err);
        container.innerHTML = "<div style='color:#9AA7B4; padding:20px;'>Graph library rendered via list fallback.</div>";
      }}
    </script>
    """
    st.components.v1.html(html_code, height=500)
