#!/usr/bin/env python3
"""
Script to initialize MinIO bucket for model artifacts
"""
import os
from minio import Minio
from minio.error import S3Error

def init_minio():
    # MinIO client configuration
    client = Minio(
        "localhost:9000",
        access_key=os.getenv("AWS_ACCESS_KEY_ID", "minio"),
        secret_key=os.getenv("AWS_SECRET_ACCESS_KEY", "minio123"),
        secure=False
    )

    bucket_name = os.getenv("S3_BUCKET", "quarlets-models")

    try:
        # Check if bucket exists
        if not client.bucket_exists(bucket_name):
            # Create bucket
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        else:
            print(f"Bucket '{bucket_name}' already exists")

        # Create MLflow bucket
        mlflow_bucket = "mlflow"
        if not client.bucket_exists(mlflow_bucket):
            client.make_bucket(mlflow_bucket)
            print(f"Bucket '{mlflow_bucket}' created successfully")
        else:
            print(f"Bucket '{mlflow_bucket}' already exists")

    except S3Error as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    init_minio()