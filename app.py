import os

from flask import Flask, render_template, request, jsonify

# from pyimagesearch.colordescriptor import ColorDescriptor
# from pyimagesearch.searcher import Searcher
from image_search_engine.search2 import Search

import json
from PIL import Image
from urllib.request import urlopen
import numpy
from skimage import io
import cv2
from sklearn.metrics import average_precision_score

# create flask instance
app = Flask(__name__)
app.config['FLASK_DEBUG'] = 1
INDEX = os.path.join(os.path.dirname(__file__), 'index-oxbuild.csv')

with open('groundtruth.json', 'r') as f:
    groundtruth = json.load(f)

# extra file
extra_dirs = ['./app/static']
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)

# main route
@app.route('/')
def index():
    return render_template('index.html')

# search route
@app.route('/search', methods=['POST'])
def search():

    if request.method == "POST":

        RESULTS_ARRAY = []

        # get url
        image_url = request.form.get('img')
        image_name = image_url.split("/")[5]

        print("Query Image: " + image_url)

        for queryInfo in groundtruth:
            if(queryInfo["query"] == image_name):
                cropRegion = queryInfo["region"]
                break

        pilImg = Image.open(urlopen(image_url))
        pilCrop = pilImg.crop(
            (cropRegion["x1"], cropRegion["y1"], cropRegion["x2"], cropRegion["y2"]))
        query = cv2.cvtColor(numpy.array(pilCrop), cv2.COLOR_RGB2GRAY)

        try:
            # initialize the image descriptor
            print("DEBUG 1")
            retrieve = Search("model/features.hdf5", "model/bovw.hdf5", "model/vocab.cpickle", "model/idf.cpickle")
            result = retrieve.imageRetrieve(query)
            print("DEBUG 2")

            gtComp = [0] * 20
            propScore = [0] * 20
            # loop over the results, displaying the score and image name
            for (i, (score, resultID, resultsIdx)) in enumerate(result):
                for queryInfo in groundtruth:
                    if (queryInfo["query"] == image_name and resultID in queryInfo["relevant"]):
                        gtComp[i] = 1
                RESULTS_ARRAY.append(
                    {"image": str(resultID), "score": str(gtComp[i])})
                propScore[i] = score
            gtComp = numpy.array(gtComp)
            propScore = numpy.array(propScore)

            if all(gt == 0 for gt in gtComp):
                AP = 0
            else:
                AP = average_precision_score(gtComp, propScore)
            
            # return success
            return jsonify(results=(RESULTS_ARRAY[:20]), ap=AP)

        finally:

            # return error
            jsonify({"sorry": "Sorry, no results! Please try again."})


@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# run!
if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=True, extra_files=extra_files)
