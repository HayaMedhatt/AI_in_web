from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np

# Load the trained model
#model = tf.keras.models.load_model('model.h5')

# Initialize Flask app
app = Flask(__name__)

@app.get('/test')
def test():
    return "test"
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     input_data = np.array(data['input']).reshape(1, -1)
#     prediction = model.predict(input_data)
#     return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

