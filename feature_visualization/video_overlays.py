from feature_extraction.super_feature_extraction_utils import face_utils as fu, pose_utils as pu
import numpy as np
import settings
import cv2 as cv
import face_recognition as fr


overlay_names=["Person Identification", "Emotion Recognition", "Pose Detection"]

def draw_people(img):
    encoding_list = settings.encodings[settings.current_video_ind]

    face_bbs = fu.detect_face_mediapipe(img)
    if not face_bbs:
        face_bbs = fu.detect_face_haar(img)
    if not face_bbs:
        return img
    
    unknown_encoding_list = [settings.get_encoding_im(img, bb) for bb in face_bbs]
    
    resolved_inds = resolve_people(encoding_list, unknown_encoding_list)

    for i in range(len(resolved_inds)):
        (x,y,w,h) = face_bbs[resolved_inds[i]]

        rect_p1 = (x, y)
        rect_p2 = (x + w, y + h)
        rect_color = (255,255,0)
        rect_thick = 2

        text_p1 = (x, y + h + 30)
        name = settings.img_names[settings.current_video_ind][resolved_inds[i]]
        text_font = cv.FONT_HERSHEY_SIMPLEX
        text_scale = 1
        text_color = (255, 255, 0)
        text_thick = 2
        text_line_style = cv.LINE_AA

        cv.rectangle(img, rect_p1, rect_p2, rect_color, rect_thick)
        cv.putText(img, name, text_p1, text_font, text_scale, text_color, text_thick, text_line_style)
    
    return img

def draw_emotion(img):
    face_bbs = fu.detect_face_mediapipe(img)
    if not face_bbs:
        face_bbs = fu.detect_face_haar(img)
    if not face_bbs:
        return img

    for (x,y,w,h) in face_bbs:
        emotion_ind = fu.classify_emotion(img[y:y + h, x:x + w])

        rect_p1 = (x,y)
        rect_p2 = (x+w,y+h)
        rect_color = (255,255,0)
        rect_thick = 2

        text_p1 = (x,y+h+30)
        emotion = settings.EMOTIONS[emotion_ind]
        text_font = cv.FONT_HERSHEY_SIMPLEX
        text_scale = 1
        text_color = (255,255,0)
        text_thick = 2
        text_line_style = cv.LINE_AA

        cv.rectangle(img, rect_p1, rect_p2, rect_color, rect_thick)
        cv.putText(img, emotion, text_p1,text_font,text_scale,text_color,text_thick,text_line_style)

    return img

def draw_pose(img):
    keypoints, pose_bbs = pu.detect_keypoints(img, len(settings.img_lists[settings.current_video_ind]))
    
    for i in range(len(keypoints)):
        keypoints_i=keypoints[i]*np.array([img.shape[0], img.shape[1]])
        for keypoint in keypoints_i:
            cv.circle(img, (int(keypoint[1]), int(keypoint[0])), 4, (0, 255, 0), -1)
        for edge in settings.EDGES:
            p1, p2 = edge
            y1, x1 = keypoints_i[p1]
            y2, x2 = keypoints_i[p2]
            cv.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
    return img


#------
def best_person_match(known_encodings, unknown_encoding):
    # print(known_encodings)
    # print(unknown_encoding)
    face_distances = fr.face_distance([kn[0] for kn in known_encodings], unknown_encoding[0])
    if len(face_distances.shape)==1:
        return 0
    normalized=np.linalg.norm(face_distances, axis=1)
    return np.argmin(normalized)

def resolve_people(known_encoding_list, unknown_encoding_list):
    resolved_inds = [-1 for _ in known_encoding_list]
    
    if len(unknown_encoding_list)<=len(known_encoding_list):    
        possible_inds = [i for i in range(len(known_encoding_list))]
        for i in range(len(unknown_encoding_list)):
            possible_encodings = [known_encoding_list[j] for j in possible_inds]
            best_remaining_match_ind = best_person_match(possible_encodings,unknown_encoding_list[i])

            best_match_ind = possible_inds[best_remaining_match_ind]
            resolved_inds[best_match_ind] = i
            possible_inds.remove(best_match_ind)

    else:
        possible_inds = [i for i in range(len(unknown_encoding_list))]
        for i in range(len(known_encoding_list)):
            possible_encodings = [unknown_encoding_list[j] for j in possible_inds]
            best_remaining_match_ind = best_person_match(possible_encodings,known_encoding_list[i])

            best_match_ind = possible_inds[best_remaining_match_ind]
            resolved_inds[best_match_ind] = i
            possible_inds.remove(best_match_ind)

    return resolved_inds

overlay_functions=[draw_people,draw_emotion,draw_pose]