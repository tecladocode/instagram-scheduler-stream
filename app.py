import os

from flask import Flask, render_template_string
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role
from views.upload import upload_pages
from views.facebook_auth import facebook_auth

# Create app
app = Flask(__name__)

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get(
    "SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpeg']

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)

app.register_blueprint(upload_pages)
app.register_blueprint(facebook_auth)


# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    if not user_datastore.find_user(email="test@me.com"):
        user_datastore.create_user(email="test@me.com",
                                   password=hash_password("password"))
    db_session.commit()


# Views
@app.route("/")
@auth_required()
def home():
    return render_template_string('Hello {{email}} !',
                                  email=current_user.email)
