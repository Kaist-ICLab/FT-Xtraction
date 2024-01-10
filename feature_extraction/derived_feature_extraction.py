import numpy as np

#--------------------CONSTANTS--------------------
# These are constants used in the calculations below.

# EPS is an arbitrarily small value used to prevent division by 0 and log(0) errors.
EPS = 0.0000000001
LOG_7 = np.log(7)

UPPER_LIP = [0, 37, 39, 40, 267, 269, 270]
LOWER_LIP = [17, 84, 181, 314, 405]

FACE_POINTS = [1, 33, 61, 199, 263, 291]

#--------------------MAIN FUNCTIONS--------------------


# This function collects the all the emotions expressed by everyone over a set amount of frames and combiens them
# into a vector for each person.
def calculate_total_emotion_vectors(collected_features, collected_extra_features):
    # Although collected_extra_features is not needed in this function, it is used in others. This is maintained in
    # order to allow loops to be used and to facilitate custom feature creation.

    focus_feature = collected_features[0]
    emotion_vectors = np.sum(focus_feature, axis=1, dtype=np.uint8)
    return emotion_vectors.reshape(-1)


# This function calculates the emotional entropy, or emotional randomness, of each person over a set amount of frames.
# This si done using Shannon's entropy.
def calculate_emotion_entropies(collected_features, collected_extra_features):
    focus_feature = collected_features[0]
    emotion_vectors = np.sum(focus_feature, axis=1, dtype=np.uint8)

    probs = emotion_vectors/((np.sum(emotion_vectors, axis=1)+EPS).reshape(-1, 1))
    log_probs = np.log(probs + EPS) / LOG_7
    emotion_entropies = -1*np.sum(probs * log_probs, axis=1)
    
    return emotion_entropies


# This function calculates the emotion synchronicity between every pair of people by taking the euclidean distances
# between the total emotion vectors of each person.
def calculate_emotion_synchronicities(collected_features, collected_extra_features):
    num_pairs = int((collected_features[0].shape[0]*(collected_features[0].shape[0]-1))/2)

    focus_feature = collected_features[0]
    emotion_vectors = np.sum(focus_feature, axis=1, dtype=np.uint8)

    emotion_synchronicities = np.zeros(num_pairs, dtype=np.float32)

    acc = 0

    for i in range(emotion_vectors.shape[0]-1):
        synchronocities_i = np.sqrt(np.sum((emotion_vectors[i]-emotion_vectors)**2, axis=1))[i+1:]
        emotion_synchronicities[acc:acc+len(synchronocities_i)] = synchronocities_i
        acc += len(synchronocities_i)
    
    return emotion_synchronicities


# This function calculates the average lip movement of people. This is done by taking the upper and lower lip
# keypoints, taking the vertical distances between the average lip keypoints, and finding the average of the euclidean
# distance between the lip distance in one frame and the lip distance in the following frame.
def calculate_lip_movement(collected_features, collected_extra_features):
    focus_feature = collected_features[2][:, :, :, 1]

    lip_points_upper = focus_feature[:, :, UPPER_LIP]
    lip_points_lower = focus_feature[:, :, LOWER_LIP]

    avg_upper_y = np.mean(lip_points_upper, axis=-1)
    avg_lower_y = np.mean(lip_points_lower, axis=-1)

    lip_distances = avg_lower_y-avg_upper_y
    lip_before = lip_distances[:, :-1]
    lip_after = lip_distances[:, 1:]
    average_movement = np.mean(np.abs(lip_after-lip_before), axis=-1)

    return average_movement


# This is used to calculate whether two people interacted or not; this is done by determining the gaze direction of one
# person, projecting it onto the bounding box of another person, and seeing if there is a collision. The gaze direction
# calculated using the chin, forehead, and nose keypoints.
def calculate_interactions(collected_features, collected_extra_features):
    focus_feature = collected_features[2]
    extra_feature = collected_extra_features[0]

    num_pairs = int((focus_feature.shape[0]*(focus_feature.shape[0]-1))/2)
    interactions = np.zeros(num_pairs, dtype=np.uint8)

    acc = 0

    for i in range(focus_feature.shape[0]-1):
        directions_i = get_direction(focus_feature[i])
        for j in range(i+1, focus_feature.shape[0]):
            directions_j = get_direction(focus_feature[j])
            for k in range(len(directions_i)):
                # calculating the gaze direction
                origin_x_i = focus_feature[i, k, 1, 0]
                origin_y_i = focus_feature[i, k, 1, 1]
                m_i = directions_i[0][k]
                d_i = directions_i[1][k]
                lower_x_i = extra_feature[i][k][0]
                lower_y_i = extra_feature[i][k][1]
                upper_x_i = extra_feature[i][k][0] + extra_feature[i][k][2]
                upper_y_i = extra_feature[i][k][1] + extra_feature[i][k][3]

                origin_x_j = focus_feature[j, k, 1, 0]
                origin_y_j = focus_feature[j, k, 1, 1]
                m_j = directions_j[0][k]
                d_j = directions_j[1][k]
                lower_x_j = extra_feature[j][k][0]
                lower_y_j = extra_feature[j][k][1]
                upper_x_j = extra_feature[j][k][0] + extra_feature[j][k][2]
                upper_y_j = extra_feature[j][k][1] + extra_feature[j][k][3]

                interaction_ij = detect_interaction(origin_x_i, origin_y_i, m_i, d_i, lower_x_j, upper_x_j, lower_y_j,
                                                    upper_y_j)
                interaction_ji = detect_interaction(origin_x_j, origin_y_j, m_j, d_j, lower_x_i, upper_x_i, lower_y_i,
                                                    upper_y_i)

                if interaction_ij or interaction_ji:
                    interactions[acc] += 1

            acc += 1
    
    return interactions


# Calculates the average activeness of each person; this is done by taking the euclidean distance between one frame
# and the frame following it.
def calculate_activeness(collected_features, collected_extra_features):
    focus_feature = collected_features[1]

    activeness = np.zeros(focus_feature.shape[0], dtype=np.float32)
    for i in range(focus_feature.shape[0]):
        activeness_i = focus_feature[i]

        activeness_before = activeness_i[:-1]
        activeness_after = activeness_i[1:]
        average_activeness_i = np.sum(activeness_after-activeness_before)/activeness_before.shape[0]

        activeness[i] = average_activeness_i
    
    return activeness

# Calculates the average distance between people; this is done by taking the average euclidean distance between the
# pose keypoints of two people
def calculate_people_proximities(collected_features, collected_extra_features):
    focus_feature = collected_features[1]

    num_pairs = int(focus_feature.shape[0]*(focus_feature.shape[0]-1)/2)
    people_proximities = np.zeros(num_pairs, dtype=np.float32)

    acc = 0

    for i in range(focus_feature.shape[0]-1):
        avg_keypoints = np.mean(focus_feature, axis=1)
        proximities_i = np.sqrt(np.sum((avg_keypoints[i]-avg_keypoints)**2, axis=-1))
        proximities_i = np.mean(proximities_i, axis=-1)[i+1:]
        people_proximities[acc:acc+len(proximities_i)] = proximities_i
        acc += len(proximities_i)

    return people_proximities


# Calculates the pose synchronicity between each pair of people. This is done by first calculating a few major pose
# angles that we determined and finding the average euclidean distance between those among the set amount of frames.
def calculate_pose_synchronicities(collected_features, collected_extra_features):
    focus_feature = collected_features[1]

    angles = np.zeros((focus_feature.shape[0], 8))

    avg_keypoints = np.mean(focus_feature, axis=1)
    for i in range(focus_feature.shape[0]):
        angles[i] = calculate_pose_angles(avg_keypoints[i])

    num_pairs = int(focus_feature.shape[0]*(focus_feature.shape[0]-1)/2)
    pose_synchronicities = np.zeros(num_pairs, dtype=np.float32)

    acc = 0

    for i in range(focus_feature.shape[0]-1):
        synchronicities_i = np.sqrt(np.sum((angles[i]-angles)**2, axis=-1))[i+1:]
        pose_synchronicities[acc:acc+len(synchronicities_i)] = synchronicities_i
        acc += len(synchronicities_i)

    return pose_synchronicities


#-SIG MOMENTS-
def detect_multiple_people(collected_features, collected_extra_features):
    inf = calculate_interactions(collected_features, collected_extra_features)
    if np.sum(inf) > 0:
        return 1
    else:
        return 0

#--------------------UTILS--------------------


DIRECTION_POINTS = [10, 152]

# Calculates the gaze direction based on chin and forehead keypoints
def get_direction(landmarks):
    coords = landmarks[:, DIRECTION_POINTS, :2]
    nose = landmarks[:, 1, :2]

    den = (coords[:, 0, 1]-coords[:, 1, 1])
    for i in range(len(den)):
        if den[i] == 0:
            den[i] += 0.0000001

    m = (coords[:, 1, 0]-coords[:, 0, 0])/den

    mean_x = np.mean(coords[:, :, 0], axis=1)
    d = np.ones(landmarks.shape[0])
    for i in range(len(landmarks)):
        if nose[i, 0] < mean_x[i]:
            d[i] = -1
    return m, d


# This function projects the gaze direction of one person onto the facial bounding box of another; if a collision
# between the projected gaze and the bounding box occurs, a collision is detected.
def detect_interaction(origin_x, origin_y, m, d, lower_x, upper_x, lower_y, upper_y):
    if d == 1:
        y_projected = origin_y+(lower_x-origin_x)*m
    else:
        y_projected = origin_y + (upper_x - origin_x) * m

    if y_projected < upper_y and y_projected > lower_y:
        return 1
    else:
        return 0


# Function to calculate the pre-determined pose angles using the dot product rule.
def calculate_pose_angles(keypoints):
    left_forearm = keypoints[10] - keypoints[8]
    left_upper_arm = keypoints[6] - keypoints[8]
    left_side = keypoints[12] - keypoints[6]
    left_thigh = keypoints[12] - keypoints[14]
    left_shin = keypoints[16] - keypoints[14]
    right_forearm = keypoints[9] - keypoints[7]
    right_upper_arm = keypoints[5] - keypoints[7]
    right_side = keypoints[11] - keypoints[5]
    right_thigh = keypoints[11] - keypoints[13]
    right_shin = keypoints[15] - keypoints[13]
    angles = np.zeros(8)
    connections = np.array([[left_forearm, left_upper_arm], [-left_upper_arm, left_side], [-left_side, -left_thigh],
                            [left_thigh, left_shin], [right_forearm, right_upper_arm], [-right_upper_arm, right_side],
                            [-right_side, -right_thigh], [right_thigh, right_shin]])

    for i in range(len(connections)):
        connection_dot = np.dot(connections[i][0], connections[i][1])
        connection_mags = np.linalg.norm(connections[i][0]) * np.linalg.norm(connections[i][1])
        angles[i] = connection_dot / (connection_mags+EPS)

    return np.arccos(angles)
