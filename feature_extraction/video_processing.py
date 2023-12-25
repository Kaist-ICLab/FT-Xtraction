import time
import datetime
import os
import csv
import asyncio

import cv2 as cv

import settings
from feature_extraction.feature_extraction import InfoTable

current_video_ind = 0
processing_progress=0
start_time=0
est_time="0:00:00"

async def process_video(video_indices, selected_features, selected_significant_moments):
    global est_time, processing_progress, current_video_ind

    super_feature_inds = []
    for i in selected_features:
        if settings.features[i]["super_sub_mapping"] not in super_feature_inds:
            super_feature_inds.append(settings.features[i]["super_sub_mapping"])

    for i in range(len(video_indices)):
        if video_indices[i]:
            info_table_i = InfoTable(settings.img_lists[i])
            current_video_ind = i
            processing_progress=0
            est_time="0:00:00"
            start_time=time.time()

            current_video = settings.video_list[i]
            current_csv = os.path.join(settings.csv_data_dir, f"{'.'.join(settings.video_names[i].split('.')[:-1])}.csv")
            current_sig_csv = os.path.join(settings.csv_data_dir,
                                       f"{'.'.join(settings.video_names[i].split('.')[:-1])}_sig.csv")

            cur_frame=0
            cap = cv.VideoCapture(current_video)

            tot_frames=int(cap.get(cv.CAP_PROP_FRAME_COUNT))

            header=[settings.features[j]["feature_name"] for j in selected_features]
            header_sig_moment=[settings.significant_moment_names[j] for j in selected_significant_moments]

            with open(current_csv, 'w', newline='') as csv_file, open(current_sig_csv, 'w', newline='') as sig_csv_file:
                csv_writer = csv.writer(csv_file, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer_sig = csv.writer(sig_csv_file, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow(header)
                csv_writer_sig.writerow(header_sig_moment)

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    img = frame.copy()
                    frame_num = cur_frame % settings.n_frames

                    info_table_i.extract_data(img, frame_num, super_feature_inds)

                    cur_frame += 1

                    if (cur_frame % settings.n_frames) == 0:
                        info = info_table_i.calculate_features(selected_features)
                        info_sig = info_table_i.calculate_sigm(selected_significant_moments, cur_frame)
                        csv_writer.writerow(info)
                        csv_writer_sig.writerow(info_sig)
                        info_table_i.reset()

                    progress_percent=cur_frame/tot_frames
                    elapsed_time = time.time()-start_time
                    estimated_time = elapsed_time/progress_percent - elapsed_time
                    
                    est_time = str(datetime.timedelta(seconds=int(estimated_time)))
                    processing_progress = f"{progress_percent*100:.2f}%"

                    if settings.end_processing:
                        break
                    
                    await asyncio.sleep(0.1)
                
            if settings.end_processing:
                settings.end_processing=False
                break

    return None
