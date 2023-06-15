# 🚁 SOCCER FIELD 🚁

![GIF](.\Modules\Front\images_for_gui\logo_cut.gif)
## Description ##

Input UTM coordinates where you want to land, and specify a radius around those coordinates, get viable landing spots
for a helicopter
![Image](.\Modules\Front\images_for_gui\gui_preview.png)

## Installation ##

1. Clone the repository - `frontback` branch to make sure you can use a remote server.
2. Make sure you have a DTM relevant to your area of interest, and place it in the following
   path: `DTM_data\your_model.tif`
3. Make sure you are running python 3.7 or higher, and run the following command in your
   terminal: `pip install -r requirements.txt`'

## Usage ##

The project is divided into two modules: the backend and the frontend.
You can run them both together (using `localhost` for the IP and a common port such as `2222`), or you can run each module
separately, if your main machine is not rich in resources, and you have access to a bulkier remote
machine ([Azure](https://azure.microsoft.com/), [AWS](https://aws.amazon.com/), [Google Cloud](https://cloud.google.com/),
etc.).

### Backend ###

1. Navigate to the `Modules\Back` directory.
2. Run the following command in your terminal: `python server.py [SERVER_IP] [SERVER_PORT]` (SERVER_IP and SERVER_PORT
   are optional, default is localhost:2222).
3. Wait for the server to start, you should be seeing the text:
```console
* Serving Flask app "server" (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
  Use a production WSGI server instead.
* Debug mode: on
* Restarting with stat
* Debugger is active!
* Debugger PIN: 189-508-852
* Running on http://127.0.0.1:2222/ (Press CTRL+C to quit)'
```

#### Features: ####

1. The project allows for more functions that take coordinates and radius as input, so you can implement more of those
   and simply add them to list of those taken into consideration.
2. The project handles shape files ([.shp](https://fileinfo.com/extension/shp)), and loads them as another mask to
   consider.
   Additionally, the infrastructure to save the output from a run of the project field as a shape file is already done (
   all of these are documented under the `Modules\Back\SHP_Handle`).
3. The tree module allows prediction with a trained model, and the infrastructure to train a model is already done (
   all of these are documented under `Modules\Back\Trees`).

#### Reservations: ####

1. The slopes model currently supports DTMs in UTM format with a 10m resolution. If you want to use a different
   resolution, you will have to change the code in the `slope.py` file, and if the resolution is significantly higher,
   you might want to start accounting for changes in the slope within the landing zone of the chopper (10mx10m is large
   enough so we don't have to worry about what happens in there, as the chopper fits).
2. The building module is entirely reliant on arcgis' World_TOPO_MAP service (which is free), and its support is limited
   to areas outside of Israel. Make sure to test the coverage for your area of interest, and if you want to use
   another service, you will have to change the preferences in the `arcgis_preferences.json` file.


### Frontend ###

1. Navigate to the `Modules\Front` directory.
2. Run the following command in your terminal: `python main.py [SERVER_IP] [SERVER_PORT]` (SERVER_IP and SERVER_PORT are
   optional, default is localhost:2222).
3. Input your UTM coordinates and radius, and press the "Search" button.
4. Wait for the calculations to end, and the aerial image with the overlayed areas will be displayed.

#### Features: ####

1. Draw lines on the map with the mouse to calculate their length. Right click the lines to remove them.
2. Slide the slider to change the opacity of the overlayed areas.
3. Tick the different checkboxes to display consideration only of certain obstacles.

## Support

feel free to contact either one of us at:

* [Guy](mailto:guy.harel.43@gmail.com  "Guy's Email")
* [Matan](mailto:matan.hadad.43@gmail.com  "Matan's Email")

## Project Status 

We are no longer working on this project, but feel free to clone it and use it as you wish.
