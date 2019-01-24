from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from keeper import app
from keeper.apps.twist import twist_layout

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

index_layout = html.Div([dcc.Link("Twist", href="/twist")])

# Update the index
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/twist":
        return twist_layout
    else:
        return index_layout
    # You could also return a 404 "URL not found" page here

