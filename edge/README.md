Before going through this setup, finish [Cloud Run deployment](../cloudrun) first.

### Download tflite files

```
$ wget https://github.com/google-coral/edgetpu/raw/master/test_data/mobilenet_v1_1.0_224_quant_embedding_extractor.tflite
$ wget https://github.com/google-coral/edgetpu/raw/master/test_data/mobilenet_v1_1.0_224_quant_embedding_extractor_edgetpu.tflite
```

Locate these files to same directory as `server.py`.

### Install requirements

To install OpenCV for Coral Dev Board, refer to [this repository](https://github.com/google-coral/examples-camera/tree/master/opencv)

```
$ pip install -r requirements.txt
$ apt install python3-opencv
```

### How to start

```
$ export CLOUDRUN_URL="coral-image-search-xxx.a.run.app"
$ python3 server.py
```

Once the server is ready, Open `localhost:8080` on your browser.
