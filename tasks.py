import requests
from celery import Celery
from celery.utils.log import get_task_logger

app = Celery("tasks", broker="pyamqp://guest@localhost//")
logger = get_task_logger(__name__)


@app.task
def publish_instagram_media(file_url, instagram_user_id,
                            facebook_access_token):
    logger.info("Creating Instagram media with facebook API.")
    create_media = requests.post(
        f"https://graph.facebook.com/{instagram_user_id}/media",
        params={
            "image_url": file_url,
            "access_token": facebook_access_token
        })
    container_id = create_media.json()["id"]
    logger.info(
        f"Publishing Instagram container {container_id} with facebook API.")
    publish_media = requests.post(
        f"https://graph.facebook.com/{instagram_user_id}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": facebook_access_token
        })

    logger.info(
        f"Instagram container published successfully with HTTP status {publish_media.status_code}."
    )
    logger.debug(publish_media.content)
