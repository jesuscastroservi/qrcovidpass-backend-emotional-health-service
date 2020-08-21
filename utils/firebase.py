from google.cloud import firestore
from utils.valide import Field
from utils.valide import CharField
class ModelFirebase():
	db = firestore.Client()
	__tablename__ = None
	group = False
	fields = []
	errors = []
	id = None

	def __new__(cls, data={}, pk=None):
		cls.fields = []
		cls.errors = []
		cls.data = data
		cls.id = None
		fields = cls.get_fields()
		cls.set_pk(data)
		if pk:
			cls.id.value = pk
		return cls

	@classmethod
	def valide(self, patch=False):
		errors = {}
		for field in self.fields:
			try:
				if field.name in self.data.keys():
					field.value = self.data[field.name]
					setattr(self, field.name, field)
				else:
					value = getattr(self, field.name, None)
					if isinstance(value, Field):
						field.value = value.default
				if not patch:
					field.value = field.clean(field.value, self)
			except Exception as e:
				self.errors.append(str(e))
		return errors

	@classmethod
	def set_pk(self, data):
		if self.id == None:
			self.id = CharField(max_length=200, name='id', primary_key=True)
		else:
			pk_name = [f.name for f in self.fields if f.primary_key][0]
			if self.id.name in data.keys():
				self.id.value = data[self.id.name]
			elif pk_name in data.keys():
				self.id.value = data[pk_name]
			else:
				self.id.value = None

	@classmethod
	def get_fields(self):
		if len(self.fields) == 0:
			self_dict = self.__dict__
			for d in self_dict:
				if isinstance(self_dict[d], Field):
					self_dict[d].name = d
					self_dict[d]._check_field_name()
					self.fields.append(self_dict[d])
					if self_dict[d].primary_key:
						setattr(self, 'id', self_dict[d].__copy__())
		return self.fields


	@classmethod
	def queryset(self):
		doc_ref = None
		if self.group == False:
			if len(self.__tablename__.split('/'))%2 == 0:
				docs = self.__tablename__.split('/')
				doc_ref = self.db.collection(docs[0])
				docs.remove(docs[0])
				path = ",".join(docs).replace(",","/")
				doc_ref = doc_ref.document(path)
			else:
				doc_ref = self.db.collection(self.__tablename__)
		else:
			doc_ref = self.db.collection_group(self.__tablename__)
		return doc_ref

	@classmethod
	def validations(self, select=[], filters=[]):
		doc_ref = self.queryset()
		if len(filters) == 0 and len(select) == 0:
			data = doc_ref.stream()
		elif len(filters) == 0 and len(select) > 0:
			data = doc_ref.select(select).stream()
		else:
			for f in filters:
				if len(select) == 0:
					doc_ref = doc_ref.where(*f)
				else:
					doc_ref = doc_ref.select(select).where(*f)
			data = doc_ref.stream()
		return data

	@classmethod
	def get(self, select=[], filters=[], parent=False):
		doc_ref = self.queryset()
		data = []
		if self.id == None:
			data = self.validations(select, filters)
		else:
			if self.id.value:
				data = [doc_ref.document(str(self.id.value)).get()]
			else:
				data = self.validations(select, filters)

		return self.to_dict(data, parent)

	@classmethod
	def to_dict(self, data, parent=False):
		
		datos = []
		for d in data:
			d2 = d.to_dict()
			if d2:
				if parent:
					path_parent = d.reference.parent._parent_info()[0].split('/')
					d2.update({'id': d.id, 'path_parent': '/'.join(path_parent), 'id_parent': 
					path_parent[len(path_parent)-1]})
				else:
					d2.update({'id': d.id})
			datos.append(d2)
		return datos

	@classmethod
	def object_data(self, fields, update=False):

		aux = {}
		for f in fields:
			value = getattr(self, f.name, None)
			if value:
				value = value.value
			if not update:
				aux[f.name] = value
			elif f.name in self.data.keys():
				aux[f.name] = self.data[f.name]
		return aux

	@classmethod
	def _do_update(self, fields, pk_value=None, create=False,valide=True):

		doc_ref = self.queryset()
		if valide == True:
			data = self.object_data(fields, True)
		else:
			data = self.data
		if pk_value:
			try:
				dataF = doc_ref.document(str(pk_value)).update(data)
				data.update({'id': pk_value})
				return data
			except Exception as e:
				if create:
					return self._do_insert(self.id.value)
				else:
					return {}
		return {}

	@classmethod
	def get_all_documents(self, collection, instance):

		doc_ref = self.queryset()
		docs = doc_ref.collection(collection).stream()
		if instance:
			return docs
		else:
			return self.to_dict(docs)
	
	@classmethod
	def delete_all_documents(self, instance):

		for doc in instance:
			doc.reference.delete()
		return self
	
	@classmethod
	def delete(self):

		doc_ref = self.queryset()
		if self.id.value:
			dataF = doc_ref.document(str(self.id.value)).delete()
			return {}
		return {}

	@classmethod
	def _do_insert(self, fields, pk_value=None, valide=True):

		doc_ref = self.queryset()
		if valide:
			data = self.object_data(fields)
		else:
			data = self.data
		if pk_value:
			dataF = doc_ref.document(str(pk_value)).set(data)
			data.update({'id': pk_value})
		else:
			try:
				dataF = doc_ref.add(data)
				data.update({'id': dataF[1].id})
				self.id.value = data['id']
			except Exception as e:
				dataF = doc_ref.set(data)
		response = {}
		for k, v in data.items():
			response[k] = v
		return response

	@classmethod
	def save(self, update=False, create=False, valide=True):
		if len(self.errors) == 0:
			if self.id:
				if getattr(self.id,'value',None):
					if update:
						return self._do_update(fields=self.get_fields(), pk_value=self.id.value, create=create, valide=valide)
					else:
						return self._do_insert(fields=self.get_fields(), pk_value=self.id.value, valide=valide)
				else:
					return self._do_insert(fields=self.get_fields(), valide=valide)
			else:
				return self._do_insert(fields=self.get_fields(), valide=valide)
		else:
			return {"errors": [self.errors]}
	