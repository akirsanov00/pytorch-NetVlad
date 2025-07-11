#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import argparse
import rosbag
import utm
from tqdm import tqdm
from sensor_msgs.msg import NavSatFix

def main():
    parser = argparse.ArgumentParser(description="Extract GPS from bag, convert to UTM+alt, save as JSON.")
    parser.add_argument("bag_file", help="Input ROS bag file")
    parser.add_argument("--output_json", default="../output/raw_GPS.json", help="Output JSON file")
    parser.add_argument("--gps_topic", default="/msp_node_ros1/gps", help="GPS topic name")
    args = parser.parse_args()

    bag = rosbag.Bag(args.bag_file, "r")
    total_msgs = bag.get_message_count(topic_filters=[args.gps_topic])

    gps_data = []

    with tqdm(total=total_msgs, desc="Extracting GPS") as pbar:
        id_counter = 1
        for topic, msg, t in bag.read_messages(topics=[args.gps_topic]):
            if msg.status.status < 0:
                pbar.update(1)
                continue

            lat = msg.latitude
            lon = msg.longitude
            alt = msg.altitude

            utm_x, utm_y, zone_num, zone_letter = utm.from_latlon(lat, lon)

            gps_data.append({
                "id": id_counter,
                "utm": [round(utm_x, 3), round(utm_y, 3)],
                "alt": alt
            })

            id_counter += 1
            pbar.update(1)

    bag.close()

    with open(args.output_json, "w") as f:
        json.dump(gps_data, f, indent=2)

    print(f"\nDone. Extracted {len(gps_data)} GPS points to {args.output_json}")

if __name__ == "__main__":
    main()

