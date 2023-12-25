from fastapi import FastAPI, Request

import settings
from feature_extraction import video_processing as vp

#--------------------FASTAPI SETUP--------------------
extraction_app=FastAPI()

#--------------------APP SETUP--------------------
@extraction_app.post("/extraction_info")
async def handle_extract_request(request: Request):
    data = await request.json()
    video_indices = data["video_indices"]
    selected_feature_flags = data["selected_features"]
    selected_features = [i for i in range(len(selected_feature_flags)) if selected_feature_flags[i]]
    selected_significant_moments_flags = data["selected_significant_moments"]
    selected_significant_moments = [i for i in range(len(selected_significant_moments_flags)) if selected_significant_moments_flags[i]]

    await vp.process_video(video_indices, selected_features, selected_significant_moments)
    return {"message":"message"}

@extraction_app.post("/extraction_progress")
async def handle_update_time(request: Request):
    global est_time, processing_progress
    _ = await request.json()
    return {"processing_progress": vp.processing_progress, "est_time": vp.est_time, "current_video": vp.current_video_ind}

@extraction_app.post("/update_lists")
async def handle_update_list(request: Request):
    _ = await request.json()
    settings.update_lists()
    return {"csv_exists_list": settings.csv_exists, "number_features": settings.num_features}

@extraction_app.post("/stop_processing")
async def handle_stop_processing(request: Request):
    _ = await request.json()
    settings.end_processing = True
    return {"message":"message"}
