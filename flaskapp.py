import os
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from flask_wtf  import FlaskForm
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

# CONFIG AND INIT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this is my secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

bootstrap = Bootstrap(app)

# DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
db = SQLAlchemy(app)

migrate = Migrate(app, db)



# VIEWS

@app.route('/')
def index():
    tasks = db.session.query(Task).all()
    return render_template('index.html', tasks=tasks)

@app.route('/new', methods=['GET', 'POST'])
def new_task():
    form = NewForm()
    if form.validate_on_submit():
        task= Task(title=form.title.data, description=form.description.data)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('newtask.html', form=form)


@app.route('/delete/<id>')
def delete_task(id):
    Task.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<id>', methods=['GET', 'POST'])
def update_task(id):
    task = Task.query.get(id)
    form = EditForm()
    if form.validate_on_submit():
        task = Task.query.filter_by(id=id).first()
        task.title =  form.title.data
        print(task.title)
        print(form.title.data)
        task.description = form.description.data
        db.session.commit()
        return redirect(url_for('index'))
    form.description.data = task.description
    form.title.data = task.title

    return render_template('edittask.html', form=form)


@app.route('/done/<id>')
def doned_task(id):
    task = Task.query.get(id)
    task.done = not(task.done)
    db.session.commit()
    print(task.done)
    return redirect(url_for('index'))



@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Task=Task)






# MODELS

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(64))
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.title

class NewForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_email(self, field):
        if Task.query.filter_by(title=field.data).first():
            raise ValidationError('Task already registered.')

class EditForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Edit')



