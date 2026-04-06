# Cloud File Uploader (Flask + Boto3)

A simple web app to upload, list, and download files from your S3-compatible object storage service using **Flask** and **boto3**.

## Features

- Drag-and-drop or click-to-select multi-file uploads
- Real-time upload progress tracking
- Automatic bucket existence check/creation at startup
- List files in the configured bucket
- Download files from the bucket through Flask
- Docker support

## Tech Stack

- Python
- Flask
- boto3
- python-dotenv
- HTML/CSS/Vanilla JavaScript frontend

## Project Structure

- `app.py` — Flask backend and S3 integration
- `templates/index.html` — UI for upload/list/download
- `requirements.txt` — Python dependencies
- `BUILD_RUN.md` — quick local build/run notes
- `DOCKER.md` — Docker usage guide

## Prerequisites

- Python 3.9+ (recommended)
- Access to your S3-compatible endpoint (MinIO, AWS S3-compatible API, etc.)
- Valid access key and secret key

## Environment Variables

Create a `.env` file in the project root with:

```env
YOUR_ENDPOINT=https://your-s3-endpoint/
YOUR_ACCESS_KEY=your-access-key
YOUR_SECRET_KEY=your-secret-key
YOUR_BUCKET=uploads
```

### Variable Details

- `YOUR_ENDPOINT`: your S3-compatible endpoint URL
- `YOUR_ACCESS_KEY`: your access key
- `YOUR_SECRET_KEY`: your secret key
- `YOUR_BUCKET`: your bucket name (defaults to `uploads` if not set)

## Run Locally

1. Create and activate a virtual environment
2. Install dependencies
3. Start the app

Example (same flow used in this project):

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open: `http://localhost:5000`

## Docker

Build image:

```bash
docker build -t cloud-uploader .
```

Run using `.env` file:

```bash
docker run -p 5000:5000 --env-file .env cloud-uploader
```

Open: `http://localhost:5000`

For detached mode, logs, stop/remove container, and rebuild flow, see `DOCKER.md`.

## API Endpoints

- `GET /` — UI page
- `POST /upload` — Upload one or more files
- `GET /progress/<upload_id>` — Upload progress polling
- `GET /files` — List bucket files
- `GET /download/<file_key>` — Download file by key

## Notes

- The app keeps upload progress in memory (`upload_progress` dict), suitable for single-process/simple deployments.
- On startup, the app checks if the bucket exists and creates it if missing.
- Keep your `.env` out of version control (already covered by `.gitignore`).

## Troubleshooting

- **Connection/auth errors**: verify endpoint, access key, and secret key.
- **Bucket issues**: ensure permissions allow `head_bucket`, `create_bucket`, `list_objects_v2`, `get_object`, and upload operations.
- **Port already in use**: change port mapping or stop existing process using `5000`.

## License

Add your preferred license here (MIT/Apache-2.0/etc.).
