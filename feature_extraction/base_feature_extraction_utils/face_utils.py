import cv2 as cv
from feature_extraction.base_feature_extraction_utils.emotion_recognition import emotion_recognizer as e_rec
import numpy as np
import model_initialization


# Detects faces from an image using the Haar Cascades model initialized in "./model_intialization.py"
def detect_face_haar(img):
    g_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = model_initialization.cascade_classifier.detectMultiScale(g_img, scaleFactor=1.1, minNeighbors=5)
    face_bounding_boxes = []

    for (x, y, w, h) in faces:
        face_bounding_boxes.append([x, y, w, h])

    if not face_bounding_boxes:
        return []

    return face_bounding_boxes

# Detects faces from an image using the mediapipe model initialized in "./model_intialization.py"
def detect_face_mediapipe(img):

    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    faces = model_initialization.pipe_detector.process(rgb_img)
    face_bounding_boxes = []

    if faces.detections is None:
        return []

    for face in faces.detections:
        bounding_box = face.location_data.relative_bounding_box
        x = int(bounding_box.xmin * img.shape[1])
        y = int(bounding_box.ymin * img.shape[0])
        w = int(bounding_box.width * img.shape[1])
        h = int(bounding_box.height * img.shape[0])
        face_bounding_boxes.append([x, y, w, h])

    return face_bounding_boxes


# Classifies the emotions of a person using the emotion recognition model in
# "./feature_extraction/base_feature_extraction_utils/emotion_recognition.
def classify_emotion(img):
    return e_rec.classify_emotion(img)


# Extracts the facial landmarks of a person using the model defined in "./model_intialization.py".
def extract_face_mesh(img):
    landmarks = np.zeros((468, 3))

    rgb_img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    rgb_img.flags.writeable = False
    
    img_face_mesh = model_initialization.face_mesh.process(rgb_img)
    
    if img_face_mesh.multi_face_landmarks:
        for i in range(len(img_face_mesh.multi_face_landmarks[0].landmark)):
            landmarks[i] = [img_face_mesh.multi_face_landmarks[0].landmark[i].x,
                            img_face_mesh.multi_face_landmarks[0].landmark[i].y,
                            img_face_mesh.multi_face_landmarks[0].landmark[i].z]
    
    return landmarks
