import os
import cv2
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from isodate import parse_duration
from pytube import YouTube
import subprocess
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable

# Constants
YOUTUBE_API_KEY = '...'
OUTPUT_DIR = '/home/vboxuser/mlop/bai1/output'
MAX_RESULTS = 20

# Function to crawl YouTube trends
def crawl_youtube_trends(**kwargs):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(part="snippet,contentDetails", chart="mostPopular", maxResults=MAX_RESULTS, regionCode="US")
    response = request.execute()

    shorts_urls = []
    for item in response.get('items', []):
        video_id = item['id']
        duration = item['contentDetails']['duration']
        duration_seconds = parse_duration(duration).total_seconds()

        if duration_seconds <= 300:  # Filter for YouTube Shorts
            shorts_urls.append(f'https://www.youtube.com/watch?v={video_id}')

    # Push to XCom
    kwargs['ti'].xcom_push(key='shorts_urls', value=shorts_urls)

def download_videos(**kwargs):
    # Retrieve video URLs from XCom
    ti = kwargs['ti']
    video_urls = ti.xcom_pull(task_ids='crawl_youtube_trends', key='shorts_urls')

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, video_url in enumerate(video_urls):
        video_path = os.path.join(OUTPUT_DIR, f'video{i}.mp4')
        try:
            # Use yt-dlp to download videos
            command = [
                "yt-dlp",
                video_url,
                "-f", "best[ext=mp4]",
                "-o", video_path
            ]
            subprocess.run(command, check=True)
            print(f"Downloaded: {video_path}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {video_url}: {e}")

def detect_faces(**kwargs):
    # Retrieve video URLs from XCom
    ti = kwargs['ti']
    video_urls = ti.xcom_pull(task_ids='crawl_youtube_trends', key='shorts_urls')

    if not video_urls:
        raise ValueError("No video URLs retrieved. Check the crawl_youtube_trends task.")
    
    # Download videos first
    download_videos(**kwargs)

    for i, video_url in enumerate(video_urls):
        video_path = os.path.join(OUTPUT_DIR, f'video{i}.mp4')
        
        if not os.path.exists(video_path):
            print(f"Video file not found: {video_path}. Skipping.")
            continue

        cap = cv2.VideoCapture(video_path)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        fps = 5
        frame_interval = int(cap.get(cv2.CAP_PROP_FPS) / fps)
        frame_count = 0
        save_path = os.path.join(OUTPUT_DIR, f'frames_video{i}')
        os.makedirs(save_path, exist_ok=True)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                if len(faces) > 0:
                    frame_filename = os.path.join(save_path, f"frame_{frame_count}.jpg")
                    cv2.imwrite(frame_filename, frame)
            
            frame_count += 1

        cap.release()
        print(f"Processed video: {video_path}")

# DAG definition
with DAG(
    'youtube_face_detection_dag',
    default_args={
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='YouTube Video Face Detection',
    schedule_interval='*/5 * * * *',  # Chạy mỗi 5 phút
    start_date=datetime(2025, 1, 15),
    catchup=False,
) as dag:

    # Task to crawl YouTube trends
    crawl_task = PythonOperator(
        task_id='crawl_youtube_trends',
        python_callable=crawl_youtube_trends,
        provide_context=True,  # Passes Airflow context
    )

    # Task to detect faces
    detect_faces_task = PythonOperator(
        task_id='detect_faces',
        python_callable=detect_faces,
        provide_context=True,  # Passes Airflow context
    )

    # Task dependencies
    crawl_task >> detect_faces_task
