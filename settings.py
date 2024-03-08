import os
import csv
import numpy as np
import face_recognition as fr

import cv2 as cv

from feature_extraction import base_feature_extraction as sfe, derived_feature_extraction as fa

#--------------------SERVER FLAGS--------------------
# Flags used during server operation; used to signal shutdowns, terminate video processing, and perform video
# replays.
server_running = True
end_processing = False
end_video = False

#--------------------EXTRACTION SETTINGS--------------------
# Sets up lists containing the paths of all the videos and their supplementary files.
video_data_dir = "./data/video"
csv_data_dir = "./data/csv"
vids = [i for i in os.listdir(video_data_dir) if i != ".DS_Store"]
video_list = [os.path.join(video_data_dir, i, j) for i in vids for j in os.listdir(os.path.join(video_data_dir, i))
              if j != "img" and j != ".DS_Store"]
video_names = [vid_path.split("/")[-1] for vid_path in video_list]

img_lists = [[os.path.join(video_data_dir, i, "img", j) for j in os.listdir(os.path.join(video_data_dir, i, "img"))] for
             i in vids]
img_names = [[".".join(j.split(".")[:-1]) for j in os.listdir(os.path.join(video_data_dir, i, "img"))] for i in vids]
fixed_face_positions=[]
fixed_face_ordering = False


# helper function to get the face encoding of a person from an image.
def get_encoding(img_path):
    img = cv.imread(img_path)
    encoded = fr.face_encodings(img, known_face_locations=[(1, 1, img.shape[1] - 1, img.shape[0] - 1)])
    return encoded


# helper function to get the face encoding of a person from an image containing other people.
def get_encoding_im(img, bb):
    x, y, w, h = bb
    img_i = img[y:y+h, x:x+w]
    encoded = fr.face_encodings(img, known_face_locations=[(1, 1, img_i.shape[1] - 1, img_i.shape[0] - 1)])
    return encoded


encodings = [[get_encoding(j) for j in i] for i in img_lists]

# Lists that are filled with the requisite information and sent to the client side in order to inform the user
# of which videos have been processed and with how many features.
csv_exists = [] 
num_features = []
n_frames = 10

# List of all the features that can be extracted.
base_feature_functions = [sfe.extract_emotion, sfe.extract_pose, sfe.extract_facial_landmarks]
derived_features = [{"feature_name": "Total Emotion Vectors", "feature_extraction_function":
                fa.calculate_total_emotion_vectors, "base_derived_mapping": 0},
            {"feature_name": "Emotion Entropy", "feature_extraction_function":
                fa.calculate_emotion_entropies, "base_derived_mapping": 0},
            {"feature_name": "Emotion Synchronicity", "feature_extraction_function":
                fa.calculate_emotion_synchronicities, "base_derived_mapping": 0},
            {"feature_name": "Lip Movement", "feature_extraction_function":
                fa.calculate_lip_movement, "base_derived_mapping": 2},
            {"feature_name": "Interactions", "feature_extraction_function":
                fa.calculate_interactions, "base_derived_mapping": 2},
            {"feature_name": "People Proximities", "feature_extraction_function":
                fa.calculate_people_proximities, "base_derived_mapping": 1},
            {"feature_name": "Pose Synchronicity", "feature_extraction_function":
                fa.calculate_pose_synchronicities, "base_derived_mapping": 1},
            {"feature_name": "Activeness", "feature_extraction_function":
                fa.calculate_activeness, "base_derived_mapping": 1}]

# List containing the derived feature; this information is used only for video processing and chart name creation.
feature_processing_info = {"Total Emotion Vectors": {"is_pair": False, "sub_name_list":
                           ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']},
                           "Emotion Entropy": {"is_pair": False, "sub_name_list": None},
                           "Emotion Synchronicity": {"is_pair": True, "sub_name_list": None},
                           "Lip Movement": {"is_pair": False, "sub_name_list": None},
                           "Interactions": {"is_pair": True, "sub_name_list": None},
                           "People Proximities": {"is_pair": True, "sub_name_list": None},
                           "Pose Synchronicity": {"is_pair": True, "sub_name_list": None},
                           "Activeness": {"is_pair": False, "sub_name_list": None}}


# This function is used to update the lists containing the metadata.
def update_lists():
    global video_names, csv_exists, video_list, csv_list, num_features, csv_data_dir
    csv_list = os.listdir(csv_data_dir)
    csv_exists = []
    num_features = []
    for i in range(len(video_names)):
        csv_name = f"{'.'.join(video_names[i].split('.')[:-1])}.csv"
        if csv_name not in csv_list:
            csv_exists.append("MISSING")
            num_features.append("")
        else:
            csv_exists.append("FOUND")
            with open(os.path.join(csv_data_dir, csv_name), 'r', newline='') as csv_file:
                row_length = len(next(csv.reader(csv_file, delimiter=',')))
            num_features.append(str(row_length))


#--------------------ANALYSIS SETTINGS--------------------
EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
EDGES = [(0, 1), (0, 2), (1, 3), (2, 4), (0, 5), (0, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 6), (5, 11), (6, 12),
         (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]

significant_moment_names = ["Interaction Detected"]
significant_moment_funcs=[fa.detect_multiple_people]

# The following are all flags and information used in video analysis
capture = None
current_video_ind = 0
feature_data = None
derived_feature_names = None
feature_names = None
frames = None
feature_offsets = None
sig_names = None
sig_data = None
overlay_flags = []

video_paused = True
video_skip = False
video_replay = False
video_ended = False
current_frame = 0
skip_frame = 0
video_max_frames = 0
fps = 60

feature_graph_colors = None
sig_colors = None


# This function loads the data necessary for analyzing a select video.
def load_video():
    global capture, current_video_ind, feature_data, feature_names, derived_feature_names, frames, video_skip,\
        video_replay, video_ended, current_frame, skip_frame, video_max_frames, feature_graph_colors, sig_colors, \
        feature_offsets, video_paused, fps, sig_names, sig_data

    # The validity of a video is checked before it is analyzed; invalid videos can cause errors.
    check_validity()
    if capture is not None:
        # Necessary if a previous video is already loaded
        capture.release()

    # Loading the chosen video and collecting the requisite meta data.
    capture = cv.VideoCapture(video_list[current_video_ind])
    video_max_frames = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
    fps = int(capture.get(cv.CAP_PROP_FPS))
    video_name = '.'.join(video_names[current_video_ind].split('.')[:-1])
    people_names = img_names[current_video_ind]

    # Processing the supporting CSV for the chosen video's analysis.
    feature_names, derived_feature_names, feature_data, feature_graph_colors = process_csv(video_name, people_names)

    # Significant moments are stored in a separate file.
    if f"{video_name}_sig.csv" in os.listdir(csv_data_dir):
        sig_names, sig_data, sig_colors = process_sig_csv(video_name)
    else:
        sig_names, sig_data, sig_colors = [], [], []

    video_paused = True
    video_skip = False
    video_replay = False
    video_ended = False
    current_frame = 0
    skip_frame = 0
    frames = [i for i in range(0, len(feature_data[0][0]), n_frames)]
    frames = [i*n_frames for i in range(0, len(feature_data[0][0]))]
    feature_offsets = get_feature_offsets(derived_feature_names)
    return None


# Used to process the CSVs pertaining to the significant moments of a select video.
def process_sig_csv(video_name):
    extracted_feature_names = []
    sig_lists = []
    sig_colors = []

    with open(os.path.join(csv_data_dir,f"{video_name}_sig.csv"), 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        extracted_feature_names = next(csv_reader)
        sig_lists = [[] for i in extracted_feature_names]
        # Since an unconstrained number of people and features can be extracted, chart color are randomly generated.
        raw_sig_colors = (np.random.rand(len(sig_lists), 3) * 255).astype(np.uint8).tolist()
        sig_colors = [f"rgb({color[0]}, {color[1]}, {color[2]})" for color in raw_sig_colors]

        for row in csv_reader:
            int_row = [int(val) for val in row]
            for i in range(len(int_row)):
                sig_lists[i].append(int_row[i])

    return extracted_feature_names, sig_lists, sig_colors


# Used to process the CSVs pertaining to the extracted features of a select video.
def process_csv(video_name, people_names):
    extracted_feature_names = []
    extracted_derived_feature_names = []
    extracted_feature_data = []
    graph_colors = None
    
    extraction_feature_inds = []

    with open(os.path.join(csv_data_dir,f"{video_name}.csv"), 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        extracted_feature_names = next(csv_reader)[1:]

        graph_colors = create_graph_colors(extracted_feature_names, len(people_names))
        
        extracted_derived_feature_names, extracted_feature_data, extraction_feature_inds = \
            create_processing_lists(extracted_feature_names, people_names)
    
        for row in csv_reader:
            float_row = [float(val) for val in row[1:]]
            
            for i in range(len(extracted_feature_names)):
                for j in range(len(extraction_feature_inds[i])):
                    extracted_feature_data[i][j].append(float_row[extraction_feature_inds[i][j]])

    return extracted_feature_names, extracted_derived_feature_names, extracted_feature_data, graph_colors


# Graph colors have to be randomly generated since there are no limits to the number of people and
# sub-categories to be displayed
def create_graph_colors(extracted_feature_names, num_people):
    stored_colors = {}
    graph_colors = []

    for i in range(len(extracted_feature_names)):
        feature_details_i = feature_processing_info[extracted_feature_names[i]]
        if feature_details_i["is_pair"]:
            num_pair = int(num_people*(num_people-1)/2)
            if feature_details_i["sub_name_list"] is None:
                num_colors_i = num_pair
                stored_color_type_i = "pair_no_sub"
            else:
                num_colors_i = num_pair*len(feature_details_i["sub_name_list"])
                stored_color_type_i = "pair_sub"
        else:
            if feature_details_i["sub_name_list"] is None:
                num_colors_i = num_people
                stored_color_type_i = "no_pair_no_sub"
            else:
                num_colors_i = num_people*len(feature_details_i["sub_name_list"])
                stored_color_type_i = "no_pair_sub"
        
        if stored_color_type_i not in stored_colors:
            stored_colors[stored_color_type_i] = (np.random.rand(num_colors_i, 3)*255).astype(np.uint8).tolist()
            
        graph_colors.append(stored_colors[stored_color_type_i])
    
    return graph_colors


# Before loading all the data and transferring it to the client, several lists must be first created
# to save the data in.
def create_processing_lists(extracted_feature_names, people_names):
    extracted_derived_feature_names = []
    extracted_feature_data = []
    extraction_feature_inds = []
    acc = 0

    for i in range(len(extracted_feature_names)):
        feature_details_i = feature_processing_info[extracted_feature_names[i]]
        derived_feature_names_i = []
        feature_data_i = []
        feature_inds_i = []

        # Creating lists for all features that analyze people in pairs.
        if feature_details_i["is_pair"]:
            for j in range(len(people_names)-1):
                for k in range(j+1,len(people_names)):
                    name_jk = f"{people_names[j]}-{people_names[k]}"
                    if feature_details_i["sub_name_list"] is not None:
                        for sub_name in feature_details_i["sub_name_list"]:
                            derived_feature_names_i.append(f"{name_jk}: {sub_name}")
                            feature_data_i.append([])
                            feature_inds_i.append(acc)
                            acc += 1
                    else:
                        derived_feature_names_i.append(name_jk)
                        feature_data_i.append([])
                        feature_inds_i.append(acc)
                        acc += 1

        # Creating lists for all features that analyze people individually.
        else:
            for j in range(len(people_names)):
                name_j = people_names[j]

                if feature_details_i["sub_name_list"] is not None:
                    for sub_name in feature_details_i["sub_name_list"]:
                        derived_feature_names_i.append(f"{name_j}: {sub_name}")
                        feature_data_i.append([])
                        feature_inds_i.append(acc)
                        acc += 1
                else:
                    derived_feature_names_i.append(name_j)
                    feature_data_i.append([])
                    feature_inds_i.append(acc)
                    acc += 1
        
        extracted_derived_feature_names.append(derived_feature_names_i)
        extracted_feature_data.append(feature_data_i)
        extraction_feature_inds.append(feature_inds_i)
    
    return extracted_derived_feature_names, extracted_feature_data, extraction_feature_inds


# This is a sanitization function for the extracted feature CSVs; if the CSVs are corrupted or
# are incorrectly processed, then the software is stopped.
def check_validity():
    global current_video_ind, img_names
    video_name = '.'.join(video_names[current_video_ind].split('.')[:-1])
    header = None
    num_feature_csv = 0
    num_feature_true = 0

    if f"{video_name}.csv" not in os.listdir(csv_data_dir):
        print(f"CSV for the video '{video_name}' not found")
        exit()

    with open(os.path.join(csv_data_dir,f"{video_name}.csv"), 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        header = next(csv_reader)[1:]
        data = next(csv_reader)
        num_feature_csv = len(data)

    # Checks if only valid features were extracted; also checks for if the CSV was processed using the software or not.
    for feature in header:
        if feature not in feature_processing_info:
            print(f"{feature} is not a valid feature name")
            exit()

    num_people = len(img_names[current_video_ind])

    # Checking whether the number of elements in the extracted data matches expected number given the selected
    # features and number of people.
    for i in range(len(header)):
        feature_details_i = feature_processing_info[header[i]]
        if feature_details_i["is_pair"]:
            num_pair = int(num_people*(num_people-1)/2)
            if feature_details_i["sub_name_list"] is None:
                num_feature_true += num_pair
            else:
                num_feature_true += num_pair*len(feature_details_i["sub_name_list"])
        else:
            if feature_details_i["sub_name_list"] is None:
                num_feature_true += num_people
            else:
                num_feature_true += num_people*len(feature_details_i["sub_name_list"])
    
    if num_feature_true+1 != num_feature_csv:
        print(f"Expected {num_feature_true+1} data points per row in csv, received {num_feature_csv}")
        exit()
    
    return None


# This is used to facilitate the creation of the feature charts on the client side.
def get_feature_offsets(derived_feature_names):
    feature_offsets = [0]
    for i in range(len(derived_feature_names)-1):
        feature_offsets.append(feature_offsets[i]+len(derived_feature_names[i]))
    return feature_offsets
