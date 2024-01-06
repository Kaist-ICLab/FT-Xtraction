# FT-Xtraction
FT-Xtraction is a locally hosted video processing and analysis website built on Python. It allows you to process videos by extracting features from it (further details down below), and analyze the processed videos. During the analysis, you can view the extracted features in a line chart that updates in real time with the video. You can also add video overlays in case you want to analyze certain features in real time. If the in-built features don’t fit your needs, you can add custom features quite easily (instructions given in the documentation and the “User Guide” page of the website).

## Setup

First, to install all the dependencies, run:

```console
$ pip install -r requirements.txt
```

Next, before being able to run the website, you must install a couple machine learning models. You don’t have to find and download the models by yourself, simply run:

```console
$ python model_setup.py
```

Then you can simply run the following to access the website:

```console
$ python main.py
```
Before you can process and analyze your videos, you must upload them to the correct directory with the requisite supplementary files; the instructions to do so are given in the “User Guide” page of the website as well as the documentation.

## Main Pages
FT-Xtraction has three main pages.

- **User Guide:** This page provides instructions on how to upload the videos and the supplementary files to the proper directories, as well as how to create custom features.

- **Feature Extraction:** This page is where you process your videos. Upon opening the page, you can see what videos can be processed, whether they have already been processed or not, and how many features have been processed. From here, you can select the video you want to process, the feature you want extracted, and the significant moments you want extracted. Once processing starts, a popup appears showing the processing progress as well as how much time is left until a given video is finished. Processing can be ended any time; all the features extracted until that point will still be saved in a CSV. Due to how the CSVs are created and how they are processed during video analysis, you must use this page to process your videos.

- **Video Analysis:** This page is where you analyze the processed videos. The videos that can be analyzed are listed on the page; if a video wasn’t processed using the feature extraction page or if the video is not supplemented with the appropriate files, then it will not show up. After selecting the video, you can select which overlays you want to see, which significant moments you want highlighted, what extracted features you want to see, and even which person’s extracted features you want to focus on.

## Analysis Tools
FT-Xtraction provides three different analytical tools for video analyses. 

- **Feature Extraction:** This allows you to extract certain features and gain insights from them. These extracted features are placed in a CSV and displayed on a line chart in the video analysis page. 

- **Significant Moments:** This allows you to highlight certain frames in the video which are considered significant; markers will be placed on the video progress bar in the video analysis page to show these significant moments. More information is provided in the documentation.

- **Video Overlays:** This allows you to see certain extracted features in real time as overlays on the video. More information is provided in the documentation.

## In-Built Features
FT-Xtraction was prototyped around multi-person behavior analysis. As such it extracts the following features:

Base Features:
- Facial Emotions
- Facial Landmarks
- Pose Key Points

Derived Features:
- Total Expressed Emotions
- Emotion Entropy
- Emotion Synchronicity
- Lip Distance
- Social Gaze Detection
- People Proximities
- Pose Synchronicity
- Physical Activeness

More details regarding these features, as well as what base and derived features are, are given in the documentation.
