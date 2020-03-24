import os
import sys
from flask import Flask, Response, render_template, request
from PIL import Image
import numpy as np
import requests
import json
import cv2
import time
import queue
from inference import Inference

app = Flask(__name__)

CLOUDRUN_URL = os.environ.get('CLOUDRUN_URL')
if not CLOUDRUN_URL:
  sys.exit("Specify Cloud Run URL." \
           "e.g. $export CLOUDRUN_URL=\"coral-image-search-xxx.a.run.app\"")

# Camera settings
print('Initialize camera')
camera = cv2.VideoCapture(0)
if not camera.isOpened():
  raise RuntimeError('Could not start camera.')
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Using requests.Session to activate keep-alive
# https://requests.readthedocs.io/en/v0.8.2/user/advanced/#keep-alive
session = requests.Session()

# TF Lite Interpreters
print('Initialize TF Lite Interpreters')
inference = Inference()

# Search result queue
q = queue.Queue()


def frames():
  # inference.init_interpreter(tpu=True)

  while True:
    # read current frame
    _, img = camera.read()
    im = Image.fromarray(img).resize((224, 224))

    t0 = time.time()
    feature = inference.extract_feature(im)
    t1 = time.time()
    res = session.post(CLOUDRUN_URL,
                       json={"feature": feature.tolist()})
    t2 = time.time()

    rank = json.loads(res.content)

    frame_data = {"inference_time": (t1 - t0) * 1000,
                  "cloudrun_time": (t2 - t1) * 1000,
                  "url": rank['url']}
    q.put(frame_data)
    print(frame_data)
    # encode as a jpeg image
    frame = cv2.imencode('.jpg', img)[1].tobytes()

    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/', methods=['GET'])
def mainpage():
  return render_template('index.html')


@app.route('/video_feed')
def video_feed():
  """Video streaming"""
  return Response(frames(),
                  mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/change_interpreter', methods=['POST'])
def change():
  """ Change TFLite Interpreter"""
  data = request.get_json()
  delegate = 'tpu' if data['tpu'] else 'cpu'
  inference.change_interpreter(delegate=delegate)

  return 'ok'


@app.route('/stream')
def search():
  """ Send search results to browser via SSE(Server-sent events)"""
  def eventStream():
    while True:
      try:
        data = q.get(timeout=0.5)
      except:
        data = {'msg': 'Cloud Run cold start'}
      yield "event: images\ndata: {}\n\n".format(json.dumps(data))
  return Response(eventStream(), mimetype="text/event-stream")


if __name__ == "__main__":
  app.run(debug=True, threaded=True, use_reloader=False,
          host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
