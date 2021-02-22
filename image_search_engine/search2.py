# import packages
from __future__ import print_function
from image_search_pipeline.descriptors import DetectAndDescribe
from image_search_pipeline.information_retrieval import BagOfVisualWords
from image_search_pipeline.information_retrieval import Searcher
from image_search_pipeline.information_retrieval import chi2_distance
from image_search_pipeline import ResultsMontage
from scipy.spatial import distance
from redis import Redis
from imutils.feature import FeatureDetector_create, DescriptorExtractor_create
import argparse
import pickle
import imutils
import json
import cv2

# construct the argument parser and parse the argument
# ap = argparse.ArgumentParser()
# ap.add_argument("-d", "--dataset", required = True, help = "Path to the directory of indexed images")
# ap.add_argument("-f", "--features_db", required = True, help = "Path to the feature database")
# ap.add_argument("-b", "--bovw_db", required = True, help = "Path to the bag-of-visual-words database")
# ap.add_argument("-c", "--codebook", required = True, help = "Path to the codebook")
# ap.add_argument("-i", "--idf", type = str, help = "Path to inverted document frequencies array")
# ap.add_argument("-r", "--relevant", required = True, help = "Path to the relevant dictionary")
# ap.add_argument("-q", "--query", required = True, help = "Path to the query image")
# args = vars(ap.parse_args())

class Search:
    def __init__(self, features_db, bovw_db, codebook, idf):
        # store our index path
        self.features_db = features_db
        self.bovw_db = bovw_db
        self.codebook = codebook
        self.idf = idf
    def imageRetrieve(self, queryImg):
        # initialize the keypoint detector, local invariant descriptor, descriptor pipeline,
        # distance metric, and inverted document frequency array
        detector = FeatureDetector_create("SURF")
        descriptor = DescriptorExtractor_create("RootSIFT")
        dad = DetectAndDescribe(detector, descriptor)
        distanceMetric = chi2_distance
        idf = self.idf
        self.queryImage = queryImg

        # if the path to the inverted document frequency is array was supplied, then load
        # idf array and update the distance metric
        # if args["idf"] is not None:
        idf = pickle.loads(open(idf, "rb").read())
        distanceMetric = distance.cosine

        # load the codebook vocabulary and initialize the BOVW transformer
        vocab = pickle.loads(open(self.codebook, "rb").read())
        bovw = BagOfVisualWords(vocab)

        # load the relevant queries dictionary and lookup the relevant results for the
        # query image
        # relevant = json.loads(open(args["relevant"]).read())
        # queryFilename = args["query"][args["query"].rfind("/") + 1:]
        # queryRelevant = relevant[queryFilename]

        # load the query image and process it
        # queryImage = cv2.imread(self.queryImage)
        # cv2.imshow("Query", imutils.resize(queryImage, width = 320))
        queryImage = self.queryImage
        queryImage = imutils.resize(queryImage, width = 320)
        # queryImage = cv2.cvtColor(queryImage, cv2.COLOR_BGR2GRAY)

        # extract features from the query image and construct a bag-of-visual-word from  it
        (_, descs) = dad.describe(queryImage)
        hist = bovw.describe(descs).tocoo()

        # connect to redis and perform the search
        redisDB = Redis(host = "localhost", port = 6379, db = 0)
        searcher = Searcher(redisDB, self.bovw_db, self.features_db, idf = idf,
            distanceMetric = distanceMetric)
        sr = searcher.search(hist, numResults = 20)
        print("[INFO] search took: {:.2f}s".format(sr.search_time))

        # initialize the results montage
        montage = ResultsMontage((240, 320), 5, 20)

        return sr.results
        # loop over the individual results
        # for (i, (score, resultID, resultsIdx)) in enumerate(sr.results):
        #     # load the result image and display it
        #     print("[RESULT] {result_num}. {result} - {score:.2f}".format(result_num = i + 1,
        #         result = resultID, score = score))
            # result = cv2.imread("{}/{}".format(args["dataset"], resultID))
            # montage.addResult(result, text = "#{}".format(i + 1),
            #     highlight = resultID in queryRelevant)

        # show the output image of results
        # cv2.imshow("Results", imutils.resize(montage.montage, height = 700))
        # cv2.waitKey(0)
        searcher.finish()

        # cv2.destroyAllWindows()
