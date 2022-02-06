from __future__ import unicode_literals
import requests
import youtube_dl
from uuid import uuid4
from bs4 import BeautifulSoup
from fastapi import APIRouter, status, HTTPException, BackgroundTasks
from isodate import parse_duration
from typing import List
import fastapi
import sqlalchemy.orm as orm
from .auth_api import is_authenticated
from .schemas import users_schemas
from .schemas import video_schemas as schema
from .models import video_model as model

from bigfastapi.db.database import get_db

app = APIRouter(tags=["video streaming and download"])


@app.post("/video/stream")
def stream_videos(video: schema.videoSearch,
                  db: orm.Session = fastapi.Depends(get_db),
                  user: users_schemas.User = fastapi.Depends(is_authenticated)
                  ):
    videos = get_video(url=video.url)
    vid = model.videos(id=uuid4().hex, title=videos["title"], url=videos["track_url"],
                       thumbnail=videos["thumbnail_url"], duration=videos["duration"], added_by=user.id)
    db.add(vid)
    db.commit()
    db.refresh(vid)
    return {"message": "video saved successfully", "video": schema.videos.from_orm(vid)}


@app.get("/video/stream", response_model=List[schema.videos])
def user_stream_list(db: orm.Session = fastapi.Depends(get_db),
                     user: users_schemas.User = fastapi.Depends(is_authenticated)
                     ):
    videos = db.query(model.videos).filter(model.videos.added_by == user.id).all()
    return list(map(schema.videos.from_orm, videos))


@app.get("/video/stream/{video_id}")
def get_stream(video_id: str, db: orm.Session = fastapi.Depends(get_db),
               user: users_schemas.User = fastapi.Depends(is_authenticated)
               ):
    videos = db.query(model.videos).filter(model.videos.id == video_id).first()
    if videos:
        return {"message": "successful", "video": schema.videos.from_orm(videos)}
    return {"message": "not found"}


@app.put("/video/stream/{video_id}/likes")
def like_videos(action: str, video_id: str, db: orm.Session = fastapi.Depends(get_db),
                user: users_schemas.User = fastapi.Depends(is_authenticated)
                ):
    if action not in ["like", "unlike"]:
        return {"status": False, "message": {f"{action} not supported. Consider using 'like' or 'unlike'."}}
    video = db.query(model.videos).filter(model.videos.id == video_id).first()
    if not video:
        return {"message": "video not found"}
    if action == "like":
        video.like()
    elif action == "unlike":
        video.unlike(),

    db.commit()
    db.refresh(video)
    return {"status": True, "data": video}


@app.delete("/video/stream/{video_id}")
def delete_video(video_id: str, db: orm.Session = fastapi.Depends(get_db),
                 user: users_schemas.User = fastapi.Depends(is_authenticated)
                 ):
    video = model.video_picker(user=user, id=video_id, db=db)
    if video:
        db.delete(video)
        db.commit()
        return video
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="video never existed")


@app.post("/video/download")
def download_videos(video_id: str, background_tasks: BackgroundTasks,
                    user: users_schemas.User = fastapi.Depends(is_authenticated),
                    db: orm.Session = fastapi.Depends(get_db)):
    video = db.query(model.videos).filter(model.videos.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="video doesn't exist")
    background_tasks.add_task(download, url=video.url)
    return {"message": "downloading in background............."}


# **************************************video services****************************************#


def get_video(url):
    res = requests.get(url)
    content = res.content
    soup = BeautifulSoup(content, "html.parser")

    return {
        "title": soup.select_one('meta[itemprop="name"][content]')["content"],
        "track_url": soup.select_one('link[itemprop="url"]')["href"],
        "thumbnail_url": soup.select_one('link[itemprop="thumbnailUrl"]')["href"],
        "duration": str(
            parse_duration(
                soup.select_one('meta[itemprop="duration"][content]')["content"]
            )
        ),
    }


def download(url):
    ydl_opts = {'outtmpl': 'C:/Users/D E L E/CODE/bigfastapi/download/%(title)s.%(ext)s'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        load = ydl.download([url])
        return {"message": "downloaded successfully", "video": load}
