import face_recognition as fr
from feature_extraction.super_feature_extraction_utils import face_utils as fu, pose_utils as pu
import numpy as np

def extract_emotion(img, num_people):
    unknown_encodings=[]
    emotion_information=[]

    face_bbs = fu.detect_face_mediapipe(img)
    if not face_bbs:
        face_bbs = fu.detect_face_haar(img)
    
    for (x, y, w, h) in face_bbs:
        img_i = img[y:y+h, x:x+w]
        emotion_i = fu.classify_emotion(img_i)
        ohe_i = np.zeros(7, dtype=np.uint8)
        ohe_i[emotion_i]=1

        encoding_i = fr.face_encodings(img, known_face_locations=[(y, x + w, y + h, x)])[0]

        unknown_encodings.append(encoding_i)
        emotion_information.append(ohe_i)
        
    return face_bbs[:], unknown_encodings[:], emotion_information[:]

def extract_pose(img, num_people):
    unknown_encodings=[]
    pose_information=[]
    face_bbs=[]

    keypoints, pose_bbs = pu.detect_keypoints(img, num_people)
    for i in range(len(pose_bbs)):
        y1,x1,y2,x2 = pose_bbs[i]

        img_i = img[int(y1):int(y2), int(x1):int(x2)]
        
        face_bb_i = fu.detect_face_mediapipe(img_i)

        if not face_bb_i:
            face_bb_i = fu.detect_face_haar(img_i)
        
        if face_bb_i:
            face_bb_i=face_bb_i[0]
            face_bb_i[0]+=x1
            face_bb_i[1]+=y1
            face_bb_i[0] = int(face_bb_i[0])
            face_bb_i[1] = int(face_bb_i[1])

            x, y, w, h = face_bb_i

            encoding_i = fr.face_encodings(img, known_face_locations=[(y, x + w, y + h, x)])[0]

            unknown_encodings.append(encoding_i)
            pose_information.append(keypoints[i])
            face_bbs.append(face_bb_i)


    return face_bbs, unknown_encodings, pose_information

def extract_facial_landmarks(img, num_people):
    unknown_encodings=[]
    facial_landmark_information=[]

    face_bbs = fu.detect_face_mediapipe(img)
    if not face_bbs:
        face_bbs = fu.detect_face_haar(img)

    for (x, y, w, h) in face_bbs:
        img_i = img[y:y+h, x:x+w]
        landmarks_i = fu.extract_face_mesh(img_i)
        landmarks_i[:,0]=landmarks_i[:,0]*w+x
        landmarks_i[:, 1] = landmarks_i[:, 1] * h + y

        encoding_i = fr.face_encodings(img, known_face_locations=[(y, x + w, y + h, x)])[0]

        unknown_encodings.append(encoding_i)
        facial_landmark_information.append(landmarks_i)

    return face_bbs, unknown_encodings, facial_landmark_information