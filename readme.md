# Webcam Surveillance System using FastAPI

A complete webcam-based surveillance and recording system built with **FastAPI**, **OpenCV**, **FFmpeg**, and **SQLite**.

This project provides:

 Live Webcam Streaming  
 Start/Stop Video Recording  
 Admin Dashboard to Manage Recordings  
 Play + Download Recorded Videos  
 Delete Recordings  

---

##  Features

- Admin Login System  
- Webcam Live Feed in Browser  
- Recording stored as MP4 files  
- Play recordings directly from dashboard  
- Download recordings  
- Delete unwanted recordings  

---

##  Technology Stack

- **FastAPI** – Backend Framework  
- **Jinja2 Templates** – HTML Rendering  
- **SQLite + SQLAlchemy** – Database  
- **OpenCV** – Webcam frame capture  
- **FFmpeg** – Video Recording & Encoding  
- **Bootstrap 5** – UI Styling  

---

##  Project Structure
camera_app/
│── main.py
│── models.py
│── database.py
│── auth.py
│── utils.py
│── recording.py
│── camera.db
│── recordings/
│── templates/
│── login.html
│── admin.html
│── user.html


##  Installation Steps

## 1️ Create Virtual Environment


python -m venv venv
venv\Scripts\activate

## 2️ Install Requirements
pip install fastapi uvicorn sqlalchemy jinja2 opencv-python passlib[bcrypt]

## 3️ Install FFmpeg

Download FFmpeg from:

https://www.gyan.dev/ffmpeg/builds/

Add it to Windows PATH.

 Run Project
uvicorn main:app --reload



Default Login
Role	Username	Password
Admin	admin	admin