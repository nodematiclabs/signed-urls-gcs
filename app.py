from flask import Flask, jsonify
from google.cloud import storage

import datetime
import google.auth

BUCKET_NAME = 'signed-urls-demo'
BLOB_NAME = 'secret-image.png'

app = Flask(__name__)

storage_client = storage.Client()

@app.route('/get-signed-url', methods=['GET'])
def get_signed_url():
    try:
        credentials, _ = google.auth.default()
        auth_request = google.auth.transport.requests.Request()
        credentials.refresh(auth_request)

        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(BLOB_NAME)

        expiration = datetime.timedelta(minutes=5)
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
            credentials = google.auth.compute_engine.IDTokenCredentials(
                auth_request,
                "",
                service_account_email=credentials.service_account_email
            )
        )

        return jsonify({
            "signed_url": url,
            "expires_in": str(expiration)
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)