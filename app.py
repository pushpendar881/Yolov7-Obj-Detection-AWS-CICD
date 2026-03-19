# Testing Data Ingestion component below

# from isd.pipeline.training_pipeline import TrainPipeline

# obj = TrainPipeline()
# obj.run_pipeline()
# -------------------------------------------------------------


import sys
import os
import subprocess
from pathlib import Path
from isd.pipeline.training_pipeline import TrainPipeline
from isd.exception import isdException
from isd.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template,Response
from flask_cors import CORS, cross_origin



app = Flask(__name__)
CORS(app)


class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"



@app.route("/train")
def trainRoute():
    obj = TrainPipeline()
    obj.run_pipeline()
    return 


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=['POST','GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']
        # Save input deterministically into the project ./data folder (absolute path),
        # so we don't depend on the process working directory.
        input_image_path = Path(__file__).parent / "data" / clApp.filename
        decodeImage(image, str(input_image_path))

        # we can add the code here to download the model (best.pt) from S3 bucket if the 
        # model is not there in local dir. This code of downloading from s3 is there in
        # USVisa project.
        # Run YOLOv7 detection with deterministic output folder so the API always returns the latest result.
        # Also raise the confidence threshold to avoid "too many boxes" by default.
        yolov7_dir = Path(__file__).parent / "yolov7"
        output_project = "runs/detect"
        output_name = "api"
        conf_thres = "0.50"
        iou_thres = "0.50"

        cmd = [
            sys.executable,
            "detect.py",
            "--weights",
            "best.pt",
            "--source",
            str(input_image_path),
            "--conf-thres",
            conf_thres,
            "--iou-thres",
            iou_thres,
            "--project",
            output_project,
            "--name",
            output_name,
            "--exist-ok",
        ]
        subprocess.run(cmd, cwd=str(yolov7_dir), check=True)

        opencodedbase64 = encodeImageIntoBase64(
            str(yolov7_dir / output_project / output_name / "inputImage.jpg")
        )
        result = {"image": opencodedbase64.decode('utf-8')}
        # os.system("rm -rf yolov7/runs")

    except ValueError as val:
        print(val)
        return Response("Value not found inside  json data")
    except KeyError:
        return Response("Key value error incorrect key passed")
    except Exception as e:
        print(e)
        result = "Invalid input"

    return jsonify(result)


if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host="0.0.0.0", port=8080)