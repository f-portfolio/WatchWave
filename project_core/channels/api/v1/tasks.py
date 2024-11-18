from celery import shared_task
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ...models import VideoPost

@shared_task
def save_video(video_id, file_path):
    try:
        print(f"Starting video saving for video_id: {video_id}")
        video = VideoPost.objects.get(id=video_id)
        with open(file_path, 'rb') as f:
            file_content = f.read()
        video.video.save(os.path.basename(file_path), ContentFile(file_content))
        video.save()
        print(f"Video {video_id} saved successfully.")
    except VideoPost.DoesNotExist:
        print(f"Video with id {video_id} does not exist.")
    except Exception as e:
        print(f"An error occurred while saving the video: {str(e)}")