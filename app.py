from collections import Iterable

from flask import Flask, request
import pandas as pd
import sys

import urllib.request, json
import urllib

app = Flask(__name__)

base_c_url = "https://life.coronasafe.network"
max_count = 2


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


def create_response_obj(resp_str, samp=None):
    if samp is None:
        samp = sample_response
    res = samp
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


def get_url_for_place(place):
    if place == 'Bengaluru':
        place = 'Bengaluru (Bangalore) Urban'
    if place in states:
        return f"{base_c_url}/{place.lower().replace(' ', '_')}"
    for state in states:
        for city in states[state]:
            if place in city:
                return f"{base_c_url}/{state.lower().replace(' ', '_')}/{city.lower().replace(' ', '_')}"
    return base_c_url


def parse_type(df_o, obj, area=None, available_only=True):
    if available_only and 'availability' in df_o.columns:
        df_o = df_o[df_o['availability'] == 'Available']
    if df_o.shape[0] < 1:
        return f"Sorry, I did not get any results for {obj} in {area}. Please try with your state name here instead. If you did try with your state, please contact elsewhere as it looks like we have no record of any oxygen availability at that area!"
    res_str = f"Here are the top {max_count} items what I have for {obj} in {area}. If you need more, please visit: {get_url_for_place(area)} \n"
    count = 0
    for row in df_o.itertuples(index=False, name="Entry"):
        count += 1
        it = ""
        if count <= max_count:
            if hasattr(row, 'name') and row.name is not None and len(row.name) > 0:
                it += f"{count}. \n\t Name: {row.name}\t"
            if hasattr(row, 'contactName') and row.contactName is not None and len(
                    row.contactName) > 0:
                it += f"\t Contact Name: {row.contactName}\t"
            if hasattr(row, 'companyName'):
                it+= f"\tCompany: {row.companyName}"
            if hasattr(row, 'phone1'):
                it += f"\t Phone Numbers: +91-{str(row.phone1)}, {row.phone2 if hasattr(row, 'phone2') and row.phone2 is not None else ''}\n"

            if hasattr(row, 'emailId') and row.emailId is not None:
                it += f"\t Email: {row.emailId}"
            if hasattr(row, 'description') and row.description is not None and len(
                    row.description) > 0:
                it += f"\t Description: {row.description}\n"
            if hasattr(row, 'instructions') and row.instructions is not None and len(
                    row.instructions) > 0:
                it += f"\t Instructions: {row.instructions}\n"
            if hasattr(row, 'type') and isinstance(row.type, Iterable) and len(row.type) > 0:
                it += f"\t Types: {row.type}\n"

            if hasattr(row, 'verificationStatus') and row.verificationStatus is not None:
                it += f"\t Verification Status: {row.verificationStatus}"

            if hasattr(row, 'lastVerifiedOn') and row.lastVerifiedOn is not None:
                it += f"\t Last verified on: {row.lastVerifiedOn}\n"
            if hasattr(row, 'sourceName') and row.sourceName is not None and len(
                    row.sourceName) > 0:
                it += f"\t Source: {row.sourceName}"

        it += "\n\n\n"
        res_str += it
    return res_str


def city_mapping(city):
    m = {
        'Mumbai': 'Mumbai City',
        'Bengaluru': 'Bengaluru (Bangalore) Urban',
        'Delhi': 'West Delhi'
    }
    if city in m:
        return m[city]
    else:
        return city

def parse_response(req):
    # try:
    intent = req['queryResult']['intent']
    if intent['displayName'] == 'Query':
        place = {}
        params = req['queryResult']['parameters']
        if 'geo-city' in params and len(params['geo-city'])>0:
            place['name'] = city_mapping(params['geo-city'])
            place['type'] = 'district'
        elif 'geo-state' in params and len(params['geo-state'])>0:
            place['name'] = params['geo-state']
            place['type'] = 'state'
        else:
            create_response_obj(
                "Please specify a state of city in your query. If you did not get a response for a city, please try querying with your state",
                req)
        if 'Oxygen' in params and len(params['Oxygen']) > 0:
            # print(place)
            # print(oxygen[oxygen.loc[:,place['type']] == place['name']])
            return create_response_obj(
                parse_type(oxygen[(oxygen[place['type']] == place['name']) | (oxygen['city'] == place['name'])], obj='oxygen',
                           area=place['name']))
        elif 'Medicine' in params and len(params['Medicine']) > 0:
            return create_response_obj(
                parse_type(meds[(meds[place['type']] == place['name']) | (meds['city'] == place['name'])], obj='medicines',
                           area=place['name']))
        elif 'Plasma' in params and len(params['Plasma']) > 0:
            print(plasma[plasma[place['type']] == place['name']])
            return create_response_obj(
                parse_type(plasma[(plasma[place['type']] == place['name']) | (plasma['city'] == place['name'])], obj='plasma',
                           area=place['name']))
    return create_response_obj(
        "Sorry, I did not recognize this request"
    )

    # except KeyError as e:
    #     eprint("KeyError parsing response", e)
    #     return error_response
    # except:
    #     eprint("Unexpected error parsing response")
    #     return unexpected_error_response


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        return parse_response(data)
        # return sample_response
    else:
        return 'GET not implemented'


if __name__ == '__main__':
    app.run()
