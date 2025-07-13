#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
import numpy as np
import scipy.io as sio


input_json = "../output/raw_dataset.json"
train_output_json = "train_db.json"
query_output_json = "train_q.json"
test_output_json = "test_q.json"
val_output_json = "val_q.json"
database_ratio = 0.5
query_ratio = 0.2
val_test_ration = 0.15

posDistThr = 100
posDistSqThr = posDistThr ** 2
nonTrivPosDistSqThr = 100

output_train_mat = "../../data/datasets/train.mat"
output_test_mat = "../../data/datasets/test.mat"
output_val_mat = "../../data/datasets/val.mat"

def split_dataset():
    with open(input_json, 'r') as f:
        data = json.load(f)

    print(f"Founded {len(data)} notes")

    random.shuffle(data)

    split_index_one = int(len(data) * database_ratio)
    split_index_two = int(len(data) * query_ratio) + split_index_one
    split_index_three = int(len(data) * val_test_ration) + split_index_two
    
    database_data = data[:split_index_one]
    query_data = data[split_index_one:split_index_two]
    test_data = data[split_index_two:split_index_three]
    val_data = data[split_index_three:]

    print(f"Train (db): {len(database_data)} notes")
    print(f"Train (q): {len(query_data)} notes")
    print(f"Test (q only): {len(test_data)} notes")
    print(f"Val (q only): {len(val_data)} notes")
    
    return database_data, query_data, test_data, val_data
    
def save_json_files(database_data, query_data, test_data, val_data):
    with open(train_output_json, 'w') as f:
        json.dump(database_data, f, indent=2)
        
    with open(query_output_json, 'w') as f:
        json.dump(query_data, f, indent=2)
        
    with open(test_output_json, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    with open(val_output_json, 'w') as f:
        json.dump(val_data, f, indent=2)
        
    print(f"Done. Definition created: {train_output_json}, {query_output_json}, {test_output_json}, {val_output_json}")

def prepare_fields(entries):
    names = np.array([e["name"] for e in entries], dtype=object).reshape(-1, 1)
    utm = np.array([e["utm"] for e in entries], dtype=np.float64).T  # форма (2, N)
    return names, utm

def save_train_mat(database_data, query_data):
    train_dbImage, utmDb_train = prepare_fields(database_data)
    train_qImage, utmQ_train = prepare_fields(query_data)

    train_struct = {
        "whichSet": "train",
        "dbImage": train_dbImage,
        "utmDb": utmDb_train,
        "qImage": train_qImage,
        "utmQ": utmQ_train,
        "numDb": np.array([[train_dbImage.shape[0]]], dtype=np.uint32),
        "numQ": np.array([[train_qImage.shape[0]]], dtype=np.uint32),
        "posDistThr": np.array([[posDistThr]], dtype=np.uint32),
        "posDistSqThr": np.array([[posDistSqThr]], dtype=np.uint32),
        "nonTrivPosDistSqThr": np.array([[nonTrivPosDistSqThr]], dtype=np.uint32)
    }

    sio.savemat(output_train_mat, {"dbStruct": train_struct})
    print(f"train.mat saved: {output_train_mat}")

def save_test_mat(database_data, test_data):
    test_dbImage, utmDb_test = prepare_fields(database_data)
    test_qImage, utmQ_test = prepare_fields(test_data)

    test_struct = {
        "whichSet": "test",
        "dbImage": test_dbImage,
        "utmDb": utmDb_test,
        "qImage": test_qImage,
        "utmQ": utmQ_test,
        "numDb": np.array([[test_dbImage.shape[0]]], dtype=np.uint32),
        "numQ": np.array([[test_qImage.shape[0]]], dtype=np.uint32),
        "posDistThr": np.array([[posDistThr]], dtype=np.uint32),
        "posDistSqThr": np.array([[posDistSqThr]], dtype=np.uint32),
        "nonTrivPosDistSqThr": np.array([[nonTrivPosDistSqThr]], dtype=np.uint32)
    }

    sio.savemat(output_test_mat, {"dbStruct": test_struct})
    print(f"test.mat saved: {output_test_mat}")
    
def save_val_mat(database_data, val_data):
    val_dbImage, utmDb_val = prepare_fields(database_data)
    val_qImage, utmQ_val = prepare_fields(val_data)

    val_struct = {
        "whichSet": "val",
        "dbImage": val_dbImage,
        "utmDb": utmDb_val,
        "qImage": val_qImage,
        "utmQ": utmQ_val,
        "numDb": np.array([[val_dbImage.shape[0]]], dtype=np.uint32),
        "numQ": np.array([[val_qImage.shape[0]]], dtype=np.uint32),
        "posDistThr": np.array([[posDistThr]], dtype=np.uint32),
        "posDistSqThr": np.array([[posDistSqThr]], dtype=np.uint32),
        "nonTrivPosDistSqThr": np.array([[nonTrivPosDistSqThr]], dtype=np.uint32)
    }

    sio.savemat(output_val_mat, {"dbStruct": val_struct})
    print(f"val.mat saved: {output_val_mat}")

def main():
    database_data, query_data, test_data, val_data = split_dataset()
    save_json_files(database_data, query_data, test_data, val_data)
    save_train_mat(database_data, query_data)
    save_test_mat(database_data, test_data)
    save_val_mat(database_data, val_data)

if __name__ == "__main__":
    main()

