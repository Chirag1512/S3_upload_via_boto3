import os
import uuid
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, render_template, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from werkzeug.serving import WSGIRequestHandler

load_dotenv()

app = Flask(__name__)


class QuietProgressRequestHandler(WSGIRequestHandler):
    """Avoid terminal spam from frequent /progress polling requests."""
    def log_request(self, code="-", size="-"):
        if self.path.startswith("/progress/"):
            return
        super().log_request(code, size)

ENDPOINT   = os.getenv("DATNASS_ENDPOINT")
ACCESS_KEY = os.getenv("DATNASS_ACCESS_KEY")
SECRET_KEY = os.getenv("DATNASS_SECRET_KEY")
BUCKET_NAME = os.getenv("DATNASS_BUCKET", "uploads")

# In-memory progress store: { upload_id: { 'loaded': int, 'total': int } }
upload_progress = {}

# boto3 S3 client — works with any S3-compatible service (Datnass)
client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)   


class TrackingStream:
    """Wraps a file stream and tracks bytes read into upload_progress."""
    def __init__(self, stream, upload_id):
        self._stream = stream
        self._upload_id = upload_id

    def read(self, size=-1):
        chunk = self._stream.read(size)
        if chunk:
            upload_progress[self._upload_id]['loaded'] += len(chunk)
        return chunk


def ensure_bucket():
    """Create bucket if it doesn't exist."""
    try:
        client.head_bucket(Bucket=BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' already exists.")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' created.")
        else:
            raise


@app.route("/")
def index():
    return render_template("index.html", bucket=BUCKET_NAME)


@app.route("/progress/<upload_id>")
def get_progress(upload_id):
    """Return real-time upload progress for a given upload_id."""
    prog = upload_progress.get(upload_id)
    if not prog:
        return jsonify({'pct': 0, 'loaded': 0, 'total': 0})
    total = prog['total']
    loaded = prog['loaded']
    pct = round((loaded / total) * 100) if total > 0 else 0
    return jsonify({'pct': min(pct, 99), 'loaded': loaded, 'total': total})


@app.route("/upload", methods=["POST"])
def upload():
    if "files" not in request.files:
        return jsonify({"error": "No files selected"}), 400

    upload_id = request.form.get('upload_id', str(uuid.uuid4()))
    total_size = int(request.form.get('total_size', 0))
    upload_progress[upload_id] = {'loaded': 0, 'total': total_size}

    uploaded = []
    errors = []

    for file in request.files.getlist("files"):
        if file.filename == "":
            continue
        try:
            tracker = TrackingStream(file.stream, upload_id)
            client.upload_fileobj(
                tracker,
                BUCKET_NAME,
                file.filename,
                ExtraArgs={"ContentType": file.content_type or "application/octet-stream"},
            )
            uploaded.append(file.filename)
        except ClientError as e:
            errors.append({"file": file.filename, "error": str(e)})

    # Clean up progress entry
    upload_progress.pop(upload_id, None)
    return jsonify({"uploaded": uploaded, "errors": errors})

@app.route("/files")
def list_files():
    """List all objects in the bucket."""
    try:
        response = client.list_objects_v2(Bucket=BUCKET_NAME)
        files = [
            {
                "name": obj["Key"],
                "size": obj["Size"],
                "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S"),
            }
            for obj in response.get("Contents", [])
        ]
        return jsonify({"files": files})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:file_key>")
def download_file(file_key):
    """Stream a file from object storage through Flask for maximum compatibility."""
    try:
        obj = client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        body = obj["Body"]
        content_type = obj.get("ContentType") or "application/octet-stream"
        filename = os.path.basename(file_key) or "download"

        def generate():
            try:
                for chunk in body.iter_chunks(chunk_size=1024 * 1024):
                    if chunk:
                        yield chunk
            finally:
                body.close()

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        if obj.get("ContentLength") is not None:
            headers["Content-Length"] = str(obj["ContentLength"])

        return Response(
            stream_with_context(generate()),
            mimetype=content_type,
            headers=headers,
        )
    except ClientError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    ensure_bucket()
    app.run(debug=False, host="0.0.0.0", port=5000, request_handler=QuietProgressRequestHandler)
