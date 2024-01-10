import cv2 as cv
import time

import settings
import feature_visualization.video_overlays as vo


# This function is used to create and encode the video frames before sending them over to the client side.
# Additionally, all the video overlays are added here.
def generate_frame():
    capture = settings.capture

    # Stop frame generation if the video cannot be loaded.
    if capture is None or not capture.isOpened():
        print("Cannot load video or open camera")
        return None
    
    while True:
        # Used when shutting the servevr down.
        if not settings.server_running:
            return None

        # This check prevents the same frame from unnecessarily being generated.
        if (not settings.video_paused) and (not settings.video_ended):
            # The success variable is a boolean which indicates whether a frame could be read or not. The frame variable
            # is simply the image making up the frame of the video at that point in time.
            success, frame = capture.read()

            # If for some reason the frame can not be read, the video is interrupted.
            if not success:
                print("Breaking video capture")
                capture.release()
                return None

            else:
                # Arbitrary delay to prevent opencv from displaying all the frames at once.
                time.sleep(0.05)

                # Checks if the video has reached its last frame; this is then used to set a flag that lets the server
                # know that the video finished.
                if settings.current_frame >= settings.video_max_frames-1:
                    settings.video_ended = True
                    print('VIDEO ENDED')
                    continue

                # Checks if the user has skipped to a certain point in the video; if so the video is set to that point.
                if settings.video_skip:
                    capture.set(cv.CAP_PROP_POS_FRAMES, settings.skip_frame)
                    settings.video_skip = False

                # Adds all the overlays specified by the user on the client side.
                for i in range(len(settings.overlay_flags)):
                    if settings.overlay_flags[i]:
                        frame = vo.overlay_functions[i](frame)

                # Encodes frame to be sent to the client side
                _, buffer = cv.imencode('.jpg', frame)
                settings.current_frame = capture.get(cv.CAP_PROP_POS_FRAMES)

                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                       bytearray(buffer) + b'\r\n')

        # Setting certain flags when a video replay is requested so that the video can restart safely.
        if settings.video_replay:
            capture.set(cv.CAP_PROP_POS_FRAMES, 0)
            settings.current_frame = 0
            settings.video_replay = False
            settings.video_ended = False
            settings.video_paused = True
