from datetime import datetime, timedelta
import pandas as pd
import flask
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

from app import cache
from utils.settings import (
    MAPBOX_ACCESS_TOKEN,
    DRIVE_THRU_URL,
    NCOV19_API,
    MAPBOX_STYLE,
    STATES_COORD,
)
import requests


px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)


# TODO: Make Drive-thru testing center API
def get_drive_thru_testing_centers():
    try:
        drive_thru_df = pd.read_csv(DRIVE_THRU_URL)
    except Exception as ex:
        print(ex)
    return drive_thru_df


########################################################################
#
# App Callbacks
#
########################################################################


def confirmed_scatter_mapbox(state="US"):
    """Displays choroplepth map for the data. For the whole US, the map is divided by state.
    TODO: For individual states,the map will be divided by county lines. Add callbacks

    :return card: A dash boostrap component Card object with a dash component Graph inside drawn using plotly express scatter_mapbox
    :rtype: dbc.Card
    """
    URL = NCOV19_API + "county"
    response = requests.get(URL).json()
    data = response["message"]
    data = pd.read_json(data, orient="records")
    data["State Name"] = data["State Name"].str.title()
    data["County Name"] = data["County Name"].str.title()

    # set lat/long
    if state == "US":
        lat, lon, zoom = 39.8097343, -98.5556199, flask.session["zoom"]
    else:
        lat, lon, zoom = (
            STATES_COORD[state]["latitude"],
            STATES_COORD[state]["longitude"],
            STATES_COORD[state]["zoom"],
        )

    color_scale = ["#ffbaba", "#ff7b7b", "#ff5252", "#ff0000", "#a70000"]
    fig = px.scatter_mapbox(
        data,
        lat="Latitude",
        lon="Longitude",
        color="Confirmed",
        size="Confirmed",
        size_max=50,
        hover_name="County Name",
        hover_data=["Confirmed", "Death", "State Name", "County Name"],
        color_continuous_scale=color_scale,
    )

    fig.layout.update(
        # Title still no show after this
        title="Corona Virus Cases in U.S.",
        title_x=0.1,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # This takes away the colorbar on the right hand side of the plot
        coloraxis_showscale=False,
        mapbox_style=MAPBOX_STYLE,
        mapbox=dict(
            center=dict(lat=lat, lon=lon), zoom=zoom
        ),  # flask.session["zoom"]),
    )

    # https://community.plot.ly/t/plotly-express-scatter-mapbox-hide-legend/36306/2
    # print(fig.data[0].hovertemplate)
    fig.data[0].update(
        hovertemplate="%{customdata[3]}, %{customdata[2]}<br>Confirmed: %{marker.size}<br>Deaths: %{customdata[1]}"
    )

    return fig


def drive_thru_scatter_mapbox():
    """DO NOT CACHE. NEED APP_STATE TO CHANGE DYNAMICALLY
    """
    fig = px.scatter_mapbox(
        get_drive_thru_testing_centers(),
        lat="Latitude",
        lon="Longitude",
        hover_name="Name",
        hover_data=["URL"],
    )

    fig.layout.update(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox_style=MAPBOX_STYLE,
        mapbox=dict(
            center=dict(lat=39.8097343, lon=-98.5556199), zoom=flask.session["zoom"]
        ),
        dragmode=False,
    )

    fig.data[0].update(
        hovertemplate="<b><a href='%{customdata[0]}' style='color:black'>%{hovertext}</a></b>",
        marker={"size": 10, "symbol": "marker"},
    )

    return fig
