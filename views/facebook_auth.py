import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import current_user, auth_required
import requests
from loguru import logger

from database import db_session

facebook_auth = Blueprint("facebook_auth",
                          __name__,
                          url_prefix="/login/facebook")

STATE = "145436561"
FACEBOOK_APP_ID = os.environ.get("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.environ.get("FACEBOOK_APP_SECRET")


@facebook_auth.route("/")
@auth_required()
def facebook_login():
    redirect_uri = url_for(".facebook_redirect",
                           _external=True).replace("http", "https")
    print(redirect_uri)
    return redirect(
        f"https://www.facebook.com/v12.0/dialog/oauth?client_id={FACEBOOK_APP_ID}&redirect_uri={redirect_uri}&state={STATE}&scope=instagram_basic,pages_show_list,instagram_content_publish"
    )


@facebook_auth.route("/redirect")
@auth_required()
def facebook_redirect():
    redirect_uri = url_for(".facebook_redirect",
                           _external=True).replace("http", "https")
    code = request.args["code"]

    logger.debug(f"Got code from facebook login: {code[:10]}")
    logger.info("Getting access token using code.")

    response = requests.get(
        "https://graph.facebook.com/v12.0/oauth/access_token",
        params={
            "client_id": FACEBOOK_APP_ID,
            "redirect_uri": redirect_uri,
            "client_secret": FACEBOOK_APP_SECRET,
            "code": request.args["code"]
        })
    access_token = response.json()["access_token"]

    logger.debug(f"Got access token from facebook: {access_token[:10]}")
    logger.info("Getting facebook page ID.")

    my_accounts = requests.get("https://graph.facebook.com/v12.0/me/accounts",
                               params={"access_token": access_token})
    page_id = my_accounts.json()["data"][0]["id"]

    logger.debug(f"Got facebook page ID: {page_id}")
    logger.info("Getting associated Instagram user ID.")
    instagram_data = requests.get(
        f"https://graph.facebook.com/v12.0/{page_id}",
        params={
            "access_token": access_token,
            "fields": "instagram_business_account"
        })
    instagram_user_id = instagram_data.json(
    )["instagram_business_account"]["id"]

    logger.debug(f"Got Instagram user ID: {instagram_user_id}.")
    logger.info("Saving access token and Instagram user ID to current user.")

    current_user.facebook_access_token = access_token
    current_user.instagram_user_id = instagram_user_id
    db_session.add(current_user)
    db_session.commit()
    return "Success!"
