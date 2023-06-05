import time
import Main
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import json
from flask import Response

import shutil
import os

app = Flask(__name__)
app.secret_key = "secretKey"

# Todo: put in config
SERVER_LISTEN_PORT = 2222
SERVER_HOST = "127.0.0.1"


def main():
    app.run(debug=True, port=SERVER_LISTEN_PORT, host=SERVER_HOST)


@app.route("/calc", methods=["POST"])
def login_page():
    # find user in data base and add to session:
    cords = request.form["coordinates"]  # todo - probably from json
    km_radius = request.form["radius"]  # todo - probably from float
    cords = cords.replace("(", "")
    cords = cords.replace(")", "")
    cords = cords.replace(" ", "")
    cords = cords.replace("'", "")
    coordinates = cords.split(",")
    cords = (int(coordinates[0]), int(coordinates[1]), int(coordinates[2]), coordinates[3])
    km_radius = float(km_radius)
    # todo - add option to add shp files

    img, masks_list = Main.get_viable_landing_in_radius(cords, km_radius)
    lists_masks_list = []
    list_img = img.tolist()
    for mask in masks_list:
        lists_masks_list.append(mask.tolist())
    return json.jsonify(list_img, lists_masks_list)


# can generate config in remote
def make_config_file(product_id):
    """
    The function will create a string that can be added to a json file.
    """
    data = {

        "ServerDomain": "",
        "ServerPort": 2222,
    }

    with open('config.json', 'w') as json_file:
        json.dump(data, json_file)


if __name__ == '__main__':
    main()
