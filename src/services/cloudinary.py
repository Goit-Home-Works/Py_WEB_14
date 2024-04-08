import hashlib

import cloudinary
import cloudinary.uploader

from config.config import settings


class Cloudinary:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    @staticmethod
    def generate_public_id_by_email(
        email: str, app_name: str = settings.app_name
    ) -> str:
        name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
        return f"APP_{app_name}/{name}"

    @staticmethod
    def upload(file, public_id: str):
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    def generate_url(r, public_id) -> str:
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")  # type: ignore
        )
        return src_url
