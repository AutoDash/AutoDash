from tensorflow.keras.models import Model
from pathlib import Path
from os import path

class ModelManager:
    def __init__(self):
        self._models = { }

    def __repr__(self):
        return f"ModelManager {{ {' ,'.join(self._models.keys())} }}"

    def get_model(self, model_id : str) -> Model:
        if model_id in self._models:
            return self._models[model_id]
        model_path = _get_model_path() / f"{model_id}.h5"
        if path.exists(model_path):
            return keras.models.load_model(model_path)
        raise ValueError(f"No model {model_id} is available")

    def save_model(self, model_id : str, model : Model) -> None:
        self._models[model_id] = model
        model_path = _get_model_path() / f"{model_id}.h5"
        model.save(model_path)

    def save_all(self) -> None:
        for (model_id, model) in self._models:
            self.save_model(model_id, model)

    def __del__(self):
        self.save_all()

    def _get_model_path():
        return Path(__file__).parent.absolute() / '../../model'
