from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import qrcode
from io import BytesIO
import base64
import re
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Добавьте секретный ключ для сессии

# Функция для чтения и обработки данных из файла
def read_train_data():
    url = "https://raw.githubusercontent.com/Over1Cloud/asspoj/refs/heads/main/list.txt"
    response = requests.get(url)
    content = response.text
    
    trains = {}
    for block in content.split('\n\n'):
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            train_number = lines[0][:-2]  # Удаляем последние две цифры
            if train_number not in trains:
                trains[train_number] = {}
            if '*УПУ-3' in lines[1] or '*Шкаф кабины машиниста' in lines[1]:
                trains[train_number]['code'] = lines[2]
    
    return list(trains.keys())

trains = read_train_data()

@app.route('/')
def index():
    selected_train = session.get('selected_train', '')
    return render_template('index.html', trains=trains, selected_train=selected_train)

@app.route('/select_train', methods=['POST'])
def select_train():
    selected_train = request.form.get('train')
    session['selected_train'] = selected_train
    return redirect(url_for('menu', train=selected_train))

@app.route('/menu/<train>')
def menu(train):
    return render_template('menu.html', train=train)

@app.route('/generate_qr/<train>/<operation>')
def generate_qr(train, operation):
    wagon = request.args.get('wagon', '01')
    side = request.args.get('side', 'left')
    is_clockwise = request.args.get('is_clockwise', 'true') == 'true'
    qr_data = get_qr_data(train, wagon, side, is_clockwise)
    img_str = generate_qr_image(qr_data)
    return render_template('qr.html', img_data=img_str, train=train, operation=operation, wagon=wagon)

@app.route('/generate_to1/<train>')
def generate_to1(train):
    wagon = request.args.get('wagon', '01')
    side = request.args.get('side', 'left')
    is_clockwise = request.args.get('is_clockwise', 'true') == 'true'
    qr_data = get_qr_data(train, wagon, side, is_clockwise)
    img_str = generate_qr_image(qr_data)
    wagon_type = get_wagon_type(wagon)
    mirrored = is_mirrored(wagon)
    return render_template('to1.html', img_data=img_str, train=train, wagon=wagon, side=side, wagon_type=wagon_type, mirrored=mirrored)

@app.route('/update_qr', methods=['POST'])
def update_qr():
    train = request.form.get('train')
    wagon = request.form.get('wagon')
    side = request.form.get('side')
    is_clockwise = request.form.get('is_clockwise') == 'true'  # Измените эту строку
    qr_data = get_qr_data(train, wagon, side, is_clockwise)
    img_str = generate_qr_image(qr_data)
    equipment = get_equipment(train, wagon, side, is_clockwise)
    return jsonify({'img_data': img_str, 'equipment': equipment, 'full_number': f"{train}{wagon}"})

def get_qr_data(train, wagon, side, is_clockwise):
    url = "https://raw.githubusercontent.com/Over1Cloud/asspoj/refs/heads/main/list.txt"
    response = requests.get(url)
    content = response.text
    
    blocks = content.split('\n\n')
    full_train_number = f"{train}{wagon}"
    
    for block in blocks:
        lines = block.split('\n')
        if lines[0].startswith(full_train_number):
            if side == 'left':
                patterns = ['*КП1-КП2 лев.', '*КП3-КП4 лев.'] if is_clockwise else ['*КП3-КП4 лев.', '*КП1-КП2 лев.']
            else:
                patterns = ['*КП3-КП4 пр.', '*КП1-КП2 пр.'] if is_clockwise else ['*КП1-КП2 пр.', '*КП3-КП4 пр.']
            
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if line.strip() == pattern:
                        return lines[i + 1].strip()
    
    return "Код не найден"

def get_equipment(train, wagon, side, is_clockwise):
    url = "https://raw.githubusercontent.com/Over1Cloud/asspoj/refs/heads/main/list.txt"
    response = requests.get(url)
    content = response.text
    
    blocks = content.split('\n\n')
    full_train_number = f"{train}{wagon}"
    
    for block in blocks:
        lines = block.split('\n')
        if lines[0].startswith(full_train_number):
            if side == 'left':
                patterns = ['*КП1-КП2 лев.', '*КП3-КП4 лев.'] if is_clockwise else ['*КП3-КП4 лев.', '*КП1-КП2 лев.']
            else:
                patterns = ['*КП3-КП4 пр.', '*КП1-КП2 пр.'] if is_clockwise else ['*КП1-КП2 пр.', '*КП3-КП4 пр.']
            
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if line.strip() == pattern:
                        return line.strip()
    
    return f"{patterns[0]} не найдена"

def generate_qr_image(data):
    img = qrcode.make(data)
    buffered = BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode()

def get_wagon_type(wagon):
    if wagon in ['01', '09']:
        return 'golova'
    elif wagon in ['03', '05', '07', '11']:
        return 'pricep'
    else:
        return 'motor'

def is_mirrored(wagon):
    return wagon == '08' or int(wagon) > 8

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
