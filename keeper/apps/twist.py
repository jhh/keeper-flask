from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import pandas as pd

from keeper.db import get_db_connection, get_db_cursor
from keeper import app

ACTIONS_SQL = """
SELECT id, name, timestamp
FROM action
WHERE meta->>'type' = 'twist'
ORDER BY timestamp DESC
LIMIT 20
"""


def action_list():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return [
            dict(
                value=row[0], label=f"{row[1]} - {row[2].strftime('%d %b %Y %I:%M %p')}"
            )
            for row in cursor
        ]


header = html.Div(className="pageHeader", children=[html.H1("Twist Plot")])
controls = html.Div(
    className="twistControls",
    children=[
        dcc.Dropdown(id="primary-action-id", options=action_list()),
        dcc.Dropdown(id="secondary-action-id", options=action_list()),
        html.Button(id="submit-button", children="Refresh"),
    ],
)
graph = html.Div(className="twistGraph", children=dcc.Graph(id="twist-graph"))
home = html.Div(className="indexLink", children=[dcc.Link("Go back to home", href="/")])
store = dcc.Store(id="actions-list", storage_type="session")

twist_layout = html.Div(
    className="container", children=[header, controls, graph, home, store]
)


@app.callback(Output("actions-list", "data"), [Input("submit-button", "n_clicks")])
def update_actions_list(n_clicks):
    return action_list()


@app.callback(Output("primary-action-id", "options"), [Input("actions-list", "data")])
def update_primary_options(data):
    if data is None:
        raise PreventUpdate
    return data


@app.callback(Output("secondary-action-id", "options"), [Input("actions-list", "data")])
def update_secondary_options(data):
    if data is None:
        raise PreventUpdate
    return data


def plot_data(action_id, primary):
    if action_id is None:
        return []

    with get_db_connection() as connection:
        trace_df = pd.read_sql(
            "SELECT * FROM action_trace WHERE action_id = {}".format(action_id),
            con=connection,
        )
        connection.commit()

    twist_df = trace_df.pivot(index="millis", columns="measure", values="value")
    if twist_df.actual_vel.mean() < 0:
        twist_df.actual_vel = twist_df.actual_vel * -1
    twist_df.setpoint_vel = twist_df.setpoint_vel / 10.0
    twist_df.profile_vel = twist_df.profile_vel / 10.0
    twist_df["ticks_error"] = twist_df.actual_ticks - twist_df.profile_ticks

    alpha = 1 if primary else 0.25
    name = "primary" if primary else "secondary"

    return [
        go.Scatter(
            name=f"{name} profile",
            x=twist_df.index,
            y=twist_df.profile_vel,
            line={"color": f"rgba(22, 11, 211, {alpha})"},
        ),
        go.Scatter(
            name=f"{name} setpoint",
            x=twist_df.index,
            y=twist_df.setpoint_vel,
            line={"color": f"rgba(22, 211, 11, {alpha})"},
        ),
        go.Scatter(
            name=f"{name} actual",
            x=twist_df.index,
            y=twist_df.actual_vel,
            line={"color": f"rgba(211, 22, 11, {alpha})"},
        ),
    ]


@app.callback(
    Output("twist-graph", "figure"),
    [Input("primary-action-id", "value"), Input("secondary-action-id", "value")],
)
def update_output_div(primary_id, secondary_id):

    data = plot_data(primary_id, True) + plot_data(secondary_id, False)

    layout = {
        "title": "Velocity",
        "xaxis": {"title": "milliseconds"},
        "yaxis": {"title": "ticks/100ms"},
        "yaxis2": {"title": "amps", "side": "right", "overlaying": "y"},
        "height": 600,
    }
    return {"data": data, "layout": layout}


# [
#     go.Scatter(
#         name="current",
#         x=twist_df.index,
#         y=twist_df.drive_current,
#         line={"color": "rgba(22, 12, 204, 0.1)"},
#         yaxis="y2",
#     ),
# ]
