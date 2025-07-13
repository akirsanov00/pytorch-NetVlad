import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from glob import glob

images_folder = '../../data/images'
output_json = '../output/raw_dataset.json'


def interpolate_for_images(tck, num_points):
    u_interp = np.linspace(0, 1, num_points)
    x_interp, y_interp, z_interp = splev(u_interp, tck)
    return x_interp, y_interp, z_interp

def save_json(interpolated_coords, output_json):
    with open(output_json, 'w') as f:
        json.dump(interpolated_coords, f, indent=2)
    print(f"The interpolated coordinates are saved {output_json}")

def main():
    image_files = sorted(glob(os.path.join(images_folder, '*', 'img*.jpg')))
    N = len(image_files)
    print(f"Images found: {N}")

    
    first_rel_path = os.path.relpath(image_files[0], images_folder)
    first_name = os.path.basename(first_rel_path)
    start_index = int(first_name.replace("img", "").replace(".jpg", ""))
    print(f"The first image has a number: {start_index}")

    interpolated_coords = []
    for i in range(N):
        name = os.path.relpath(image_files[i], images_folder)
        coord = {
            "name": name,
            "utm": [float(i+1), 0.0],
            "alt": float(0)
        }
        interpolated_coords.append(coord)

    save_json(interpolated_coords, output_json)

if __name__ == "__main__":
    main()

