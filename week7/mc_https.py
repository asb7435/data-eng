# mc_https.py — 일부러 secure=True 로 붙어 봅니다
from minio import Minio

bad = Minio("localhost:9000", access_key="minioadmin",
            secret_key="minioadmin", secure=True)
try:
    bad.bucket_exists("raw-docs")
except Exception as e:
    print(type(e).__name__)
    print(str(e)[:200])
