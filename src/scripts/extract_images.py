#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import cv2
import rosbag
import numpy as np
from tqdm import tqdm  # прогресс-бар
from sensor_msgs.msg import CompressedImage

def decode_compressed_image(msg):
    np_arr = np.frombuffer(msg.data, np.uint8)
    cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv_img

def main():
    parser = argparse.ArgumentParser(description="Extract images from a ROS bag and save to folder.")
    parser.add_argument("bag_file", help="Input ROS bag file")
    parser.add_argument("--image_topic", default="/camera_node_ros1/left/compressed", help="Image topic name")
    parser.add_argument("--output_dir", default="../images", help="Output directory for images")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    bag = rosbag.Bag(args.bag_file, "r")

    # Подсчёт количества сообщений для tqdm
    total_msgs = bag.get_message_count(topic_filters=[args.image_topic])

    count = 0
    with tqdm(total=total_msgs, desc="Extracting images") as pbar:
        for topic, msg, t in bag.read_messages(topics=[args.image_topic]):
            cv_img = decode_compressed_image(msg)
            filename = f"img{count + 1:06d}.jpg"
            filepath = os.path.join(args.output_dir, filename)

            cv2.imwrite(filepath, cv_img)
            count += 1
            pbar.update(1)

    bag.close()
    print(f"\nDone. Extracted {count} images to '{args.output_dir}'.")

if __name__ == "__main__":
    main()

