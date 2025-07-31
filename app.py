from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
model_path = 'model/fruit_model.tflite'
label_path = 'model/labels.txt'

# Load labels
labels = {}
with open(label_path, 'r') as f:
    for line in f:
        idx, label = line.strip().split(' ', 1)
        labels[int(idx)] = label

# Load model
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict_image(img_path):
    img = Image.open(img_path).convert('RGB')
    img = img.resize((224, 224))  # Resize to model input size
    input_data = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])[0]

    top_indices = output_data.argsort()[::-1][:2]
    top_predictions = [(labels[i], round(100 * output_data[i], 2)) for i in top_indices]
    return ', '.join([f"{conf}% {label}" for label, conf in top_predictions])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return render_template('index.html', result="No file uploaded.")

    file = request.files['image']
    if file.filename == '':
        return render_template('index.html', result="No selected file.")

    filepath = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(filepath)

    result = predict_image(filepath)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
