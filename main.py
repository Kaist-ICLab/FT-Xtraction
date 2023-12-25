import os
import signal

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import settings
from feature_visualization import video_overlays as vo
from feature_extraction import feature_extraction_app
from feature_visualization import video_analysis_app
#--------------------FASTAPI SETUP--------------------
app=FastAPI()
templates = Jinja2Templates(directory="./fastapi_resources/templates")
app.mount("/static", StaticFiles(directory="./fastapi_resources/static"), name="static")

#--------------------MAIN APP SETUP--------------------
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("entry_page.html", {"request": request})

@app.post("/shutdown")
async def shutdown_server(request: Request):
    _ = await request.json()
    print("Shutdown signal sent")
    settings.server_running = False
    os.kill(os.getpid(), signal.SIGTERM)
    return {"message":"message"}

def kill_server(*args):
    settings.server_running = False
    os.kill(os.getpid(), signal.SIGTERM)

@app.on_event("startup")
def handle_kill_server():
    signal.signal(signal.SIGINT, kill_server)

#--------------------TEMPLATING APPS--------------------
@feature_extraction_app.extraction_app.get("/")
def exctraction_root(request: Request):
    settings.update_lists()
    return templates.TemplateResponse("feature_extraction.html", {"request": request, "video_list": settings.video_names, "csv_exists_list": settings.csv_exists, "number_features": settings.num_features, "feature_list": [feature_i["feature_name"] for feature_i in settings.features], "signficant_moments_list": settings.significant_moment_names})

feature_extraction_app.extraction_app.mount("/static", StaticFiles(directory="./fastapi_resources/static"), name="static")

@video_analysis_app.video_app.get("/")
def video_root(request: Request):
    #anything here is called whenever page is loaded
    settings.load_video()
    return templates.TemplateResponse("video_analysis.html", {"request": request, "total_frame_count": settings.video_max_frames, "chart_frame_width": settings.n_frames, "frames": settings.frames, "feature_names":settings.feature_names, "sub_feature_names": settings.sub_feature_names, "feature_data": settings.feature_data, "video_names": settings.video_names, "overlay_names": vo.overlay_names, "graph_colors": settings.feature_graph_colors, "significant_moment_names": settings.sig_names, "significant_moment_data": settings.sig_data, "significant_moment_colors":settings.sig_colors, "feature_offsets":settings.feature_offsets, "fps":settings.fps, "current_video_ind":settings.current_video_ind})

video_analysis_app.video_app.mount("/static", StaticFiles(directory="./fastapi_resources/static"), name="static")

#--------------------MOUNTING VIDEO APP--------------------
app.mount("/feature_extraction", feature_extraction_app.extraction_app)
app.mount("/video_analysis", video_analysis_app.video_app)

#--------------------RUNNING--------------------
if __name__ == "__main__":
    uvicorn.run(app)