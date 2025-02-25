from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# Database configurations
app.config['SECRET_KEY'] = "Do_not_expose"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost/flask_db'  # PostgreSQL
app.config['SQLALCHEMY_BINDS'] = {'logs': 'sqlite:///logs.db'}  # SQLite for logging
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define PostgreSQL User model
class Users(db.Model):
    __tablename__ = 'users'  # Explicit table name
    userID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Fname: Mapped[str] = mapped_column(String(50), nullable=False)
    Lname: Mapped[str] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Relationship to Log model
    logs = relationship('Log', back_populates='user', cascade='all, delete-orphan')


# Define SQLite Log model
class Log(db.Model):
    __tablename__ = 'logs'  # Explicit table name
    __bind_key__ = "logs"
    logID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=db.func.now())
    
    # Foreign key to Users table
    userID: Mapped[int] = mapped_column(Integer, ForeignKey('users.userID', ondelete="CASCADE"), nullable=False)
    user = relationship('Users', back_populates='logs')


def log_action(action, user_id):
    """Log an action with the user's ID."""
    log_entry = Log(action=action, userID=user_id)
    db.session.add(log_entry)
    db.session.commit()


@app.route('/')
def homePage():
    users = Users.query.all()
    return render_template('index.html', users=users)


@app.route('/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        Fname = request.form['Fname']
        Lname = request.form['Lname']
        email = request.form['email']
        new_user = Users(Fname=Fname, Lname=Lname, email=email)
        db.session.add(new_user)
        db.session.commit()
        log_action(f"Created user {Fname.title()} {Lname.title()}", new_user.userID)
        return redirect(url_for('homePage'))
    return render_template('create.html')


@app.route('/update/<int:userID>', methods=['GET', 'POST'])
def update_user(userID):
    user = Users.query.get(userID)
    if not user:
        return redirect(url_for('homePage'))
    if request.method == 'POST':
        user.Fname = request.form['Fname']
        user.Lname = request.form['Lname']
        user.email = request.form['email']
        db.session.commit()
        log_action(f"Updated user {user.Fname} {user.Lname}", user.userID)
        return redirect(url_for('homePage'))
    return render_template('update.html', user=user)


@app.route('/delete/<int:userID>')
def delete_user(userID):
    user = Users.query.get(userID)
    if user:
        db.session.delete(user)
        db.session.commit()
        log_action(f"Deleted user {user.Fname} {user.Lname}", user.userID)
    return redirect(url_for('homePage'))


@app.route('/logs')
def view_logs():
    logs = Log.query.all()
    return render_template('logs.html', logs=logs)


if __name__ == '__main__':
    app.run(debug=True)
