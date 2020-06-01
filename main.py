import os
import logging
from time import sleep
from flask import Flask, jsonify, request, make_response
from modules.indexOfCharges_update import IndexOfCharges
from modules.Signatory_Details_update import SignatoryDetails


app = Flask(__name__)


@app.route('/api/v1/indexOfCharges', methods=['GET', 'POST'])
def index_of_charges():

    if request.method == 'POST':
        input_list = request.json['data']

        try:
            obj = IndexOfCharges()
            print(input_list)
            obj.scrapper(input_list)
            return jsonify({"response": "updated"})
        except:
            return jsonify({"response": "internal error"})


@app.route('/api/v1/signatoryDetails', methods=['GET', 'POST'])
def signatory_details():

    if request.method == 'POST':
        input_list = request.json['data']
        try:
            obj = SignatoryDetails()
            obj.scrapper(input_list)
            return jsonify({"response": "updated"})
        except:
            return jsonify({"response": "internal error"})


if __name__ == '__main__':
    app.run(port=5000)

