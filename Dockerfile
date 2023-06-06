FROM ubuntu:latest
LABEL authors="Guy Harel"
FROM python:3.9
COPY DTM_data/DTM_new/dtm_mimad_wgs84utm36_10m.tif /app/DTM_data/DTM_new/dtm_mimad_wgs84utm36_10m.tif
COPY Models/our_models/official_masks_10%.joblib /app/Models/our_models/official_masks_10%.joblib
COPY Modules /app/Modules
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
WORKDIR /app
CMD ["start", "", "python", "/Modules/Main/Server.py", "127.0.0.1", "2222"]
CMD ["start", "", "python", "/Modules/GUI/gui.py", "127.0.0.1", "2222"]