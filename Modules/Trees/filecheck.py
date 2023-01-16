import os

# check
images_directory = "Forest Segmented\\all_images_tif"  # The directory of the all_images that the program will predict
mask_directory = "Forest Segmented\\all_masks_tif"
for image_name in os.listdir(images_directory):
    if image_name not in os.listdir(mask_directory):
        print(image_name)
