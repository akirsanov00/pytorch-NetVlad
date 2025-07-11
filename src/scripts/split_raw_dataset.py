#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

input_json = "../output/raw_dataset.json"
train_output_json = "train_db_q.json"
test_output_json = "test_q.json"
train_ratio = 0.8

def split_dataset():
    with open(input_json, 'r') as f:
        data = json.load(f)

    print(f"Founded {len(data)} notes")

    random.shuffle(data)

    split_index = int(len(data) * train_ratio)
    train_data = data[:split_index]
    test_data = data[split_index:]

    print(f"Train (db/q): {len(train_data)} notes")
    print(f"Test (q only): {len(test_data)} notes")

    with open(train_output_json, 'w') as f:
        json.dump(train_data, f, indent=2)

    with open(test_output_json, 'w') as f:
        json.dump(test_data, f, indent=2)

    print(f"Done. Definition created: {train_output_json}, {test_output_json}")
    return train_data, test_data

def main():
    train_data, test_data = split_dataset()

if __name__ == "__main__":
    main()

