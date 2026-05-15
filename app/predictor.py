import joblib
import numpy as np


class Predictor:
    def __init__(self, model_path, threshold=0.7):
        self.model = joblib.load(model_path)
        self.n_features = self.model.n_features_in_
        self.threshold = threshold

    def _prepare(self, features):
        if len(features) != self.n_features:
            raise ValueError(f"Expected {self.n_features} features")

        return np.array(features).reshape(1, -1)

    def predict_proba(self, features):
        features = self._prepare(features)
        return float(self.model.predict_proba(features)[0][1])

    def predict(self, features):
        prob = self.predict_proba(features)

        return {
            "label": int(prob > self.threshold),
            "score": prob
        }
