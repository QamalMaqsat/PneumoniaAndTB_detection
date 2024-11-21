from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import numpy as np
import tensorflow as tf
from datetime import datetime

# Создание экземпляра Flask
app = Flask(__name__)
classes = ['NORMAL', 'PNEUMONIA', 'TB']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    predicted_class_name = db.Column(db.String(300), nullable=False)
    date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Artickle %r>'% self.id

with app.app_context():
    db.create_all()


IMAGE_SIZE = (400, 400)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Загрузка предварительно обученной модели
resnetModel = tf.keras.models.load_model('my_model.h5')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def image_preprocessor(path):
    print('Processing Image ...')
    currImg_BGR = cv2.imread(path)
    b, g, r = cv2.split(currImg_BGR)
    currImg_RGB = cv2.merge([r, g, b])
    currImg = cv2.resize(currImg_RGB, IMAGE_SIZE)
    currImg = currImg / 255.0
    currImg = np.reshape(currImg, (1, IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    return currImg


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('app.html')

@app.route('/new', methods=['GET','POST'])
def new_page():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'imageFile' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['imageFile']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imgPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(imgPath)
            print(f"Image saved at {imgPath}")

            # Предварительная обработка изображения
            image = image_preprocessor(imgPath)

            # Предсказание с вероятностями
            predictions_proba = resnetModel.predict(image)

            # Передача предсказаний и вероятностей в шаблон
            predicted_class_index = np.argmax(predictions_proba)
            predicted_class_name = classes[predicted_class_index]
            predicted_class_probability = predictions_proba[0][predicted_class_index]
            probabilities_percent = {class_name: f"{probability*100:.2f}%" for class_name, probability in zip(classes, predictions_proba[0])}

            return render_template('result.html',
                                   predicted_class_name=predicted_class_name,
                                   predicted_class_probability=predicted_class_probability,
                                   probabilities_percent=probabilities_percent,
                                   name =filename)

    return redirect(url_for('home'))

def create_artickle(predicted_class_name):
    artickle = Article(predicted_class_name=predicted_class_name)

    try:
        db.session.add(artickle)
        db.session.commit()
        return 'Success'  # возвращаем успех
    except:
        return 'Ошибочка'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
