from flask import Flask

from flask import Flask, request
import pandas as pd
import json
import sys

from datetime import datetime, date
from dateutil import parser

import urllib.request, json

app = Flask(__name__)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


sample_response = {
    "fulfillmentMessages": [
        {
            "text": {
                "text": [
                    "Sample response from the  covid webhook"
                ]
            }
        }
    ]
}

error_response = {
    "fulfillmentMessages": [
        {
            "text": {
                "text": [
                    "Something unexpected happened. Please try again"
                ]
            }
        }
    ]
}


def create_response_obj(resp_str):
    res = sample_response
    res['fulfillmentMessages'][0]['text']['text'] = [resp_str]
    return res


unexpected_error_response = {
    "fulfillmentMessages": [
        {
            "text": {
                "text": [
                    "Error encountered. Please try again"
                ]
            }
        }
    ]
}


def read_url(url_l):
    try:
        with urllib.request.urlopen(
                url_l) as url:
            return url.read().decode()
    except:
        return None


meds = pd.DataFrame(
    json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/medicine.json'))['data'])
oxygen = pd.DataFrame(
    json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/oxygen.json'))['data'])
plasma = pd.DataFrame(
    json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/plasma.json'))['data'])
helpline = pd.DataFrame(
    json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/helpline.json'))['data'])
states = json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/states.json'))
ambulance = pd.DataFrame(
    json.loads(read_url('https://github.com/coronasafe/life/raw/main/data/ambulance.json'))[
        'data'])


def parse_response(req):
    try:
        intent = req['queryResult']['intent']
        if intent['displayName'] == 'Query':
            city =
        return create_response_obj(final_resp)

    except KeyError as e:
        eprint("KeyError parsing response", e)
        return error_response
    # except:
    #     eprint("Unexpected error parsing response")
    #     return unexpected_error_response


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        return parse_response(data)
        return sample_response
    else:
        return 'GET not implemented'


if __name__ == '__main__':
    app.run()
