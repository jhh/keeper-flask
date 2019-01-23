import os
import pandas as pd
from flask import Flask
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from logging.config import dictConfig

app = Dash(__name__)
server = app.server
server.config.from_object("keeper.default_settings")
server.config.from_envvar("KEEPER_SETTINGS")

from keeper.db import get_db_connection, get_db_cursor

app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

index_layout = html.Div(
    [
        dcc.Link("Twist", href="/twist"),
    ]
)



twist_layout = html.Div(
    [
        dcc.Input(id="action-id", value="409", type="text"),
        html.Button(id="submit-button", n_clicks=0, children="Submit"),
        dcc.Graph(id="twist-graph"),
        html.Br(),
        dcc.Link("Go back to home", href="/"),
    ]
)


@app.callback(
    Output("twist-graph", "figure"),
    [Input("submit-button", "n_clicks")],
    [State("action-id", "value")],
)
def update_output_div(n_clicks, action_id):
    with get_db_connection() as connection:
        trace_df = pd.read_sql(
            "SELECT * FROM action_trace WHERE action_id = {}".format(action_id),
            con=connection,
        )

    twist_df = trace_df.pivot(index="millis", columns="measure", values="value")
    if twist_df.actual_vel.mean() < 0:
        twist_df.actual_vel = twist_df.actual_vel * -1
    twist_df.setpoint_vel = twist_df.setpoint_vel / 10.0
    twist_df.profile_vel = twist_df.profile_vel / 10.0
    twist_df["ticks_error"] = twist_df.actual_ticks - twist_df.profile_ticks

    layout = {
        "title": "Velocity",
        "xaxis": {"title": "milliseconds"},
        "yaxis": {"title": "ticks/100ms"},
        "yaxis2": {"title": "amps", "side": "right", "overlaying": "y"},
        "height": 600,
    }
    return {
        "data": [
            go.Scatter(name="profile", x=twist_df.index, y=twist_df.profile_vel),
            go.Scatter(name="setpoint", x=twist_df.index, y=twist_df.setpoint_vel),
            go.Scatter(name="actual", x=twist_df.index, y=twist_df.actual_vel),
            go.Scatter(
                name="current",
                x=twist_df.index,
                y=twist_df.drive_current,
                line={"color": "rgba(22, 12, 204, 0.1)"},
                yaxis="y2",
            ),
        ],
        "layout": layout,
    }


# Update the index
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/twist":
        return twist_layout
    else:
        return index_layout
    # You could also return a 404 "URL not found" page here


log_config = {
    "version": 1,
    "formatters": {
        "debug": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"},
        "production": {"format": "%(levelname)s in %(module)s: %(message)s"},
    },
    "handlers": {
        "debug": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "debug",
        },
        "production": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "production",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["debug" if server.config["DEBUG"] else "production"],
    },
}

dictConfig(log_config)

import keeper.db
import keeper.filters
import keeper.views
import keeper.api
