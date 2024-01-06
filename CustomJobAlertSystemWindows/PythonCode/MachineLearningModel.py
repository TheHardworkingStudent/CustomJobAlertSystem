from joblib import load
import numpy as np
import os

class TextClassification:
    def __init__(self, threshold=0.6):
        current_directory = os.path.dirname(__file__)
        random_forest_model_path = os.path.join(current_directory,'random_forest_model.joblib')
        random_forest_encoder_path = os.path.join(current_directory,'random_forest_encoder.joblib')
        self.random_forest_model = load(random_forest_model_path)
        self.random_forest_encoder = load(random_forest_encoder_path)
        self.threshold = threshold

    def predict_category(self, text):
        # Get probabilities
        probabilities = self.random_forest_model.predict_proba([text])
        max_probability = np.max(probabilities, axis=1)

        # Apply threshold
        if max_probability < self.threshold:
            return 'unknown'
        else:
            prediction = self.random_forest_model.predict([text])
            return self.random_forest_encoder.inverse_transform(prediction)[0]
