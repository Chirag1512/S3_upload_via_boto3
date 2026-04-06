# Docker Setup & Run Guide

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running

---

## 1. Build the Image

```bash
docker build -t cloud-uploader .
```

---

## 2. Run the Container

### Option A — Using `.env` file (recommended)

```bash
docker run -p 5000:5000 --env-file .env cloud-uploader
```

### Option B — Passing variables manually

```bash
docker run -p 5000:5000 \
  -e DATNASS_ENDPOINT=https://s3.gdx.datnass.com/ \
  -e DATNASS_ACCESS_KEY=your-access-key \
  -e DATNASS_SECRET_KEY=your-secret-key \
  -e DATNASS_BUCKET=my-data \
  cloud-uploader
```

---

## 3. Open the App

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 4. Run in Background (detached mode)

```bash
docker run -d -p 5000:5000 --env-file .env --name cloud-uploader cloud-uploader
```

### View logs

```bash
docker logs -f cloud-uploader
```

### Stop the container

```bash
docker stop cloud-uploader
```

### Remove the container

```bash
docker rm cloud-uploader
```

---

## 5. Rebuild After Code Changes

```bash
docker build -t cloud-uploader . && docker run -p 5000:5000 --env-file .env cloud-uploader
```

---

## Environment Variables

| Variable           | Description                        | Example                          |
|--------------------|------------------------------------|----------------------------------|
| `DATNASS_ENDPOINT` | S3-compatible API endpoint URL     | `https://s3.gdx.datnass.com/`   |
| `DATNASS_ACCESS_KEY` | S3 access key                   | `--------------------------...`      |
| `DATNASS_SECRET_KEY` | S3 secret key                   | `-----------------------...`           |
| `DATNASS_BUCKET`   | Bucket name (auto-created if missing) | `my-data`                    |

> **Note:** Do not add inline comments in the `.env` file. Docker reads them as part of the value.
