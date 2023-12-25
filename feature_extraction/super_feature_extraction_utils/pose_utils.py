import numpy as np
import tensorflow as tf
import setup

def detect_keypoints(img, num_people):

    resized_img = tf.expand_dims(tf.cast(tf.image.resize_with_pad(img, setup.pose_input_size[0], setup.pose_input_size[1]), dtype=tf.int32), axis=0)
    predictions = setup.pose_model(resized_img)['output_0'].numpy()
    keypoints = predictions[:, :num_people, :51].reshape((num_people, 17, 3))[:,:,:-1]
    bounding_boxes = predictions[:, :num_people, 51:].reshape((num_people, -1))[:,:-1]
    bounding_boxes *= np.array([img.shape[0], img.shape[1], img.shape[0], img.shape[1]])

    return keypoints, bounding_boxes