from flask import Blueprint, render_template

from utils import cache

import data
import config

scoreboard = Blueprint("scoreboard", __name__, template_folder="../templates/scoreboard")


@scoreboard.route('/scoreboard/')
def index():
    scoreboard_data = cache.get_complex("scoreboard")
    graphdata = cache.get_complex("graph")
    if scoreboard_data is None or graphdata is None:
        if config.immediate_scoreboard:
            scoreboard_data = scoreboard.calculate_scores()
            graphdata = scoreboard.calculate_graph(data)
            data.scoreboard.set_complex("scoreboard", data, 120)
            data.scoreboard.set_complex("graph", graphdata, 120)
        else:
            return "No scoreboard data available. Please contact an organizer."

    return render_template("scoreboard.html", data=scoreboard_data, graphdata=graphdata)
