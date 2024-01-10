import numpy as np
import cv2 as cv
import face_recognition as fr

import settings


# Extracts the face encoding from an image of a face.
def get_face_encoding(face_img_path):
    img = cv.imread(face_img_path)
    encoded = fr.face_encodings(img, known_face_locations=[(1, 1, img.shape[1] - 1, img.shape[0] - 1)])
    return encoded


# This class is used as a data container while processing videos.
class Person:
    def __init__(self, name, face_img_path, n_frames):
        self.name = name
        self.encoding = get_face_encoding(face_img_path)[0]

        emotion_vectors = np.zeros((n_frames, 7), dtype=np.uint8)
        pose_keypoints = np.zeros((n_frames, 17, 2), dtype=np.float32)
        face_landmarks = np.zeros((n_frames, 468, 3), dtype=np.float32)
        # This list contains all of the extracted features.
        self.extracted_features = [emotion_vectors, pose_keypoints, face_landmarks]

        face_bounding_boxes = np.zeros((n_frames, 4), dtype=np.float32)
        
        self.extra_features = [face_bounding_boxes]

    def reset(self):
        for feature in self.extracted_features:
            feature *= 0
        for feature in self.extra_features:
            feature *= 0


# Used to initialize several Person classes based on the number of faces that have been uploaded for a given video.
def init_people_list(img_list):
    people_list = []
    for i in range(len(img_list)):
        name = '_'.join(img_list[i].split('.')[:-1])
        people_list.append(Person(name, img_list[i], settings.n_frames))
    return people_list


# This class is used to store all instances of the Person class and also to aggregate all the data after a specified
# amount of frames.
class InfoTable:
    def __init__(self, img_list):
        self.people_list = init_people_list(img_list)
        self.encodings = [person.encoding for person in self.people_list]

    # extracts the requested data from a given image.
    def extract_data(self, img, cur_frame, base_feature_extraction_inds):
        for i in range(len(base_feature_extraction_inds)):
            ind = base_feature_extraction_inds[i]
            face_bbs, unknown_encodings, information = settings.base_feature_functions[ind](img, len(self.people_list))
            resolved_people = self.resolve_people(unknown_encodings)
            for j in range(len(resolved_people)):
                if resolved_people[j] != -1:
                    self.people_list[j].extracted_features[ind][cur_frame] = information[resolved_people[j]]
                    if i == 0:
                        self.people_list[j].extra_features[0][cur_frame] = face_bbs[resolved_people[j]]
        
        return None

    # This function is used to match people to their encodings.
    def resolve_people(self, unknown_encoding_list):
        resolved_inds = [-1 for _ in self.people_list]
        
        if len(unknown_encoding_list) <= len(self.people_list):
            possible_inds = [i for i in range(len(self.people_list))]
            for i in range(len(unknown_encoding_list)):
                possible_encodings = [self.encodings[j] for j in possible_inds]
                best_remaining_match_ind = best_person_match(possible_encodings, unknown_encoding_list[i])

                best_match_ind = possible_inds[best_remaining_match_ind]
                resolved_inds[best_match_ind] = i
                possible_inds.remove(best_match_ind)

        else:
            possible_inds = [i for i in range(len(unknown_encoding_list))]
            for i in range(len(self.people_list)):
                possible_encodings = [unknown_encoding_list[j] for j in possible_inds]
                best_remaining_match_ind = best_person_match(possible_encodings, self.encodings[i])

                best_match_ind = possible_inds[best_remaining_match_ind]
                resolved_inds[best_match_ind] = i
                possible_inds.remove(best_match_ind)

        return resolved_inds

    # This function calculates all the requested derived features by calling the functions that calculate them. The
    # information is collected together and returned as a single array in order to be written onto a CSV file.
    def calculate_features(self, selected_feature_inds):
        all_information = []
        collected_features = []
        collected_extra_features = []
        for i in range(len(self.people_list[0].extracted_features)):
            collected_features.append(np.stack([self.people_list[j].extracted_features[i]
                                                for j in range(len(self.people_list))]))
        
        for i in range(len(self.people_list[0].extra_features)):
            collected_extra_features.append(np.stack([self.people_list[j].extra_features[i]
                                                      for j in range(len(self.people_list))]))
        
        for i in selected_feature_inds:
            accumulated_feature_i = settings.derived_features[i]["feature_extraction_function"](collected_features, collected_extra_features)
            all_information.append(accumulated_feature_i)
        
        return np.concatenate(all_information)

    # Used to extract significant moments.
    def calculate_sigm(self, selected_feature_inds, cur_frame):
        all_information = []
        collected_features = []
        collected_extra_features = []
        for i in range(len(self.people_list[0].extracted_features)):
            collected_features.append(
                np.stack([self.people_list[j].extracted_features[i] for j in range(len(self.people_list))]))

        for i in range(len(self.people_list[0].extra_features)):
            collected_extra_features.append(
                np.stack([self.people_list[j].extra_features[i] for j in range(len(self.people_list))]))

        for i in selected_feature_inds:
            accumulated_feature_i = settings.significant_moment_funcs[i](collected_features, collected_extra_features)*cur_frame
            if accumulated_feature_i > 0:
                all_information.append(accumulated_feature_i)

        return np.array(all_information)

    # Used to reset all the data array elements to 0.
    def reset(self):
        for person in self.people_list:
            person.reset()


# Used to find the person whose encoding best matches the unknowing encoding.
def best_person_match(known_encodings, unknown_encoding):
    face_distances = fr.face_distance(known_encodings, unknown_encoding)
    if len(face_distances.shape) == 1:
        return 0
    normalized = np.linalg.norm(face_distances, axis=1)
    return np.argmin(normalized)
