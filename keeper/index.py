"""
Display main application index and route to apps.
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from keeper import app
from keeper.apps.twist import twist_layout

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

INDEX_LAYOUT = html.Div([dcc.Link("Twist", href="/twist")])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    """
    Route to specific app layout.
    """
    if pathname == "/twist":
        return twist_layout
    return INDEX_LAYOUT
    # You could also return a 404 "URL not found" page here
