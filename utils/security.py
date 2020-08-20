from base64 import b64encode, b64decode
import hashlib
from io import BytesIO
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import os
import base64
import json
from flask import request, Request


class SecurityCipherData:

    def encrypt(plain_text):
        key = b'0123456789012345' # clave para cifrar
        iv= b'0123456789012345' # IV
        BS = AES.block_size # Tamaño del bloque de cbc
        cipher = AES.new(key, AES.MODE_CBC, iv)
        raw = pad(str.encode(plain_text), 16)
        ciphertext = b64encode( cipher.encrypt(raw)).decode('utf-8')
        return {"data": str(ciphertext)}

    def decrypt(enc_dict):

        key = b'0123456789012345' # clave para cifrar
        iv= b'0123456789012345' # IV
        BS = AES.block_size # Tamaño del bloque de cbc
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(b64decode(enc_dict['data']))
        decrypted_text = unpad(decrypted, 16)
        json_dump = str(decrypted_text).replace('\'', '\"')
        data_decrypt=json.loads(json_dump[2:-1])
        request.data =data_decrypt
        json_object = json.dumps(request.data, indent = 4) 
        data = json.loads(json_object)
        request.args=data

        return json.loads(json_dump[2:-1])
