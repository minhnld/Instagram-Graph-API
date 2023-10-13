from dataclasses import dataclass


@dataclass
class UploadS3FileResponse:
    s3_bucket_path_key: str
    full_url: str


@dataclass
class S3FilesInFolderResponse:
    s3_bucket_path_key: str
    full_url: str
    last_modified: str
