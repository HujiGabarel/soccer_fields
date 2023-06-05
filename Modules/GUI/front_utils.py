import numpy as np
import requests
import json


# Define the data to be sent
def send_request(coordinates, radius):
    data = {
        "coordinates": f"{coordinates}",
        "radius": f"{radius}"
    }

    # Send the POST request
    url = "http://localhost:2222/calc"  # Replace with your server URL
    response = requests.post(url, data=data)

    # Handle the response
    if response.status_code == 200:
        # Successful response
        response_data = response.json()
        image = response_data[0]
        masks_list = response_data[1]
        np_image = np.array(image)
        np_masks = []
        for mask in masks_list:
            np_masks.append(np.array(mask))
        return np_image, np_masks
    else:
        # Error handling
        print("Request failed with status code:", response.status_code)

