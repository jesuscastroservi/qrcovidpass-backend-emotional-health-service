from utils.firebase import ModelFirebase
from utils import valide
import datetime
from dateutil.relativedelta import relativedelta


class ModelEmotionalHealth(ModelFirebase):
    estado = valide.CharField(max_length=40, null=False, blank=False)
    datetime = valide.DatetimeField()

    @classmethod
    def set_parameters(self, data, table_name):
        """
        Inicializa parámetros de la clase de acuerdo a información del usuario.
        
        **Argumentos:**
            - data: información proveniente de la petición http
            - table_name: ruta de la colección en la base de datos
        """

        self.id_user = data['documento']
        self.estado.value=data['estado']
        self.datetime.value=datetime.datetime.utcnow()
        self.data = data
        self.__tablename__ = table_name
