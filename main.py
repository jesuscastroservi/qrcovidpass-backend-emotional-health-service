from __init__ import app
from sys import platform
import logging
import sys, os

if __name__ == '__main__':
    if platform in ['win32']:
        os.environ[
            "GOOGLE_APPLICATION_CREDENTIALS"] = r'D:\QRCovid\healt-service\utils\covidpass-desarrollo-999364e5e147.json'
    app.logger.handlers = []
    gcp_handler = logging.StreamHandler(sys.stdout)
    gcp_handler.setLevel(logging.DEBUG)
    gcp_handler.setFormatter(logging.Formatter('{"time":"%(asctime)s", "severity": "%(levelname)s", "module":"%(module)s", "message": "%(message)s"}'))
    app.logger.addHandler(gcp_handler)
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8000, debug=True)
