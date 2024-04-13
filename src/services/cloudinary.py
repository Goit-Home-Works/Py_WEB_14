import hashlib

import cloudinary
import cloudinary.uploader


from config.config import settings


class Cloudinary:
    """Service Class for  Cloudinary Images

    :return: _description_
    :rtype: _type_
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
        """static method generate_public_id_by_email

        :param email: _description_
        :type email: str
        :param app_name: _description_, defaults to settings.app_name
        :type app_name: str, optional
        :return: _description_
        :rtype: str
        """
        name = hashlib.sha224(email.encode("utf-8")).hexdigest()[:16]
        return f"APP_{app_name}/{name}"

    @staticmethod
    def upload(file, public_id: str):
        """static method  upload

        :param file: _description_
        :type file: _type_
        :param public_id: _description_
        :type public_id: str
        :return: _description_
        :rtype: _type_
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, overwrite=True)
        return r

    def generate_url(r, public_id) -> str:
        """static method generate_url

        :param r: _description_
        :type r: _type_
        :param public_id: _description_
        :type public_id: _type_
        :return: _description_
        :rtype: str
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")  # type: ignore
        )
        return src_url
