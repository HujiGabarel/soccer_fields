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

#Todo: put in config
SERVER_LISTEN_PORT = 2222
SERVER_HOST ="127.0.0.1"
def main():
    app.run(debug=True, port=SERVER_LISTEN_PORT, host=SERVER_HOST)


@app.route("/calc", methods=["POST"])
def login_page():


        # find user in data base and add to session:
        cords = request.form["coordinates"] #todo - probably from json
        km_radius = request.form["radius"] #todo - probably from float

        #todo - add option to add shp files
        #todo - add options to cancel some masks



        img,masks_dict = Main.get_viable_landing_in_radius(cords,km_radius,None) #todo - remove gui paramater from function
        return json.jsonify(masks_dict) #todo - return also img










#can generate config in remote
def make_config_file(product_id):
    """
    The function will create a string that can be added to a json file.
    """
    data = {
            "General" : {
                "ProductId": product_id,
            },   

        "Communication" :
        {
            "ServerDomain": "",
            "ServerPort": 80,
            "DefenderListenPort": 2222
        }
    }
    
    with open('Example/Configuration{}_tmp.json'.format(product_id), 'w') as json_file:
        json.dump(data, json_file)


if __name__ == '__main__':
    main()