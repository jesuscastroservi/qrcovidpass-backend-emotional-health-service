from flask import request
from utils.ext import Response
from functools import wraps
from formencode import validators
from datetime import datetime
from google.cloud import firestore 
from firebase_admin import firestore
import re

class ValideFields(object):

    errors = []

    @classmethod
    def validate(self, expected_args, json_data):
        missing = [field for field in expected_args if field['name'] not in json_data]
        if len(missing) > 0:
            return {'missing fields': missing}
        for i, field in enumerate(expected_args):
            for validate in field['type']:
                if validate == "alphanumeric":
                    if not json_data[field['name']].isalnum():
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                    else:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                elif validate == "email":
                    try:
                        validators.Email(not_empty=True).to_python(json_data[field['name']])
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                    except Exception as e:
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                elif validate == 'string':
                    if not isinstance(json_data[field['name']], str):
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                    else:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                elif validate == 'integer':
                    if  not str(json_data[field['name']]).isdigit():
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                    else:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                elif validate == 'notempty':
                    try:
                        validators.NotEmpty(not_empty=True).to_python(json_data[field['name']])
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                    except Exception as e:
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                elif validate == 'date':
                    try:
                        d = datetime.strptime(json_data[field['name']], field['format'])
                        try:
                            self.errors.remove("Invalid date format.  Use yyyy-mm-dd")
                            break
                        except Exception:
                            break
                    except Exception as e:
                        print(e)
                        self.errors.append("Invalid date format.  Use yyyy-mm-dd")
                elif validate == 'list':
                    if type(json_data[field['name']]) == list:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                    else:
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                elif field['type'] == 'dict':
                    if type(json_data[field['name']]) == dict:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                    else:
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
                elif validate == 'bool':
                    if type(json_data[field['name']]) == bool:
                        try:
                            self.errors.remove("Invalid %s." % field['name'].capitalize())
                            break
                        except Exception:
                            break
                    else:
                        message = "Invalid %s." %field['name'].capitalize()
                        if message not in self.errors:
                            self.errors.append(message)
            if 'values' in field.keys():
                if 'string' in field['type']:
                    if json_data[field['name']] not in field['values']:
                        self.errors.append("""Invalid value for field {0} the correct fields are {1} the value [{2}] is incorrect """.format(field['name'], field['values'], json_data[field['name']]).replace('\t', '').replace('\n', ''))
                elif 'list' in field['type']:
                    for values in json_data[field['name']]:
                        if values not in field['values']:
                            self.errors.append("""Invalid value for field {0} the correct fields are {1} the value [{2}] is incorrect""".format(field['name'], field['values'], values).replace('\t', '').replace('\n', ''))
                elif 'dict' in field['type']:
                    for values in json_data[field['name']]:
                        if values not in field['values']:
                            self.errors.append("""for field {0} the key must be some the next values {1} the value [{2}] is incorrect""".format(field['name'], field['values'], values).replace('\t', '').replace('\n', ''))
            if 'null' in field.keys():
                if field['null'] == 'true':
                    if not json_data[field['name']]:
                        return []
        return []

    @classmethod
    def validate_request(self, *expected_args):
        self.errors = []
        json_data = request.data
        if isinstance(json_data, list):
            for data in json_data:
                validate = self.validate(expected_args[0], data)
        else:
            validate = self.validate(expected_args[0], json_data)
        if isinstance(validate, dict):
            if 'missing fields' in validate.keys():
                return validate
        if len(self.errors) > 0:
                return self.errors
        else:
            return []


class Field():

    def __init__(self, name=None, primary_key=False, max_length=None, min_length=None, blank=True, null=True, default=None, choices=(), error_messages=None, auto_now=False, struct=None):
        self.name = name
        self.max_length = max_length
        self.null = null
        self.default = default
        self.value = self.default
        self.blank = blank
        self.choices = choices 
        self.primary_key = primary_key
        self.auto_now = auto_now
        self.struct = struct
        self.min_length = min_length
    

    def clean(self, value, model_instance):
        if not self.default == value:
            self.valide(value)
            self._check_field_name()
            self.valide_length(value)
        return value

    def valide_length(self, value):
        if not self.null:
            if self.max_length is not None:
                if len(str(value)) > self.max_length:
                    raise Exception(
                        "Invalid lenght by field {0}, max lenght must be {1}".format(
                            self.name, str(self.max_length)))
            if self.min_length is not None:
                if len(str(value)) < self.min_length:
                    raise Exception(
                        "Invalid lenght by field {0}, min lenght must be {1}".format(
                            self.name, str(self.min_length)))
        return self

    def to_python(self, value):
        return value

    def valide(self, value):
        if len(self.choices) != 0:
            if value not in self.choices:
                raise Exception(
                    "Invalid value by field {0}, value must be {1}".format(
                        self.name, str(self.choices)))
        if value is None and not self.null:
            raise Exception(
                "Field {0} can't null".format(self.name))
        if value is None and not self.blank:
            raise Exception(
                "Field {0} can't blank".format(self.name))

    def _check_field_name(self):
        if self.name == None:
            return [
                'Field names cannot be null',
            ]
        elif self.name == 'pk':
            return [
                "'pk' is a reserved word that cannot be used as a field name.",
            ]
        else:
            return []

class CharField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, str) or value is None:
            return value
        return str(value)


class IntegerField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators = []

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise Exception(
                "Invalid value for field %s must be integer"% self.name
            )

class BooleanField(Field):

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.validators = []
    
    def to_python(self,value):
        if value is None:
            return None
        if isinstance(value,bool):
            return value
        else:
            raise Exception(
                "Invalid value for field %s must be boolean"% self.name
            )

class DatetimeField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.auto_now:
            self.default = firestore.SERVER_TIMESTAMP
        self.validators = []

    def to_python(self, value):
        return value


class ArrayField(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators = []

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, list) or isinstance(value, tuple):
            return value
        else:
            raise Exception(
                "Invalid value for field %s must be array"% self.name
            )

class GeoPointField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        if isinstance(value, firestore.GeoPoint):
            return value
        else:
            raise Exception(
                "Invalid value for field %s must be GeoPoint"% self.name
            )

class EmailField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        try:
            validators.Email(not_empty=True).to_python(value)
            return value
        except Exception as e:
            if value and not self.null:
                raise Exception(
                    "Invalid email for field %s"% value
                )


class ReferenceField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        return value

        
