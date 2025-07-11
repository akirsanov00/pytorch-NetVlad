import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from glob import glob

input_json = '../output/raw_coords.json'
images_folder = '../images'
output_json = '../output/raw_dataset.json'
min_dist = 1.0

def read_raw_gps(input_json):
    with open(input_json, 'r') as f:
        data = json.load(f)
    raw_coords = np.array([[p['utm'][0], p['utm'][1], p['alt']] for p in data])
    print(f"Raw GPS coordinates: {len(raw_coords)}")
    return raw_coords

def clean_gps(raw_gps):
    filtered_gps = [raw_gps[0]]
    for point in raw_gps[1:]:
        prev = filtered_gps[-1]
        dist = np.linalg.norm(point[:3] - prev[:3])
        if dist >= min_dist:
            filtered_gps.append(point)
    filtered_gps = np.array(filtered_gps)
    print(f"Filtered GPS coordinates: {len(filtered_gps)}\t(min_dist = {min_dist} m)")
    return filtered_gps

def compute_spline(filtered_points):
    try:
        distances = np.linalg.norm(np.diff(filtered_points, axis=0), axis=1)
        u = np.zeros(len(filtered_points))
        u[1:] = np.cumsum(distances)
        u /= u[-1]

        tck, _ = splprep(filtered_points.T, u=u, s=500.0, k=2)
        return tck
    except Exception as e:
        print(f"Error: {e}")
        return None

def interpolate_for_images(tck, num_points):
    u_interp = np.linspace(0, 1, num_points)
    x_interp, y_interp, z_interp = splev(u_interp, tck)
    return x_interp, y_interp, z_interp

def plot_graph(filtered_gps, tck):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    u_fine = np.linspace(0, 1, 5000)
    x_spline, y_spline, z_spline = splev(u_fine, tck)

    ax.plot(x_spline, y_spline, z_spline, 'r-', label='Interpolated spline')
    ax.plot(filtered_gps.T[0], filtered_gps.T[1], filtered_gps.T[2], 'b--', label='Filtered GPS')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    plt.title('3D GPS Trajectory with Spline')
    plt.tight_layout()
    plt.show()

def save_json(interpolated_coords, output_json):
    with open(output_json, 'w') as f:
        json.dump(interpolated_coords, f, indent=2)
    print(f"The interpolated coordinates are saved {output_json}")

def main():
    raw_gps = read_raw_gps(input_json)
    filtered_points = clean_gps(raw_gps)

    tck = compute_spline(filtered_points)
    if tck is None:
        return

    plot_graph(filtered_points, tck)
    
    image_files = sorted(glob(os.path.join(images_folder, '*', 'img*.jpg')))
    N = len(image_files)
    print(f"Images found: {N}")

    x_interp, y_interp, z_interp = interpolate_for_images(tck, N)
    
    first_rel_path = os.path.relpath(image_files[0], images_folder)
    first_name = os.path.basename(first_rel_path)
    start_index = int(first_name.replace("img", "").replace(".jpg", ""))
    print(f"The first image has a number: {start_index}")

    interpolated_coords = []
    for i in range(N):
        name = os.path.relpath(image_files[i], images_folder)
        coord = {
            "name": name,
            "utm": [float(x_interp[i]), float(y_interp[i])],
            "alt": float(z_interp[i])
        }
        interpolated_coords.append(coord)

    save_json(interpolated_coords, output_json)

if __name__ == "__main__":
    main()

