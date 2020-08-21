from flask_restful import Api
from flask import Flask
from flask import Flask
from importlib import import_module
from firebase_admin import (
    credentials,
    firestore,
    initialize_app
)
import firebase_admin
from flask_cors import CORS
import sys
import os
import logging

app = Flask(__name__)



if __name__ == "__main__":
    # Configuración de Logger para GCP
    app.logger.handlers = []
    gcp_handler = logging.StreamHandler(sys.stdout)
    gcp_handler.setLevel(logging.DEBUG)
    gcp_handler.setFormatter(
        logging.Formatter('{"time":"%(asctime)s", "severity": "%(levelname)s", "module":"%(module)s", "message": "%(message)s"}')
    )
    app.logger.addHandler(gcp_handler)
    app.logger.setLevel(logging.DEBUG)

api = Api(app)
CORS(app)

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)

from importlib import import_module
import_module('urls')
