from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from feature_visualization import frame_generation
import settings

#--------------------FASTAPI SETUP--------------------
# Initializing the app that handles all the video analysis logic.
video_app = FastAPI()


#--------------------APP SETUP--------------------
# Setting the URL where we stream the video frames to.
@video_app.get("/data")
def video():
    return StreamingResponse(frame_generation.generate_frame(), media_type="multipart/x-mixed-replace;boundary=frame")


# Setting the URL that receives the pause flag; this is used to tell the generation function whether to temporarily halt
# frame generation or not.
@video_app.post("/video_info/pause_info")
async def handle_pause(request: Request):
    data = await request.json()
    settings.video_paused = data["video_paused"]
    return {"message": "message"}


# This URL serves 2 purposes; the first is to receive information regarding whether a user skipped to a certain frame
# and if so, which frame it is. This information is used to tell the frame generation function to skip to said frame.
# The second purpose is to tell the client what the current frame is and whether the video is over. This is necessary
# due to how the progress bar on the client side is implemented.
@video_app.post("/video_info/frame_info")
async def handle_change_frame(request: Request):
    data = await request.json()
    if "set_current_frame" in data:
        settings.skip_frame = data["set_current_frame"]-1
        settings.video_skip = True
        print(f"Setting to {settings.current_frame}")
    return {"current_frame": settings.current_frame, "video_ended": settings.video_ended}


# Setting the URL that receives the overlay flags; these determine which overlays have to be added to the generated
# frame before it's encoded and sent to the client.
@video_app.post("/video_info/overlay_info")
async def handle_overlay(request: Request):
    data = await request.json()
    settings.overlay_flags = data["overlay_flags"]
    return {"message": "message"}


# Setting the URL that receives the replay flag; this tells the frame generation function to reset all the flags and
# the current frame of the current video, allowing the video to be replayed without issue.
@video_app.post("/video_info/replay_info")
async def handle_pause(request: Request):
    data = await request.json()
    settings.video_replay = True
    return {"message": "message"}


# Setting the URL that receives a request to change the video. No other flag is needed to reset the video flags like the
# replay requests since the client side implementation refreshes the page whenever the video is changed (which
# automatically resets all the flags).
@video_app.post("/video_info/change_video")
async def handle_change_video(request: Request):
    data = await request.json()
    settings.current_video_ind = data["index"]
    return {"message": "message"}
