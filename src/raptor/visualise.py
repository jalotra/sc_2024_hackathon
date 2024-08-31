
from .tree_structures import Tree, Node
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
import pickle
from ..routes.DocumentRoutes import read_redis_document
from ..routes.DocumentRoutes import get_redis_db

# Formats data so that plotly can plot it better, 
# each line should have less than 80 characters and 
# take care of generated new lines chars
def format_plotted_data(s : str):
    lines = s.split("\n")
    final_lines = [] 
    for line in lines:
        while len(line) > 80:
            final_lines.append(line[:80])
            line = line[80:]
        final_lines.append(line)
    
    return "<br>".join(final_lines)


def create_figure(Xe, Ye, Xn, Yn, labels):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                    y=Ye,
                    mode='lines',
                    line=dict(color='rgb(210,210,210)', width=1),
                    hoverinfo='none'
                    ))
    fig.add_trace(go.Scatter(x=Xn,
                    y=Yn,
                    mode='markers',
                    name='bla',
                    marker=dict(symbol='circle-dot',
                                    size=18,
                                    color='#6175c1',    #'#DB4551',
                                    line=dict(color='rgb(50,50,50)', width=1)
                                    ),
                    text=list(map(lambda x : format_plotted_data(x), labels)),
                    hoverinfo='text',
                    opacity=0.8
                    ))

    return fig



def create_igraph_tree(graph : Graph, node : Node, tree : Tree, parent_id : int = -1):
    node_id = graph.vcount()
    graph.add_vertex(name=f"Node Index : {node.index}, Node Text : {node.text}",
                    index=node.index,
                    embeddings=node.embeddings)
    
    if parent_id != -1:
        graph.add_edge(parent_id, node_id)
    
    for child_index in node.children:
        print(child_index, type(child_index))
        print(type(tree))
        child_node = find_node_by_index(child_index, tree)
        create_igraph_tree(graph, child_node, tree, node_id)
    
    return node_id


def find_node_by_index(child_index, tree):
    print(child_index, type(child_index))
    print(type(tree))
    for node_index in tree.all_nodes.keys():
        node = tree.all_nodes[node_index]
        if node.index == child_index:
            return node
    
    raise Exception(f"Not able to find the Node with index : {child_index}")
    


def visual(node : Node, tree : Tree) :
    # Assuming the tree is properly linked
    G = Graph()
    create_igraph_tree(G, node, tree)

    # Layout and visualization
    lay = G.layout('rt')
    position = {k: lay[k] for k in range(G.vcount())}
    Y = [lay[k][1] for k in range(G.vcount())]
    M = max(Y)

    es = EdgeSeq(G)
    E = [e.tuple for e in G.es]
    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe += [position[edge[0]][0], position[edge[1]][0], None]
        Ye += [2*M-position[edge[0]][1], 2*M-position[edge[1]][1], None]

    labels = [v['name'] for v in G.vs]

    fig = create_figure(Xe, Ye, Xn, Yn, labels)

    axis = dict(showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
            )

    fig.update_layout(title= 'Example Tree Node',
                    font_size=12,
                    showlegend=False,
                    xaxis=axis,
                    yaxis=axis,
                    margin=dict(l=40, r=40, b=85, t=100),
                    hovermode='closest',
                    plot_bgcolor='rgb(248,248,248)'
                )

    fig.show()

if __name__ == "__main__":

    tree_id = "RAG_1eebcf72-2ad6-423f-8a8f-8ee153d73d27"

    redis_picked_tree = read_redis_document(
            redis_conn=next(get_redis_db()), document_key=tree_id
        )
    if redis_picked_tree is None:
        raise Exception(f"No tree found with tree id : {tree_id}")

    tree = pickle.loads(redis_picked_tree.value)
    root_node = Node(
        text = "This is placeholder fellas; made for my ease !",
        index= -1, 
        children=tree.root_nodes, 
        embeddings=[]
    )
    
    visual(root_node, tree)


