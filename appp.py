from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rollnumber = db.Column(db.String(50))
    class_name = db.Column(db.String(50))
    department = db.Column(db.String(100))
    teacher = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"message": "Token missing"}), 401

        try:
            token = auth_header.split(" ")[1]

            jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

        except:
            return jsonify({"message": "Invalid Token"}), 401

        return f(*args, **kwargs)

    return decorated


@app.route('/register', methods=['POST'])
def register():

    data = request.json

    user = User(
        username=data['username'],
        password=data['password']
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User Registered Successfully"})



@app.route('/login', methods=['POST'])
def login():

    data = request.json

    user = User.query.filter_by(
        username=data['username'],
        password=data['password']
    ).first()

    if not user:
        return jsonify({"message": "Invalid Credentials"}), 401

    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    return jsonify({
        "token": token
    })


@app.route('/profile', methods=['POST'])
@token_required
def create_profile():

    data = request.json

    profile = Profile(
        name=data['name'],
        rollnumber=data['rollnumber'],
        class_name=data['class'],
        department=data['department'],
        teacher=data['teacher'],
        phone_number=data['phone_number']
    )

    db.session.add(profile)
    db.session.commit()

    return jsonify({
        "message": "Profile Created Successfully"
    })


@app.route('/profile', methods=['GET'])
@token_required
def get_profile():

    profiles = Profile.query.all()

    result = []

    for p in profiles:

        result.append({
            "name": p.name,
            "rollnumber": p.rollnumber,
            "class": p.class_name,
            "department": p.department,
            "teacher": p.teacher,
            "phone_number": p.phone_number
        })

    return jsonify(result)



with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)