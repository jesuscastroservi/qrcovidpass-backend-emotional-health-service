from utils.security import SecurityCipherData
from flask import current_app
from flask import request
from utils.ext import Response
from flask_restful import Resource
from flask import Blueprint
from flask_restful import Api
from models import (
ModelEmotionalHealth
)
from flask import request
from utils.valide import ValideFields
import firebase_admin
from flask import (
    make_response,
    jsonify,)
from google.cloud import firestore
import datetime
import os
import copy
import logging
from dateutil.relativedelta import relativedelta


class ViewReady(Resource):

    def get(self):
        return Response.send(results={"msg": True}, status=200)


class ViewLive(Resource):

    def get(self):
        return Response.send(results={"msg": True}, status=200)

class ViewEmotionalHealth(Resource):
    id_user = None
    fields = [{
        'name': 'documento',
        'type': 'integer'
    }, {
        'name': 'estado',
        'type': 'string'
    }]


    def post(self, **kwargs):

       
        try:
            data=SecurityCipherData.decrypt(request.get_json())
            validation = ValideFields.validate_request(self.fields)
            if len(validation) > 0:
                return Response.send(results=validation, status=400)
            model = ModelEmotionalHealth
            model.set_parameters(data, f'emotional_health/{data["documento"]}')
            _data = model.save()
            _data['datetime'] = str(_data['datetime'] + relativedelta(hours=-5) )
            return Response.send(results=_data, status=201)
         
        except Exception as e:
            current_app.logger.error(
                "Error al procesar la solicitud:" + str(e),
                exc_info=True
            )

            return Response.send(results={
                "Error": "Internal server error"
                }, status=500)
        
