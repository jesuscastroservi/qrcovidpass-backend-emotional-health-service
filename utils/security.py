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
        try:
            decrypted = unpad(decrypted, 16)
        except:
            pass
        decrypted=decrypted.decode(encoding='utf-8-sig')
        json_object = json.dumps(decrypted, indent = 4, sort_keys=True) 
        res = json.loads(json_object) 

        json_acceptable_string = str(res).replace('\\',"")
        data=json.loads(json_acceptable_string)
        request.data =data
        request.args=data
        return data