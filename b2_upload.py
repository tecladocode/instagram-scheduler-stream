import os
from dotenv import load_dotenv
from b2sdk.v2 import InMemoryAccountInfo, B2Api

load_dotenv()

info = InMemoryAccountInfo()
b2_api = B2Api(info)

application_key_id = os.environ.get("B2_APP_KEY_ID")
application_key = os.environ.get("B2_APP_KEY")
b2_api.authorize_account("production", application_key_id, application_key)

ig_scheduler_bucket = b2_api.get_bucket_by_name("instagram-scheduler")


def upload_to_b2(local_file_path):
    b2_file_name = os.path.basename(local_file_path)
    file_info = {'how': 'good-file'}

    uploaded_file = ig_scheduler_bucket.upload_local_file(
        local_file=local_file_path,
        file_name=b2_file_name,
        file_infos=file_info,
    )

    return b2_api.get_download_url_for_fileid(uploaded_file.id_)
