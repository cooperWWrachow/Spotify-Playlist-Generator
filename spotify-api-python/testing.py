import os

# Get the directory path of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the images folder
images_folder = os.path.join(script_dir, 'covers')

# List all files in the images folder
image_files = os.listdir(images_folder)

# Iterate over the image files and do something with them
for image_file in image_files:
    if image_file.endswith('.jpg'):
        # Construct the full path to each image file
        image_path = os.path.join(images_folder, image_file)
        # Now you can use this image_path to access each image file
        print(image_path)