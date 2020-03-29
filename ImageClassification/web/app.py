from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import numpy
import tensorflow as tf
import requests
import urllib.request
import subprocess
import json
from classify_image import run_inference_on_image

app = Flask(__name__)
api = Api(app)




class Classify(Resource):
    def post(self):
        postedData = request.get_json()

        url = postedData["url"]
        urllib.request.urlretrieve(url, "temp.jpg")
        retJson = run_inference_on_image("temp.jpg")

        return retJson

api.add_resource(Classify, '/class')

if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
