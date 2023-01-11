import os

# check
images_directory = "Forest Segmented\\images_processed"  # The directory of the images that the program will predict
mask_directory = "Forest Segmented\\masks_processed"
for image_name in os.listdir(images_directory):
    if image_name not in os.listdir(mask_directory):
        print(image_name)
