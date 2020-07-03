import tensorflow as tf
from pathlib import Path
from os import path

_models = { }

def get_model(model_id : str):
    if model_id in _models:
        return self._models[model_id]
    model_path = _get_model_path() / model_id / "saved_model"
    if path.exists(model_path):
        return tf.saved_model.load(str(model_path))
    raise ValueError(f"No model {model_id} is available")

def save_model(self, model_id : str, model):
    _models[model_id] = model
    model_path = _get_model_path() / model_id / "saved_model"
    tf.saved_models.save(model, str(model_path))

def save_all(self) -> None:
    for (model_id, model) in self._models:
        self.save_model(model_id, model)

def __del__(self):
    self.save_all()

def _get_model_path():
    return Path(__file__).parent.absolute() / '../../model'
