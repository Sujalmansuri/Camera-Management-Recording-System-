from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from database import engine, Base, SessionLocal
import models
from auth import hash_password, verify_password

from utils import webcam_frames
from recording import start_recording, stop_recording

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)


# -------------------- DB Dependency --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Create Default Admin --------------------
@app.on_event("startup")
def create_admin():
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.username == "admin").first()

    if not user:
        admin = models.User(
            username="admin",
            password=hash_password("admin"),
            role="admin"
        )
        db.add(admin)
        db.commit()

    db.close()


# -------------------- Login Page --------------------
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# -------------------- Login Logic --------------------
@app.post("/login")
def login(request: Request,
          username: str = Form(...),
          password: str = Form(...),
          db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid Credentials"}
        )

    return RedirectResponse(url=f"/{user.role}", status_code=303)


# -------------------- Admin Dashboard --------------------
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    cameras = db.query(models.Camera).all()
    recordings = db.query(models.Recording).all()

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "cameras": cameras, "recordings": recordings}
    )


# -------------------- User Dashboard --------------------
@app.get("/user", response_class=HTMLResponse)
def user_dashboard(request: Request, db: Session = Depends(get_db)):
    cameras = db.query(models.Camera).all()

    return templates.TemplateResponse(
        "user.html",
        {"request": request, "cameras": cameras}
    )


# -------------------- Add Webcam Camera --------------------
@app.post("/add_camera")
def add_camera(name: str = Form(...),
               location: str = Form(...),
               db: Session = Depends(get_db)):

    cam = models.Camera(
        name=name,
        rtsp_url="webcam",
        location=location
    )

    db.add(cam)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)


# -------------------- Webcam Stream --------------------
@app.get("/stream/{cam_id}")
def stream(cam_id: int):
    return StreamingResponse(
        webcam_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# -------------------- Start Recording --------------------
@app.get("/start_record/{cam_id}")
def start_record(cam_id: int):
    start_recording()
    return RedirectResponse(url="/user", status_code=303)


# -------------------- Stop Recording + Save to DB --------------------
@app.get("/stop_record/{cam_id}")
def stop_record(cam_id: int, db: Session = Depends(get_db)):

    filename = stop_recording()

    if filename:
        rec = models.Recording(camera_id=cam_id, filename=filename)
        db.add(rec)
        db.commit()

    return RedirectResponse(url="/user", status_code=303)


# -------------------- Play Recording --------------------
@app.get("/play/{rec_id}")
def play_recording(rec_id: int, db: Session = Depends(get_db)):

    rec = db.query(models.Recording).filter(models.Recording.id == rec_id).first()

    if not rec:
        return {"error": "Recording not found"}

    file_path = os.path.join(RECORDINGS_DIR, rec.filename)

    if not os.path.exists(file_path):
        return {"error": f"File not found: {rec.filename}"}

    return FileResponse(file_path, media_type="video/mp4")


# -------------------- Download Recording --------------------
@app.get("/download/{rec_id}")
def download_recording(rec_id: int, db: Session = Depends(get_db)):

    rec = db.query(models.Recording).filter(models.Recording.id == rec_id).first()

    file_path = os.path.join(RECORDINGS_DIR, rec.filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path, filename=rec.filename)


# -------------------- Delete Recording --------------------
@app.get("/delete/{rec_id}")
def delete_recording(rec_id: int, db: Session = Depends(get_db)):

    rec = db.query(models.Recording).filter(models.Recording.id == rec_id).first()

    file_path = os.path.join(RECORDINGS_DIR, rec.filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(rec)
    db.commit()

    return RedirectResponse(url="/admin", status_code=303)