import os
import pickle
import tempfile
import hnswlib
from flask import Flask, request, jsonify
from google.cloud import storage

BUCKET_NAME = os.getenv('BUCKET_NAME')

# Download hnswlib index from GCS
client = storage.Client()
bucket = client.get_bucket(BUCKET_NAME)
blob = bucket.get_blob('index_5k.bin')
f = tempfile.NamedTemporaryFile(mode='wb', delete=False)
blob.download_to_file(f)
f.close()

# Load index
# Note: this index must be created by the same version hnswlib
dim = 1024
p = hnswlib.Index(space='cosine', dim=dim)
p.load_index(f.name)

# Download file name list from GCS
blob = bucket.get_blob('file_names.pkl')
f = tempfile.NamedTemporaryFile(mode='wb', delete=False)
blob.download_to_file(f)
f.close()

with open(f.name, "rb") as fp:
  file_names = pickle.load(fp)

app = Flask(__name__)


@app.route('/', methods=['POST'])
def nn_search():

    data = request.get_json()
    feature = data['feature']

    labels, x = p.knn_query(feature, k=1)
    url = "https://storage.googleapis.com/{}/images/{}".format(
        BUCKET_NAME, file_names[labels[0][0]])

    # return jsonify({"labels": labels.tolist(), "distance": x.tolist()})
    return jsonify({"url": url, "distance": x.tolist()[0][0]})


if __name__ == "__main__":
    app.run(debug=False, threaded=False, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
