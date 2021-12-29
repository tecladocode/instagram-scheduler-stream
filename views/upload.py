import os

from flask import Blueprint, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
import requests
from loguru import logger

from database import db_session
from models import InstagramImage
from b2_upload import upload_to_b2

upload_pages = Blueprint("upload_pages", __name__, url_prefix="/upload")


@upload_pages.route("/", methods=["GET", "POST"])
@auth_required()
def upload():
    if request.method == "POST":
        logger.debug("Handling POST of upload endpoint")
        uploaded_file = request.files['image']
        filename = uploaded_file.filename
        logger.debug(f"Uploaded {filename}")
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(uploaded_file.filename)
            logger.debug("File saved to local disk.")
            file_url = upload_to_b2(uploaded_file.filename)
            logger.debug(f"File saved to B2 Backblaze at {file_url}")
            os.remove(filename)
            logger.debug("File removed from local disk.")

            db_session.add(
                InstagramImage(user_id=current_user.id, image_url=file_url))
            db_session.commit()

            logger.debug("Creating Instagram media with facebook API.")
            create_media = requests.post(
                f"https://graph.facebook.com/{current_user.instagram_user_id}/media",
                params={
                    "image_url": file_url,
                    "access_token": current_user.facebook_access_token
                })
            container_id = create_media.json()["id"]
            logger.debug(
                f"Publishing Instagram container {container_id} with facebook API."
            )
            publish_media = requests.post(
                f"https://graph.facebook.com/{current_user.instagram_user_id}/media_publish",
                params={
                    "creation_id": container_id,
                    "access_token": current_user.facebook_access_token
                })

            logger.debug(
                "Instagram container published successfully with HTTP status {publish_media.status_code}."
            )
            logger.debug(publish_media.content)

        return redirect(url_for(".upload"))
    return render_template("upload.html")
