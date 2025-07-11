#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil


source_dir = '../images'
target_dir = '../images'
images_per_folder = 10000

def decode_compressed_image(msg):
    np_arr = np.frombuffer(msg.data, np.uint8)
    cv_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv_img

def main():
    all_images = sorted([
        f for f in os.listdir(source_dir)
        if os.path.isfile(os.path.join(source_dir, f))
        ])

    total_images = len(all_images)
    print(f"Founded {len(all_images)} images")

    for i in range(0, total_images, images_per_folder):
        chunk = all_images[i:i + images_per_folder]
        folder_index = i // images_per_folder
        folder_name = f"{folder_index:03d}"
        folder_path = os.path.join(target_dir, folder_name)

        os.makedirs(folder_path, exist_ok=True)

        print(f"Moving {len(chunk)} images to {folder_name}")

        for filename in chunk:
            src = os.path.join(source_dir, filename)
            dst = os.path.join(folder_path, filename)
            shutil.move(src, dst)

    print(f"\nDone.")

if __name__ == "__main__":
    main()

