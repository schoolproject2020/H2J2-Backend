import bcrypt
import jwt
from flask import Flask
from flask import render_template
from flask import request, make_response
from flask import jsonify
from flask_cors import CORS
from flask_request_validator import (Param, JSON, GET, Pattern, validate_params)
from models import User
from models import db
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../H2J2-Front/public', static_folder='../H2J2-Front/public/assets')
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/check/id', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
)
def check_id(*request_element):
    userid = request_element[0]
    check = User.query.filter_by(userid=userid).first()

    if check is None:
        return {'id': True}
    else:
        return {'id': False}


@app.route('/api/register', methods=['POST'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
    Param('passwd', JSON, str, required=True),
    Param('name', JSON, str, rules=[Pattern(r'^[가-힣]*$')], required=True),
    Param('phone', JSON, str, rules=[Pattern(r'\d{2,3}-\d{3,4}-\d{4}')], required=True),
    Param('email', JSON, str, rules=[Pattern(r'[a-zA-Z0-9_-]+@[a-z]+.[a-z]+')], required=True),
    Param('address', JSON, str, required=True),
    Param('age', JSON, str, required=True),
    Param('sex', JSON, str, required=True),
    Param('height', JSON, str, required=True),
    Param('weight', JSON, str, required=True),
)
def register(*request_elements):
    userid = request_elements[0]
    check = User.query.filter_by(userid=userid).first()

    if check is None:
        hashed_password = bcrypt.hashpw(request_elements[1].encode('utf-8'), bcrypt.gensalt())

        if request_elements[6] == '남자':
            basic_metabolic = round(66.47 + (13.75 * int(request_elements[9])) + (5 * int(request_elements[8])) - (6.76 * int(request_elements[6])), 1)
        else:
            basic_metabolic = round(655.1 + (9.56 * int(request_elements[9])) + (1.85 * int(request_elements[8])) - (4.68 * int(request_elements[6])), 1)
        
        bmi = round(int(request_elements[9]) / ((int(request_elements[8]) * 0.01) * (int(request_elements[8]) * 0.01)), 1)

        user = User(
            userid = request_elements[0],
            passwd = hashed_password,
            name = request_elements[2],
            phone = request_elements[3],
            email = request_elements[4],
            address = request_elements[5],
            age = request_elements[6],
            sex = request_elements[7],
            height = request_elements[8],
            weight = request_elements[9],
            basic_metabolic = basic_metabolic,
            bmi = bmi
        )

        db.session.add(user)
        db.session.commit()

        json_request = {'register': True}
        
    else:
        json_request = {'register': False}

    return jsonify(json_request)

    
@app.route('/api/login', methods=['POST'])
@validate_params(
    Param('userid', JSON, str, rules=[Pattern(r'^[a-z0-9]+$')], required=True),  
    Param('passwd', JSON, str, required=True)
)
def login(*request_elements):
    userid = request_elements[0]
    passwd = request_elements[1]
    user = User.query.filter_by(userid=userid).first()

    if user is not None:
        is_pw_correct = bcrypt.checkpw(passwd.encode('UTF-8'), user.passwd.encode('UTF-8'))
        if is_pw_correct:
            payload = {											
                'userid' : userid,
                'exp' : datetime.now() + timedelta(seconds=1800) # 토큰 만료 시간
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')	
            json_request = {'login': 'True', 'userid': userid, 'level': 1, 'token': token.decode('UTF-8')}
            resp = make_response(json_request)
            resp.headers['Authorization'] = token.decode('UTF-8')
            return resp
        
        else:
            json_request = {'login': False}
    else:
        json_request = {'login': False}

    return jsonify(json_request)


@app.route('/api/logout', methods=['GET'])
@validate_params(
    Param('userid', GET, str, rules=[Pattern(r'^.{1,50}$')], required=True)
)
def logout(*request_elements):
    if request_elements[0] is not None:
        return {'logout': True}    
    else:
        return {'logout': False}
    

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://"  
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
app.config['SECRET_KEY'] = 'rlawjdtnrlawngusrlagmltndlagywls'
app.config['JWT_SECRET_KEY'] = 'rlawjdtnrlawngusrlagmltndlagywls'

db.init_app(app)
db.app = app
db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

# host='127.0.0.1', port=5000, debug=True
# host='0.0.0.0', port=5000, debug=True
