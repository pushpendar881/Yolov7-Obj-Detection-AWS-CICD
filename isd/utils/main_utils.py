import os.path
import sys
import yaml
import base64

from isd.exception import isdException
from isd.logger import logging


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            logging.info("Read yaml file successfully")
            return yaml.safe_load(yaml_file)

    except Exception as e:
        raise isdException(e, sys) from e


def decodeImage(imgstring, fileName):
    imgdata = base64.b64decode(imgstring)
    # If fileName is an absolute/relative path, write exactly there.
    # Otherwise, default to saving under ./data/<fileName> for backward compatibility.
    target_path = fileName
    if not os.path.isabs(fileName) and os.path.dirname(fileName) == "":
        target_path = os.path.join(".", "data", fileName)

    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    with open(target_path, 'wb') as f:
        f.write(imgdata)
        f.close()


def encodeImageIntoBase64(croppedImagePath):
    with open(croppedImagePath, "rb") as f:
        return base64.b64encode(f.read())