import requests
import os
import tarfile
# DELETING PLACEHOLDERS

# Placeholder files had to be placed in certain necessary but empty directories in order to upload them.
# This section simply removes these placeholders as they will cause issues during the software execution.
os.remove('./data/csv/placeholder.txt')
os.remove('./data/video/placeholder.txt')
os.remove('feature_extraction/base_feature_extraction_utils/pose_detection/placeholder.txt')

# The following two code blocks are used to download and move the requisite machine learning models
# into the proper directories.

# EMOTION MODEL DOWNLOAD
# The emotion recognition model is stored in Google Drive; we use the requests library to automatically download the
# model.
model_link = "https://drive.google.com/u/0/uc?id=1Oy_9YmpkSKX1Q8jkOhJbz3Mc7qjyISzU&export=download"
download_session = requests.Session()
response = download_session.get(model_link, stream=True)
download_token = None

for key, value in response.cookies.items():
    if key.startswith("download_warning"):
        download_token = value
        break

download_response = download_session.get(model_link, params={"confirm": download_token}, stream=True)

with open("feature_extraction/base_feature_extraction_utils/emotion_recognition/PrivateTest_model.t7", "wb") as f:
    for chunk in response.iter_content(32768):
        if chunk:
            f.write(chunk)


# POSE MODEL DOWNLOAD
# The pose detection model is downloaded from Google storage using requests.
url = "https://storage.googleapis.com/tfhub-modules/google/movenet/multipose/lightning/1.tar.gz"
model_path = 'feature_extraction/base_feature_extraction_utils/pose_detection/tf_model.tar.gz'

response = requests.get(url, stream=True)
if response.status_code == 200:
    with open(model_path, 'wb') as f:
        f.write(response.raw.read())

file = tarfile.open(model_path)
file.extractall('./feature_extraction/base_feature_extraction_utils/pose_detection')
file.close()
os.remove('feature_extraction/base_feature_extraction_utils/pose_detection/tf_model.tar.gz')
