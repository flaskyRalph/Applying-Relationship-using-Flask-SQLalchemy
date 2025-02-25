from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_hashing import Hashing
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = Flask(__name__)
app.config['SECRET_KEY'] = "Do_not_expose"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///First_database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

hashing = Hashing(app)

class Username(db.Model):
    user_ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, unique=True)
    firstname: Mapped[str]
    lastname: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    
    def __repr__(self):
        return self.username

    def hash_pass(password):
        return hashing.hash_value(password, salt="abcd")


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 
