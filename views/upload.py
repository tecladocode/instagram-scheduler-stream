import os
import datetime

from flask import Blueprint, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect
from loguru import logger

from tasks import publish_instagram_media
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
        publish_date = request.form["publish_date"]
        logger.debug(f"Photo will be published on {publish_date}.")
        publish_datetime = datetime.datetime.strptime(publish_date,
                                                      "%Y-%m-%dT%H:%M")
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
                InstagramImage(user_id=current_user.id,
                               image_url=file_url,
                               publish_date=publish_datetime))
            db_session.commit()

            publish_instagram_media.apply_async(
                (file_url, current_user.instagram_user_id,
                 current_user.facebook_access_token),
                eta=publish_datetime)

        return redirect(url_for(".upload"))
    return render_template("upload.html")
