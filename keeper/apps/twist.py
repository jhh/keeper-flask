from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd

from keeper.db import get_db_connection, get_db_cursor
from keeper import app

twist_layout = html.Div(
    [
        html.H1("Twist Plot", className="pageHeader"),
        dcc.Dropdown(id="action-id"),
        html.Button(id="submit-button", n_clicks=0, children="Refresh"),
        dcc.Graph(id="twist-graph"),
        html.Div([dcc.Link("Go back to home", href="/")], className="indexLink"),
    ],
    className="container",
)

ACTIONS_SQL = """
SELECT id, name, timestamp
FROM action
ORDER BY timestamp DESC
LIMIT 20
"""


@app.callback(Output("action-id", "options"), [Input("submit-button", "n_clicks")])
def update_action_dropdown(n_click):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return [
            dict(
                value=row[0], label=f"{row[1]} - {row[2].strftime('%d %b %Y %I:%M %p')}"
            )
            for row in cursor
        ]


@app.callback(Output("twist-graph", "figure"), [Input("action-id", "value")])
def update_output_div(action_id):
    if action_id is None:
        return {"data": []}
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
