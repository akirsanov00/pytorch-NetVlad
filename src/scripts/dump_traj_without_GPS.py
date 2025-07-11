#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import rospy
import json
from nav_msgs.msg import Path

output = "trajectory_dump.txt"
output_file = "raw_coords.json"
trajectory = []
counter = 1

def callback(msg):
    global counter, trajectory

    if not msg.poses:
        return

    last_pose = msg.poses[-1]
    pos = last_pose.pose.position

    point = {
        "id": counter,
        "utm": [round(pos.x, 3) + 10000, round(pos.y, 3) + 10000],
        "alt": round(pos.z, 3) + 180
    }

    trajectory.append(point)
    counter += 1

    with open(output_file, "w") as f:
        json.dump(trajectory, f, indent=2)

'''
def callback(msg):
    if not msg.poses:
        return

    last_pose = msg.poses[-1]
    pos = last_pose.pose.position
    ori = last_pose.pose.orientation
    seq = msg.header.seq
    stamp = msg.header.stamp

    with open(output, "a") as f:
        f.write(f"[{seq}] t={stamp.secs}.{str(stamp.nsecs).zfill(9)} ")
        f.write(f"Position(x={pos.x:.6f}, y={pos.y:.6f}, z={pos.z:.6f}) ")
        f.write(f"Orientation(x={ori.x:.6f}, y={ori.y:.6f}, z={ori.z:.6f}, w={ori.w:.6f})\n")
'''

def main():
    master_uri = os.environ.get("ROS_MASTER_URI", "http://localhost:11311")
    os.environ["ROS_MASTER_URI"] = master_uri
    print(f"Connecting to ROS master at {master_uri}")

    rospy.init_node("path_logger_json", anonymous=True)
    rospy.Subscriber("/path", Path, callback)
    rospy.spin()

if __name__ == "__main__":
    main()

