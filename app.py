import json
import os

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
#from demos import dash_reusable_components as drc


import dash_core_components as dcc
import dash_html_components as html
from dash_extensions.enrich import DashProxy, MultiplexerTransform


# Display utility functions
def _merge(a, b):
    return dict(a, **b)


def _omit(omitted_keys, d):
    return {k: v for k, v in d.items() if k not in omitted_keys}


# Custom Display Components
def Card(children, **kwargs):
    return html.Section(
        children,
        style=_merge(
            {
                'padding': 20,
                'margin': 5,
                'borderRadius': 5,
                'border': 'thin lightgrey solid',
                'background-color': 'white',

                # Remove possibility to select the text for better UX
                'user-select': 'none',
                '-moz-user-select': 'none',
                '-webkit-user-select': 'none',
                '-ms-user-select': 'none'
            },
            kwargs.get('style', {})
        ),
        **_omit(['style'], kwargs)
    )


def SectionTitle(title, size, align='center', color='#222'):
    return html.Div(
        style={
            'text-align': align,
            'color': color
        },
        children=dcc.Markdown('#' * size + ' ' + title),
    )


def NamedCard(title, size, children, **kwargs):
    size = min(size, 6)
    size = max(size, 1)

    return html.Div([
        Card(
            [SectionTitle(title, size, align='left')] + children,
            **kwargs
        )
    ])


def NamedSlider(name, **kwargs):
    return html.Div(
        style={'padding': '20px 10px 25px 4px'},
        children=[
            html.P(f'{name}:'),
            html.Div(
                style={'margin-left': '6px'},
                children=dcc.Slider(**kwargs)
            )
        ]
    )


def NamedDropdown(name, **kwargs):
    return html.Div(
        style={'margin': '10px 0px'},
        children=[
            html.P(
                children=f'{name}:',
                style={'margin-left': '3px'}
            ),

            dcc.Dropdown(**kwargs)
        ]
    )


def NamedRadioItems(name, **kwargs):
    return html.Div(
        style={'padding': '20px 10px 25px 4px'},
        children=[
            html.P(children=f'{name}:'),
            dcc.RadioItems(**kwargs)
        ]
    )


def NamedInput(name, **kwargs):
    return html.Div(
        children=[
            html.P(children=f'{name}:'),
            dcc.Input(**kwargs)
        ]
    )


# Utils
def DropdownOptionsList(*args):
    return [{'label': val.capitalize(), 'value': val} for val in args]


#
#
#
#
#
#
# Load extra layouts
cyto.load_extra_layouts()


asset_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '.', 'assets'
)

#app = dash.Dash(__name__, assets_folder=asset_path)
app = DashProxy(__name__, assets_folder=asset_path,
                prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
server = app.server


# ###################### DATA PREPROCESSING ######################
# Load data
with open('data/test.txt', 'r') as f:
    network_data = f.read().split('\n')

# We select the first 750 edges and associated nodes for an easier visualization
edges = network_data[:750]
nodes = set()

following_node_di = {}  # user id -> list of users they are following
following_edges_di = {}  # user id -> list of cy edges starting from user id

followers_node_di = {}  # user id -> list of followers (cy_node format)
followers_edges_di = {}  # user id -> list of cy edges ending at user id

cy_edges = []
cy_nodes = []
list_breeds = []
for edge in edges:
    if " " not in edge:
        continue

    source, target, color = edge.split(" ")
    if color == 'blue':
        list_breeds.append(source)

    cy_edge = {'data': {'id': source + target,
                        'source': source, 'target': target}}
    cy_target = {"data": {"id": target, "label": "User #" + str(target), 'color': color}}
    cy_source = {"data": {"id": source, "label": "User #" + str(source), 'color': color}}

    if source not in nodes:
        nodes.add(source)
        cy_nodes.append(cy_source)
    if target not in nodes:
        nodes.add(target)
        cy_nodes.append(cy_target)

    # Process dictionary of following
    if not following_node_di.get(source):
        following_node_di[source] = []
    if not following_edges_di.get(source):
        following_edges_di[source] = []

    following_node_di[source].append(cy_target)
    following_edges_di[source].append(cy_edge)

    # Process dictionary of followers
    if not followers_node_di.get(target):
        followers_node_di[target] = []
    if not followers_edges_di.get(target):
        followers_edges_di[target] = []

    followers_node_di[target].append(cy_source)
    followers_edges_di[target].append(cy_edge)

list_breeds = set(list_breeds)
genesis_node = cy_nodes[0]
genesis_node['classes'] = "genesis"
default_elements = [genesis_node]

default_stylesheet = [
    {
        "selector": 'node',
        'style': {
            "opacity": 0.65,
            'z-index': 9999
        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.45,
            'z-index': 5000
        }
    },
    {
        'selector': '.followerNode',
        'style': {
            'background-color': '#0074D9'
        }
    },
    {
        'selector': '.followerEdge',
        "style": {
            "mid-target-arrow-color": "blue",
            "mid-target-arrow-shape": "vee",
            "line-color": "#0074D9"
        }
    },
    {
        'selector': '.followingNode',
        'style': {
            'background-color': '#FF4136'
        }
    },
    {
        'selector': '.followingEdge',
        "style": {
            "mid-target-arrow-color": "red",
            "mid-target-arrow-shape": "vee",
            "line-color": "#FF4136",
        }
    },
    {
        "selector": '.genesis',
        "style": {
            'background-color': '#B10DC9',
            "border-width": 2,
            "border-color": "purple",
            "border-opacity": 1,
            "opacity": 1,

            "label": "data(label)",
            "color": "#B10DC9",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    },
    {
        'selector': ':selected',
        "style": {
            "border-width": 2,
            "border-color": "black",
            "border-opacity": 1,
            "opacity": 1,
            "label": "data(label)",
            "color": "black",
            "font-size": 12,
            'z-index': 9999
        }
    }
]

# ################################# APP LAYOUT ################################
styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 80px)'}
}

app.layout = html.Div([
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            layout={'name': 'cola'},
            elements=default_elements,
            stylesheet=[
                # Group selectors
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)',
                        'color': 'data(color)',
                        'z-index': 9999
                    }
                },
                {
                    "selector": 'edge',
                    'style': {
                        "curve-style": "bezier",
                        "opacity": 0.45,
                        'z-index': 5000
                    }
                },
                {
                    'selector': '.followerNode',
                    'style': {
                        'background-color': 'data(color)'
                    }
                },
                {
                    'selector': '.followingNode',
                    'style': {
                        'background-color': 'data(color)'
                    }
                },
                {
                    'selector': ':selected',
                    "style": {
                        "border-width": 2,
                        "border-color": "black",
                        "border-opacity": 1,
                        "opacity": 1,
                        "label": "data(label)",
                        "color": "data(color)",
                        "font-size": 12,
                        'z-index': 9999
                    }
                }
            ],
            style={
                'height': '95vh',
                'width': '100%'
            }
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Control Panel', children=[
                NamedDropdown(
                    name='Breed',
                    id='dropdown-breed',
                    options=DropdownOptionsList(
                        *list_breeds
                    ),
                    value='???????????????',
                    clearable=False
                ),
                NamedRadioItems(
                    name='Expand',
                    id='radio-expand',
                    options=DropdownOptionsList(
                        'followers',
                        'following'
                    ),
                    value='followers'
                )
            ]),

            dcc.Tab(label='JSON', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Node Object JSON:'),
                    html.Pre(
                        id='tap-node-json-output',
                        style=styles['json-output']
                    ),
                    html.P('Edge Object JSON:'),
                    html.Pre(
                        id='tap-edge-json-output',
                        style=styles['json-output']
                    )
                ])
            ])
        ]),

    ])
])


# ############################## CALLBACKS ####################################
@app.callback(Output('tap-node-json-output', 'children'),
              [Input('cytoscape', 'tapNode')])
def display_tap_node(data):
    return json.dumps(data, indent=2)


@app.callback(Output('tap-edge-json-output', 'children'),
              [Input('cytoscape', 'tapEdge')])
def display_tap_edge(data):
    return json.dumps(data, indent=2)


@app.callback(Output('cytoscape', 'elements'),
              [Input('dropdown-breed', 'value')])
def update_cytoscape_layout(breed):
    global default_elements
    genesis_node = followers_node_di[breed][0]
    genesis_node['classes'] = "genesis"
    default_elements = [genesis_node]
    return default_elements


@app.callback(Output('cytoscape', 'elements'),
              [Input('cytoscape', 'tapNodeData')],
              [State('cytoscape', 'elements'),
               State('radio-expand', 'value')])
def generate_elements(nodeData, elements, expansion_mode):

    if not nodeData:
        return default_elements

    # If the node has already been expanded, we don't expand it again
    if nodeData.get('expanded'):
        return elements

    # This retrieves the currently selected element, and tag it as expanded
    for element in elements:
        if nodeData['id'] == element.get('data').get('id'):
            element['data']['expanded'] = True
            break

    if expansion_mode == 'followers':

        followers_nodes = followers_node_di.get(nodeData['id'])
        followers_edges = followers_edges_di.get(nodeData['id'])

        if followers_nodes:
            for node in followers_nodes:
                node['classes'] = 'followerNode'
            elements.extend(followers_nodes)

        if followers_edges:
            for follower_edge in followers_edges:
                follower_edge['classes'] = 'followerEdge'
            elements.extend(followers_edges)

    elif expansion_mode == 'following':

        following_nodes = following_node_di.get(nodeData['id'])
        following_edges = following_edges_di.get(nodeData['id'])

        if following_nodes:
            for node in following_nodes:
                if node['data']['id'] != genesis_node['data']['id']:
                    node['classes'] = 'followingNode'
                    elements.append(node)

        if following_edges:
            for follower_edge in following_edges:
                follower_edge['classes'] = 'followingEdge'
            elements.extend(following_edges)

    return elements


if __name__ == '__main__':
    app.run_server(debug=True)
