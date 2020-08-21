from utils.security import SecurityCipherData
from flask import (
    make_response, 
    jsonify,
    Response
) 
import re
from flask import request
from collections import OrderedDict
from sys import platform
import os

def url(name, endpoint):
    try:
        if isinstance(endpoint, str):
            from __init__ import api
            api = api.add_resource(name, endpoint)
    except Exception as e:
        print ('Resource loading Error:', e)

        
class Response:

    @classmethod
    def error(cls, results):
        if isinstance(results, list):
            results = {'error': results}
        return results
    
    @classmethod
    def regex(cls, results):
        if isinstance(results, list) and len(results) >0:
            results = results[0]
        return results
    
    @classmethod
    def structure(cls, results):
        result = {}
        data = []
        if isinstance(results, dict) or isinstance(results, OrderedDict):
            data.append(results)
        else:
            data = results
        result['count'] = len(data)
        result['results'] = data
        return result

    @classmethod
    def response(cls, response, status):
        print("response")
        print(response)
        no_crypr = False
        if no_crypr:
            return make_response(
                jsonify(response), status)
        else:
            return make_response(
                jsonify(SecurityCipherData.encrypt(str(response))), status)
        
        
    @classmethod
    def send(cls, results=None, status=None, error=False):
        if not results:
            return  [], status
        else:
            if not isinstance(results, str) and not isinstance(results, int):
                if error:
                    return cls.response(cls.error(results), status)
                path = request.environ['RAW_URI']
                regex = re.findall(
                    '[a-zA-Z]+_*[a-zA-Z]*/\w+/*\w*', 
                    path)
                if len(regex) > 0:
                    return cls.response(cls.regex(results), status)
                return cls.response(cls.structure(results), status)
            else:
                return cls.response(
                    {'error': 'Internal server error'}, status)