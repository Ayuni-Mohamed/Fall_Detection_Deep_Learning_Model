# -*- coding: utf-8 -*-
"""execute_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EPkzd1Ea0UYJb6bROxtTPdelFAe5a-cH
"""

import json
import os
import pandas as pd
import csv
from tensorflow import keras
from numpy import array
import matplotlib.pyplot as plt
import sys
import numpy as np

# the bodylandmark directory for a vedio

video_landmark_path = sys.argv[1]

data = []

# read json 2-d pose as data, without using:
#     {15, "REye"},
#     {16, "LEye"},
#     {17, "REar"},
#     {18, "LEar"}
frames = os.listdir(video_landmark_path)

for frame in frames:
  frame_path = os.path.join(video_landmark_path, frame)
  with open(frame_path, mode='r') as json_file:
    people_dict = json.load(json_file)
    people = people_dict["people"]
    pose_keypoints_2d = []
    # fill missing data as 0
    if len(people) == 0:
      pose_keypoints_2d = [0] * 63
    else:
      full_pose = people[0].get("pose_keypoints_2d")
      pose_keypoints_2d = full_pose[:45] + full_pose[57:]
    # each pose_keypoints_2d:
    # [431.949, 196.241, 0.0564434, 437.194, 187.749, 0.552267,...]
    frame_number = int(frame.split('.')[0].split('_')[1])
    pose_keypoints_2d.append(frame_number)
    data.append(pose_keypoints_2d)

data = sorted(data, key=lambda l:l[-1])

for d in data:
  d.remove(d[-1])

# use model and write the json file for a video
print("loading model and computing probability for each frame...")
model = keras.models.load_model('./model_improved_cnn_Apr16.h5')
dictionary = {}
dictionary['falling'] = []
test = []

# normalize data
for record in data:
    for i in range(0, 63, 3):
      record[i] = float(record[i])/ 640
      record[i + 1] = float(record[i + 1]) / 480
    test.append(record)


test = array(test)
test = test.reshape((len(test), 3, int(len(test[0])/3), 1))
probality = model.predict_proba(test)

frame_num = 0
for i in range(len(probality)):
    timestamp = frame_num / 30
    probability_fall = float(probality[i][0])
    to_add = [timestamp, probability_fall]
    dictionary['falling'].append(to_add)
    frame_num +=1

# Serializing json
json_object = json.dumps(dictionary)

print("complete computing, and the result has been written to json file")
# Writing to sample.json
with open("./results/result_cnn.json", "w") as outfile:
    outfile.write(json_object)

df = pd.DataFrame(dictionary['falling'])
p = df.plot(x=0, y=1, legend=False)
p.set_xlabel('Time (in seconds)')
p.set_ylabel('probability of fall')
plt.ylim(0.0,1.0)
plt.xticks(np.arange(0, len(dictionary['falling'])/30, 1))
plt.savefig('./results/output_plot_cnn.png')
