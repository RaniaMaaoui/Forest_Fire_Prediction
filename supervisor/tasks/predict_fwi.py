from celery import shared_task
from supervisor.models.data import Data
import joblib
import numpy as np
import os
import json
from json import JSONEncoder

class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class MLModel:
    _instance = None
    _model = None
    _scaler = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        if self._model is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "ml_model", "xgb_fwi_model.joblib")
            self._model = joblib.load(model_path)
        return self._model

    def get_scaler(self):
        if self._scaler is None:
            scaler_path = os.path.join(os.path.dirname(__file__), "..", "ml_model", "fwi_scaler.joblib")
            self._scaler = joblib.load(scaler_path)
        return self._scaler

@shared_task(bind=True, name="predict_single_fwi", queue="predict_fwi", serializer='json')
def predict_single_fwi(self, data_id):
    try:
        model_instance = MLModel()
        model = model_instance.get_model()
        scaler = model_instance.get_scaler()

        data = Data.objects.get(idData=data_id)

        features = [
            float(data.temperature),
            float(data.humidity),
            float(data.wind),
            float(data.rain or 0),
            float(data.ffmc),
            float(data.dmc),
            float(data.isi),
        ]

        features_scaled = scaler.transform([features])

        prediction = float(model.predict(features_scaled)[0])

        data.fwi_predit = prediction  # stocker dans fwi_predit
        data.save()

        result = {
            "status": "predicted",
            "fwi_predit": prediction
        }
        return json.dumps(result, cls=NumpyEncoder)

    except Exception as e:
        raise self.retry(exc=e, countdown=10)




'''from celery import shared_task
from supervisor.models.data import Data
import joblib
import numpy as np
import os
import json
from json import JSONEncoder

# Custom JSON Encoder pour gérer les types numpy
class NumpyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

class MLModel:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        if self._model is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "ml_model", "xgb_best_model1.pkl")
            self._model = joblib.load(model_path)
        return self._model

@shared_task(bind=True, name="predict_single_fwi", queue="predict_fwi", serializer='json')
def predict_single_fwi(self, data_id):
    try:
        model = MLModel().get_model()
        data = Data.objects.get(idData=data_id)
        
        features = [
            float(data.temperature),
            float(data.humidity),
            float(data.pressur),
            float(data.gaz),
            float(data.wind),
            float(data.rain or 0),
            float(data.ffmc),
            float(data.dmc or 0),
            float(data.isi)
        ]

        # Conversion explicite en float Python
        prediction = float(model.predict(np.array([features]))[0])
        data.fwi = prediction
        data.save()
        
        # Utilisation de notre encodeur personnalisé
        result = {
            "status": "predicted", 
            "fwi": prediction
        }
        return json.dumps(result, cls=NumpyEncoder)

    except Exception as e:
        raise self.retry(exc=e, countdown=10)'''
