import hashlib

import cloudinary
import cloudinary.uploader

from config.config import settings


class Cloudinary:
    """
    Class for interacting with the Cloudinary service.

    Attributes:
    - cloud_name (str): The Cloudinary cloud name.
    - api_key (str): The Cloudinary API key.
    - api_secret (str): The Cloudinary API secret.

    Methods:
    - generate_public_id_by_email(email: str, app_name: str = settings.app_name) -> str:
        Generates a unique public ID for a file based on the user's email.

    - upload(file, public_id: str):
        Uploads a file to Cloudinary with the specified public ID.

    - generate_url(r, public_id) -> str:
        Generates a URL for accessing the uploaded file on Cloudinary.
    """

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
        """
        Generates a unique public ID for a file based on the user's email.

        Parameters:
        - email (str): The user's email.
        - app_name (str, optional): The name of the application. Defaults to settings.app_name.

        Returns:
        - str: The generated public ID.
        """

        name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
        return f"APP_{app_name}/{name}"

    @staticmethod
    def upload(file, public_id: str):
        """
        Uploads a file to Cloudinary with the specified public ID.

        Parameters:
        - file: The file to upload.
        - public_id (str): The public ID for the uploaded file.

        Returns:
        - dict: The response from Cloudinary after the upload.
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    def generate_url(r, public_id) -> str:
        """
        Generates a URL for accessing the uploaded file on Cloudinary.

        Parameters:
        - r: The response from the upload operation.
        - public_id: The public ID of the uploaded file.

        Returns:
        - str: The URL for accessing the uploaded file.
        """

        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")  # type: ignore
        )
        return src_url
