from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from feature_visualization import frame_generation
import settings

#--------------------FASTAPI SETUP--------------------
video_app=FastAPI()

#--------------------APP SETUP--------------------
@video_app.get("/data")
def video():
    return StreamingResponse(frame_generation.generate_frame(), media_type="multipart/x-mixed-replace;boundary=frame")
#to change video, simply erase the capture and change video index; add sanitization step

@video_app.post("/video_info/pause_info")
async def handle_pause(request: Request):
    data = await request.json()
    settings.video_paused = data["video_paused"]
    return {"message":"message"}

@video_app.post("/video_info/frame_info")
async def handle_change_frame(request: Request):
    data = await request.json()
    if "set_current_frame" in data:
        settings.skip_frame = data["set_current_frame"]-1
        settings.video_skip = True
        print(f"Setting to {settings.current_frame}")
    return {"current_frame": settings.current_frame, "video_ended": settings.video_ended}

@video_app.post("/video_info/overlay_info")
async def handle_change_frame(request: Request):
    data = await request.json()
    settings.overlay_flags = data["overlay_flags"]
    return {"message":"message"}

@video_app.post("/video_info/replay_info")
async def handle_pause(request: Request):
    data = await request.json()
    settings.video_replay = True
    return {"message":"message"}

@video_app.post("/video_info/change_video")
async def handle_change_frame(request: Request):
    data = await request.json()
    settings.current_video_ind = data["index"]
    return {"message":"message"}
