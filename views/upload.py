import os

from flask import Blueprint, render_template, request, url_for, current_app, abort
from flask_security import current_user, auth_required
from werkzeug.utils import redirect

from database import db_session
from models import InstagramImage
from b2_upload import upload_to_b2

upload_pages = Blueprint("upload_pages", __name__, url_prefix="/upload")


@upload_pages.route("/", methods=["GET", "POST"])
@auth_required()
def upload():
    if request.method == "POST":
        uploaded_file = request.files['image']
        filename = uploaded_file.filename
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(uploaded_file.filename)
            file_url = upload_to_b2(uploaded_file.filename)
            os.remove(filename)
            db_session.add(
                InstagramImage(user_id=current_user.id, image_url=file_url))
            db_session.commit()

        return redirect(url_for(".upload"))
    return render_template("upload.html")
