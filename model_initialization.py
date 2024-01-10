import tensorflow as tf
import cv2 as cv
import mediapipe as mp

# This file is used to initialize all the machine learning models used.

#--------------------POSE DETECTION SETUP--------------------
# Used to limit the pose detection model's memory usage. This is to prevent any issues when using multiple
# models concurrently.
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

movenet = tf.saved_model.load("feature_extraction/base_feature_extraction_utils/pose_detection")

pose_model = movenet.signatures['serving_default']

pose_input_size = [352, 608]

#--------------------FACE DETECTION SETUP--------------------
# There are two models initialized here. The first is the Haar Cascades model given by opencv and the second is the
# mediapipe facial detection model. The mediapipe model can handle most facial detection cases, however in some rare
# situations it cannot, we rely on Haar Cascades as a backup.
cascade_classifier = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_profileface.xml')

mp_face_detection = mp.solutions.face_detection
pipe_detector = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)

#--------------------FACE LANDMARK DETECTION SETUP--------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
