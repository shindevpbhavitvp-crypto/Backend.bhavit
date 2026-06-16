from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "Student Notice Board API"}

if __name__ == '__main__':
    app.run(debug=True)