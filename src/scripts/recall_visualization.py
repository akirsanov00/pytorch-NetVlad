import os
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splprep, splev
from PIL import Image

gps_json = '../output/raw_GPS.json'
dataset_json = '../output/raw_dataset.json'
recall_json = "../output/recall_visualization.json"
images_dir = "../images"
min_dist = 2.0

def read_raw_gps(gps_json):
    with open(gps_json, 'r') as f:
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

def get_utm_from_dataset(image_name, dataset_json):
    for entry in dataset_json:
        if entry['name'] == image_name:
            return entry['utm'][0], entry['utm'][1], entry['alt']
    print(f"Image '{image_name}' not found in dataset")
    return None

def plot_graph_with_recall(filtered_gps, tck, recall_json, images_dir, dataset_json):
    with open(recall_json, 'r') as f:
        recall_data = json.load(f)
    with open(dataset_json, 'r') as f:
        dataset = json.load(f)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    u_fine = np.linspace(0, 1, 5000)
    x_spline, y_spline, z_spline = splev(u_fine, tck)

    ax.plot(x_spline, y_spline, z_spline, 'r-', label='Interpolated spline')
    ax.plot(filtered_gps.T[0], filtered_gps.T[1], filtered_gps.T[2], 'b--', label='Filtered GPS')

    # Query point
    q_coords = get_utm_from_dataset(recall_data['query']['name'], dataset)
    if q_coords:
        ax.scatter(*q_coords, c='green', marker='+', s=500, label='Query')

    # Recall @ 1
    r1 = recall_data['recall@1']
    r1_coords = get_utm_from_dataset(r1['name'], dataset)
    if r1_coords:
        color = 'blue'
        ax.scatter(*r1_coords, c=color, marker='o', s=50, label='Recall@1')
            
    # Recall @ 5
    for i, r in enumerate(recall_data['recall@5']):
        r_coords = get_utm_from_dataset(r['name'], dataset)
        if r_coords:
            color = 'black'
            label = 'Recall@5' if i == 0 else None
            ax.scatter(*r_coords, c=color, marker='x', s=200, label=label)

            
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    plt.title('3D GPS Trajectory with Spline')
    plt.tight_layout()
    plt.show()

def main():
    raw_gps = read_raw_gps(gps_json)
    filtered_points = clean_gps(raw_gps)

    tck = compute_spline(filtered_points)
    if tck is None:
        return
    
    plot_graph_with_recall(filtered_points, tck, recall_json, images_dir, dataset_json)
    
if __name__ == "__main__":
    main()

