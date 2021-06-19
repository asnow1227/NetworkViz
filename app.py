import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
import networkx as nx
import pandas as pd
import json
from jupyter_dash import JupyterDash
from flask import jsonify
import dash_table



G = nx.DiGraph()
df = pd.read_csv('network.csv')
attrs = pd.read_csv('attrs.csv')
attrs.set_index('id', inplace=True)
model_info = pd.read_csv('models.csv')
model_info.set_index('id', inplace=True)
usage_info = pd.read_csv('usages.csv')
usage_info.set_index('id', inplace=True)
G = nx.from_pandas_edgelist(df, create_using=nx.DiGraph())
nx.set_node_attributes(G, attrs.to_dict('index'))
nx.set_node_attributes(G, model_info.to_dict('index'))
nx.set_node_attributes(G, usage_info.to_dict('index'))
R = G.reverse()
root = list(G.nodes())[0]
app = JupyterDash(external_stylesheets=[dbc.themes.SLATE])


def get_node_class(node):
    rating = G.nodes[node]['rating']
    return f'circle {rating}' if G.nodes[node]['object_type'] == ' model' else f'triangle {rating}'



def load_graph(source, depth, orientation='both', keep=[' model', ' usages']):
    #tree = nx.descendants_at_distance(G, source, depth)
    forward_tree = nx.dfs_tree(G, source=source, depth_limit=depth)
    backward_tree = nx.dfs_tree(R, source=source, depth_limit=depth)
    elements = []
    print([G.nodes[node]['object_type'] for node in forward_tree.nodes])
    print([G.nodes[node]['object_type'] for node in backward_tree.nodes])
    forward_nodes = [
        {
            'data': {'id': node, 'label': node},
            'classes': get_node_class(node)
        }
        for node in forward_tree.nodes if G.nodes[node]['object_type'] in keep or node == source
    ]
    backward_nodes = [
        {
            'data': {'id': node, 'label': node},
            'classes': get_node_class(node)
        }
        for node in backward_tree.nodes if G.nodes[node]['object_type'] in keep or node == source
    ]

    forward_edges = [
        {
            'data': {'source': target, 'target': src},
            'classes': 'grey_arrow' if G.nodes[target]['object_type'] == ' usage' else 'grey_arrow'
        }
        for src, target in forward_tree.edges if (G.nodes[src]['object_type'] in keep and G.nodes[target]['object_type'] in keep) or (src == source and G.nodes[target]['object_type'] in keep)
    ]
    backward_edges = [
        {
            'data': {'source': src, 'target': target},
            'classes': 'grey_arrow' if G.nodes[target]['object_type'] == ' usage' else 'grey_arrow'
        }
        for src, target in backward_tree.edges if (G.nodes[src]['object_type'] in keep and G.nodes[target]['object_type'] in keep) or (src == source and G.nodes[target]['object_type'] in keep)
    ]
    if orientation == 'both' or orientation == 'downstream':
        elements.extend(forward_nodes)
        elements.extend(forward_edges)
    if orientation == 'both' or orientation == 'upstream':
        elements.extend(backward_nodes)
        elements.extend(backward_edges)
    #print(elements)
    print(orientation)
    return elements

def draw_cyto(elements):
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='demo-dropdown',
                        options=[
                        {'label': node, 'value': node}
                        for node in G.nodes
                        ],
                        value=root)
                ], width=8),
                dbc.Col([
                    dcc.Dropdown(
                        id='depth-input',
                        options=[
                        {'label': i, 'value': i}
                        for i in range(10)
                        ],
                        value=1)
                ], width=2),
                dbc.Col([
                    html.Button('Submit', id='submit-button')
                ], width=2)
            ], align='center', no_gutters=True),
            html.Br(),
            dbc.Row([
                dbc.Col([
                     html.Div([
                        cyto.Cytoscape(
                            id='cytoscape',
                            stylesheet=[
                                {
                                    'selector': 'node',
                                    'style': {
                                        'label': 'data(id)'
                                    }
                                },
                                {
                                    'selector': '.triangle',
                                    'style': {
                                        'shape': 'triangle'
                                    }
                                },
                                {
                                    'selector': '.circle',
                                    'style': {
                                        'shape': 'circle'
                                    }
                                },
                                {
                                    'selector': '.red',
                                    'style': {
                                        'background-color': 'red',
                                        'line-color': 'red'
                                    }
                                },
                                {
                                    'selector': '.low',
                                    'style': {
                                        'background-color': '#8EFF4D',
                                        'line-color': '#8EFF4D'
                                    }
                                },
                                {
                                    'selector': '.med',
                                    'style': {
                                        'background-color': '#E4FA29',
                                        'line-color': '#E4FA29'
                                    }
                                },
                                {
                                    'selector': '.high',
                                    'style': {
                                        'background-color': '#F89A0B',
                                        'line-color': '#F89A0B'
                                    }
                                },
                                {
                                    'selector': '.crit',
                                    'style': {
                                        'background-color': '#F3480C',
                                        'line-color': '#F3480C'
                                    }
                                },
                                {
                                    'selector': '.blue',
                                    'style': {
                                        'background-color': 'blue',
                                        'line-color': 'blue'
                                    }
                                },
                                {
                                    'selector': '.blue_arrow',
                                    'style': {
                                        'background-color': 'blue',
                                        'line-color': 'blue',
                                        'source-arrow-color': 'blue'
                                    }
                                },
                                {
                                    'selector': '.red_arrow',
                                    'style': {
                                        'background-color': 'red',
                                        'line-color': 'red',
                                        'source-arrow-color': 'red'
                                    }
                                },
                                {
                                    'selector': '.grey_arrow',
                                    'style': {
                                        'background-color': 'grey',
                                        'line-color': 'grey',
                                        'source-arrow-color': 'grey'
                                    }
                                },
                                {
                                    'selector': '.black_arrow',
                                    'style': {
                                        'background-color': 'black',
                                        'line-color': 'black',
                                        'source-arrow-color': 'black'
                                    }
                                },
                                {
                                    'selector': 'edge',
                                    'style': {
                                        # The default curve style does not work with certain arrows
                                        'curve-style': 'bezier',
                                        # 'source-arrow-color': 'red',
                                        'source-arrow-shape': 'triangle'
                                        # 'line-color': 'red'
                                    }
                                }],
                            elements=elements,
                            style={'width': '100%', 'height': '300px'}
                        )
                    ])
                ])
            ])
        ]), color='light') 

global current_cyto
current_cyto = [draw_cyto(load_graph(root, 2))]

def draw_dropdown():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                # dbc.Row([
                #     dbc.Col([
                #         html.Div([
                #             dcc.Dropdown(
                #                 id='demo-dropdown',
                #                 options=[
                #                 {'label': node, 'value': node}
                #                 for node in G.nodes
                #                 ],
                #                 value=root
                #             )
                #         ])
                #     ], width=12)
                # ]),
                # html.Br(),
                # html.Br(),
                # dbc.Row([
                #         html.Div([
                #         dcc.Input('depth-input', value=1)
                #     ])
                # ]),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                         html.Div([
                            html.Button('Submit', id='submit-button')
                        ])
                    ], width=12)
                ])
            ]),
        style={'height': '400px'})  
    ])



app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("Dash Cytoscape:"),
                        dcc.Dropdown(
                            id='dropdown-update-layout',
                            value='grid',
                            clearable=False,
                            options=[
                                {'label': name.capitalize(), 'value': name}
                                for name in ['grid', 'random', 'circle', 'cose', 'concentric']
                            ]
                        )
                    ]),
                ], width=3),
                dbc.Col([
                    html.Div([
                        dcc.RadioItems(
                            options=[
                                {'label': 'Upstream Only', 'value': 'upstream'},
                                {'label': 'Downstream Only', 'value': 'downstream'},
                                {'label': 'Upstream and Downstream', 'value': 'both'}
                            ],
                            value='both',
                            id='graph-orientation'
                        )
                    ])
                ], width=3),
                dbc.Col(
                    html.Div([
                        html.H4('Show In Network'),
                        dcc.Checklist(
                            options=[
                                {'label': 'Usages', 'value': ' usage'},
                                {'label': 'Models', 'value': ' model'},
                            ],
                            value=['usage', 'model'],
                            labelStyle={'display': 'inline-block'},
                            id='show-in-nx'
                        )  
                    ])
                , width=3),
                dbc.Col([
                    html.Div(className='four columns', children=[
                        # dcc.Tabs(id='tabs-image-export', children=[
                        #     dcc.Tab(label='generate jpg', value='jpg'),
                        #     dcc.Tab(label='generate png', value='png')
                        # ]),
                        # html.Div(
                        #     # style=styles['tab'], 
                        #     children=[
                        #     html.Div(
                        #         id='image-text',
                        #         children='image data will appear here'
                        #         # style=styles['output']
                        #     )
                        # ]),
                        html.Div('Download graph:'),
                        html.Button("as jpg", id="btn-get-jpg"),
                        html.Button("as png", id="btn-get-png"),
                        html.Button("as svg", id="btn-get-svg")
                    ])
                ], width=3),
            ], align='left'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id='cyto-placeholder', 
                        children=current_cyto
                    )
                ], width=9),
                dbc.Col([
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader("Card Header"),
                            dbc.ListGroup(
                            [
                                dbc.ListGroupItem("Item 1"),
                                dbc.ListGroupItem("Item 2"),
                                dbc.ListGroupItem("Item 3"),
                            ],
                            flush=False
                            )
                        ])
                    ], id='list-group')
                ], width=3)
                # dbc.Col([
                #     draw_dropdown()
                # ], width=4)
            ], align='center')
        ]), color='dark'
    )
])

@app.callback(Output('cytoscape', 'layout'),
              Input('dropdown-update-layout', 'value'))
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
    }

@app.callback(
    [
        Output('cyto-placeholder', 'children'), 
        Output('demo-dropdown', 'value'),
        Output('depth-input', 'value')
    ],
    [
        Input('submit-button', 'n_clicks'),
        State('demo-dropdown', 'value'),
        State('depth-input', 'value'),
        State('graph-orientation', 'value'),
        State('show-in-nx', 'value')
    ]
)
def update_ui(n_clicks, ID, depth, orientation, keep):
    if n_clicks == 0:
        return [draw_cyto(load_graph(root, 2, orientation=orientation, keep=keep))]
    return [draw_cyto(load_graph(ID, int(depth), orientation=orientation, keep=keep))], ID, depth


@app.callback(
    [
        Output('list-group', 'children')
    ],
    [
        Input('cytoscape', 'tapNodeData')
    ]
)
def update_list_group(data):
    if data is None:
        return [dbc.Card([
            dbc.CardHeader("Card Header"),
            dbc.ListGroupItem("Node Info Will Appear Here")
        ])]
    node = G.nodes[data['id']]
    items_list = []
    for key, value in node.items():
        items_list.append(dbc.ListGroupItemHeading(key, style={'font-size': '10px', 'height': '3px', 'text-align': 'center'})),
        items_list.append(dbc.ListGroupItemText(value, style={'font-size': '7px', 'text-align': 'center'}))


    return [
        dbc.Card(
            [dbc.CardHeader(data["id"], style={'font-size': '10px', 'text-align': 'center'})]
            + items_list
        )
    ]
    
    
@app.callback(
    Output("cytoscape", "generateImage"),
    [
        # Input('tabs-image-export', 'value'),
        Input("btn-get-jpg", "n_clicks"),
        Input("btn-get-png", "n_clicks"),
        Input("btn-get-svg", "n_clicks"),
    ])
def get_image(get_jpg_clicks, get_png_clicks, get_svg_clicks):

    # File type to output of 'svg, 'png', 'jpg', or 'jpeg' (alias of 'jpg')
    ftype = 'jpg' if get_jpg_clicks else 'png'

    # 'store': Stores the image data in 'imageData' !only jpg/png are supported
    # 'download'`: Downloads the image as a file with all data handling
    # 'both'`: Stores image data and downloads image as file.
    action = 'store'

    ctx = dash.callback_context
    if ctx.triggered:
        input_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if input_id != "tabs":
            action = "download"
            ftype = input_id.split("-")[-1]

    return {
        'type': ftype,
        'action': action
        }
                


if __name__ == '__main__':
    app.run_server(port=10000,debug=True)