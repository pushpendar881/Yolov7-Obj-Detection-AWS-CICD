from flask_cors import CORS, cross_origin
import os
import sys
import subprocess
from pathlib import Path
from isd.pipeline.training_pipeline import TrainPipeline
from isd.exception import isdException
from isd.utils.main_utils import decodeImage, encodeImageIntoBase64
from flask import Flask, request, jsonify, render_template, Response

app = Flask(__name__)
CORS(app)

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"

@app.route("/train")
def trainRoute():
    obj = TrainPipeline()
    obj.run_pipeline()
    return "Training complete"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=['POST', 'GET'])
@cross_origin()
def predictRoute():
    try:
        image = request.json['image']

        # Save input image
        input_image_path = Path(__file__).parent / "data" / clApp.filename
        input_image_path.parent.mkdir(parents=True, exist_ok=True)  # ✅ FIX: create /data if missing
        decodeImage(image, str(input_image_path))

        yolov7_dir = Path(__file__).parent / "yolov7"
        output_project = "runs/detect"
        output_name = "api"
        output_dir = yolov7_dir / output_project / output_name
        output_image_path = output_dir / clApp.filename  # ✅ FIX: use same filename as input

        # Clean previous output to avoid stale results
        if output_image_path.exists():
            output_image_path.unlink()  # ✅ FIX: delete old result before running

        conf_thres = "0.50"
        iou_thres = "0.50"

        cmd = [
            sys.executable,
            "detect.py",
            "--weights", "best.pt",
            "--source", str(input_image_path),
            "--conf-thres", conf_thres,
            "--iou-thres", iou_thres,
            "--project", output_project,
            "--name", output_name,
            "--exist-ok",
        ]

        subprocess.run(cmd, cwd=str(yolov7_dir), check=True)

        # ✅ FIX: verify output exists before encoding
        if not output_image_path.exists():
            # List what's actually in the output dir for debugging
            files = list(output_dir.glob("*")) if output_dir.exists() else []
            print(f"Output dir contents: {files}")
            return Response(f"Detection ran but output image not found. Files: {files}")

        opencodedbase64 = encodeImageIntoBase64(str(output_image_path))
        result = {"image": opencodedbase64.decode('utf-8')}

    except ValueError as val:
        print(val)
        return Response("Value not found inside json data")
    except KeyError:
        return Response("Key value error incorrect key passed")
    except Exception as e:
        print(e)
        result = "Invalid input"

    return jsonify(result)

if __name__ == "__main__":
    clApp = ClientApp()
    app.run(host="0.0.0.0", port=8080)
