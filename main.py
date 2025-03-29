from fastapi import FastAPI, Query, HTTPException, Request
from pytubefix import YouTube
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
<<<<<<< HEAD
def Home()
    return{"message":"API Running"}
=======
def Home():
    return{"message":"API running"}
>>>>>>> 200c1a4 (Final Push)

@app.get("/video_info")
@limiter.limit("5/second")  # Limit requests to 5 per minute
async def get_video_info(request: Request, url: str):
    """Fetch video details, available resolutions, and audio options."""
    try:
        yt = YouTube(url)

        unique_streams = {}
        unique_audio_streams = {}

        # Add progressive streams (video + audio)
        for stream in yt.streams.filter(progressive=True, file_extension="mp4"):
            if stream.resolution not in unique_streams:
                file_type = stream.mime_type.split("/")[-1]
                file_size = f"{stream.filesize_approx / (1024 * 1024):.2f} MB" if stream.filesize_approx else "Unknown"
                unique_streams[stream.resolution] = {
                    "resolution": stream.resolution,
                    "itag": stream.itag,
                    "type": "audio+video",
                    "file_size": file_size,
                    "file_type": file_type,
                    "download_url": stream.url 
                }

        # Add adaptive video-only streams
        for stream in yt.streams.filter(only_video=True, file_extension="mp4"):
            if stream.resolution not in unique_streams:
                file_type = stream.mime_type.split("/")[-1]  # Corrected file type assignment
                estimated_size = f"{stream.filesize_approx / (1024 * 1024):.2f} MB" if stream.filesize_approx else "Unknown"
                unique_streams[stream.resolution] = {
                    "resolution": stream.resolution,
                    "itag": stream.itag,
                    "type": "video-only",
                    "file_size": estimated_size,
                    "file_type": file_type,
                    "download_url": stream.url 
                }

        # Add unique audio streams (Convert MP4 Audio to MP3)
        for stream in yt.streams.filter(only_audio=True):
            file_type = stream.mime_type.split("/")[-1]

            # Convert MP4 Audio to MP3 in the response
            if file_type == "mp4":
                file_type = "mp3"

            file_size = f"{stream.filesize_approx / (1024 * 1024):.2f} MB" if stream.filesize_approx else "Unknown"
            unique_audio_streams[stream.abr] = {
                "abr": stream.abr,
                "itag": stream.itag,
                "type": "audio",
                "file_size": file_size,
                "file_type": file_type,
                "download_url": stream.url 
            }
            logging.info(f"Fetched video info successfully for: {url}")


        return {
            "title": yt.title,
            "thumbnail": yt.thumbnail_url,
            "video_streams": list(unique_streams.values()),
            "audio_streams": list(unique_audio_streams.values()),
        }

    except Exception as e:
        logging.error(f"Error fetching video info: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to fetch video details. Please check the URL.")


