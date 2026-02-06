import subprocess
import datetime
import os

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

recording_process = None
current_filename = None


# -------------------- Start Recording --------------------
def start_recording():
    global recording_process, current_filename

    # Prevent double start
    if recording_process is not None:
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_filename = f"webcam_record_{timestamp}.mp4"
    filepath = os.path.join(RECORDINGS_DIR, current_filename)

    command = [
        "ffmpeg",
        "-y",

        "-f", "dshow",
        "-rtbufsize", "100M",
        "-i", "video=Integrated Camera",

        "-vcodec", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",

        filepath
    ]

    recording_process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# -------------------- Stop Recording --------------------
def stop_recording():
    global recording_process, current_filename

    if recording_process is None:
        return None

    try:
        # ✅ Only stop if still running
        if recording_process.poll() is None:

            # Send graceful quit
            recording_process.stdin.write(b"q\n")
            recording_process.stdin.flush()

            recording_process.wait(timeout=5)

    except Exception as e:
        print("Stop Recording Error:", e)

    finally:
        recording_process = None

    return current_filename