# FT-Xtraction
FT-Xtraction is a locally hosted video processing and analysis website built on Python. It allows you to process videos by extracting features from it (further details down below), and analyze the processed videos. During the analysis, you can view the extracted features in a line chart that updates in real time with the video. You can also add video overlays in case you want to analyze certain features in real time. If the in-built features don’t fit your needs, you can add custom features quite easily (instructions given in the documentation).

## Motivation
Video data analysis has been used in a variety of applications, including urban traffic surveillance, sports coaching, surgical, video retrieval and education. Furthermore, advances in artificial intelligence have enabled researchers to use video analysis for complex tasks such as detecting nuances that are known to be difficult for machines to predict.; more specifically, video data has been used in melancholia detection, social behavior analysis in mice, behavior analysis of children with autism for the purpose of improving teaching, and so on.

However, conducting behavior analysis research involving video data currently requires researchers to either create custom software to analyze and process their data, use software specific to their task, or use an ensemble of software to complete separate aspects of the task. This poses an issue due to the amount of resources needed to create the software, as well as the fact that not all researchers possess the programming skills necessary to create such software. Furthermore, using an ensemble of software may prove to be inconvenient because researchers may face compatibility issues.

Although existing tools provide excellent platforms for extracting features from videos and sharing data, they lack two aspects that would greatly enhance usability: (1) researchers can only use the features given to them by the software; they cannot implement and extract their own features, (2) existing tools do not allow for features to be visualized and overlaid onto the video, which may provide researchers with vital insights.

This is where FT-Xtraction comes in; a software that supports behavioral analysis for researchers in processing video data, analyzing the processed data, visualizing the data through charts and video overlays, and creating their own custom features. Researchers will be able to use this software through a web browser after some initial setup.

FT-Xtraction was prototyped with social emotional learning (SEL) and family functioning in mind, however it can be used in any field where video data is used.

SEL, in this context, refers to the analysis of how people express and manage their emotions in social settings; more simply, it analyzes how people behave in certain social interactions. Many of the behavior metrics in SEL were created to evaluate the behavior and emotional control of children, particularly those with autism or some other kind of handicap. %However, as will be shown below, these metrics can also be used to evaluate how adults behave in certain situations.

Family functioning in this context refers to how family members act around each other and how well they get along. Many of the metrics that evaluate family functioning essentially evaluate the behavior of one family member towards another, which is similar to the metrics used in SEL. This allows family function to be a motivating task for this software as in SEL.

## Overall Workflow
The system workflow is as follows:
1. Setup: This involves installing dependencies and models as well as moving the data to the appropriate directories).
2. Feature Extraction: You must extract your desired features by using the feature extraction page. Due to how the CSVs are created and read, using your own CSVs might lead to errors which will force the website to close.
3. Video Analysis: Now you can analyze the video as you please.

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

- **User Guide:** This page provides instructions on how to upload the videos and the supplementary files to the proper directories, as well as how to create custom features. These instructions are also written in the documentation.

- **Feature Extraction:** This page is where you process your videos. Upon opening the page, you can see what videos can be processed, whether they have already been processed or not, and how many features have been processed. From here, you can select the video you want to process, the feature you want extracted, and the significant moments you want extracted. Once processing starts, a popup appears showing the processing progress as well as how much time is left until a given video is finished. Processing can be ended any time; all the features extracted until that point will still be saved in a CSV. Due to how the CSVs are created and how they are processed during video analysis, you must use this page to process your videos.

![alt text](https://github.com/Kaist-ICLab/FT-Xtraction/blob/main/readme_imgs/feature_extraction_page.png)

- **Video Analysis:** This page is where you analyze the processed videos. The videos that can be analyzed are listed on the page; if a video wasn’t processed using the feature extraction page or if the video is not supplemented with the appropriate files, then it will not show up. After selecting the video, you can select which overlays you want to see, which significant moments you want highlighted, what extracted features you want to see, and even which person’s extracted features you want to focus on.

![alt text](https://github.com/Kaist-ICLab/FT-Xtraction/blob/main/readme_imgs/video_analysis_page.png)

## Analysis Tools
FT-Xtraction provides three different analytical tools for video analyses. 

- **Feature Extraction:** This allows you to extract certain features and gain insights from them. These extracted features are placed in a CSV and displayed on a line chart in the video analysis page. 

- **Significant Moments:** This allows you to highlight certain frames in the video which are considered significant; markers will be placed on the video progress bar in the video analysis page to show these significant moments (seen as the violet markers in the above image). More information is provided in the documentation. 

- **Video Overlays:** This allows you to see certain extracted features in real time as overlays on the video. More information is provided in the documentation.

## In-Built Features & Justifications
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

## Technical Details
To play the video by generating frames on the server side, the frames are encoded on the server side and decoded back into images on the client side. Since the client is now just receiving a stream of images instead of playing a video, it has no access to the current position of the video. This necessitates periodic communication between the server and the client in order to update the video progress. These updates were implemented using the Fetch API; a request from the client side is periodically sent to the server for the metadata of the current frame. This information is then sent back to the client and reflected on the progress bar. Whenever the video is paused, the update requests are also paused to avoid sending unnecessary requests. Although it is considered bad practice to periodically send requests with a short delay, no other aspect of the client-side implementation places a heavy load on the client. Additionally, the website is locally hosted, thus only the load of the user's processes need to be considered. This means that sending several requests within a short time period will not affect the performance of the software; this was confirmed during testing.

## Future Work
1. One of the main contributions of this project is the ability to add custom features to allow researchers from various fields to analyze their video data. Currently, in order to create custom features, one must know quite a bit of coding. However, it would be better if there was a page that allowed researchers with less programming experience to code their features using something like block coding.
2. This website was made for video data analysis, but it can easily be extended to include other types of data.
