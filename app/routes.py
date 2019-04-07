import os
import uuid

from flask import render_template, flash, redirect, url_for, request, send_file
from flask_login import login_required, current_user, login_user, logout_user
from app import app, db
from app.forms import LoginForm, EditProfileForm, RegistrationForm, ChapterForm
from app.models import User, File, Chapter, Post, Formula
from datetime import datetime
from werkzeug.utils import secure_filename



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()



@app.route('/')
@app.route('/index')
#@login_required
def index():
#    user = {'username': 'miguel'}
    return render_template('index.html', title='Home', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',

                           form=form)
@app.route('/me')
def me():
    user = current_user
    return render_template('user.html', user=user)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    files = File.query.filter_by(user_id=user.id)
    return render_template('user.html', user=user, posts=posts, files=files)

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    user = current_user
    if request.method == 'POST':
        new_file = request.files['file']
#        if file and allowed_file(file.filename):
        if new_file:
            insecure_filename=new_file.filename
            filename = secure_filename(new_file.filename)
            upload_folder = app.config['UPLOAD_FOLDER']
            user_id = str(current_user.id)
            unique_part = str(uuid.uuid4())
            save_dir = os.path.join(upload_folder, user_id, unique_part)
            full_path = os.path.join(save_dir, filename)
            #filename = file.filename
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            new_file.save(os.path.join(save_dir, filename))
            url = ''.join(['/', full_path])
            file = File(filename=insecure_filename, url=url, user_id=current_user.id)
            db.session.add(file)
            db.session.commit()
#            url='/static/uploads/'user.id'/'
            return render_template('file_uploaded.html', filename=full_path, user=user)
        else:
            return render_template('file_upload.html', user=user)
    return render_template('file_upload.html', user=user)

@app.route('/chapters')
def chapters():
    user = current_user
    chapters = Chapter.query.filter_by().all()
    return render_template('chapters.html', user=user, chapters=chapters)

@app.route('/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter():
    user = current_user
    raw_files=File.query.filter_by()
    raw_formulas = Formula.query.filter_by()
    files=[]
    for file in raw_files:
        files.append((file.id, file.filename))
    formulas=[]
    for formula in raw_formulas:
        formulas.append((formula.id, formula.name))
    form = ChapterForm()
    form.files.choices=files
    form.files.default=''
    form.formulas.choices=formulas
    form.formulas.default=''
#    form.files.coerce='int'
    if form.validate_on_submit():
#        for item in form:
#            print(item.data)
#        print(form.files.data)
        chapter = Chapter(name=form.name.data, short_description=form.short_description.data, description=form.description.data, user_id=user.id)
        if form.files.data:
            for f in form.files.data:
                print(type(f))
                file=File.query.filter_by(id=int(f)).first_or_404()
                print(file)
                chapter.files.append(file)
        db.session.add(chapter)
        db.session.commit()
        print(form.files.data)
        return redirect(url_for('chapters'))
    return render_template('edit_chapter.html', title='Add chappter', user=user, form=form)

@app.route('/chapter/<id>')
@login_required
def chapter(id):
    user=current_user
    chapter = Chapter.query.filter_by(id=id).first_or_404()
    print(chapter)
#    files = File.query.filter_by(chapters=chapter.id).all()
    files = File.query.with_parent(chapter).all()
    title=chapter.name
    return render_template('chapter.html', title=title, chapter=chapter, files=files, user=user)

@app.route('/calc/', methods=['GET', 'POST'])
@login_required
def calc():
    user=current_user
    formulas = Formula.query.filter_by().all()
    print(formulas)
    if request.method == 'POST':
        data = request.form.get('output')
        f = Formula(name=request.form.get('name'), description=request.form.get('description'), formula=request.form.get('output'))
        db.session.add(f)
        db.session.commit()
    return render_template('formulas.html', user=user, formulas=formulas)

@app.route('/formula/edit/', methods=['GET', 'POST'], defaults={'id': None})
@app.route('/formula/edit/<id>', methods=['GET', 'POST'])
@login_required
def formula_edit(id):
    user=current_user
    if id:
        formula = Formula.query.filter_by(id=id).first_or_404()
        print("Formula: ", formula.formula)
    else:
        formula = None
    if request.method == 'POST':
        data = request.form.get('output')
        if id:
            f=Formula.query.filter_by(id=id).first_or_404()
            f.name = request.form.get('name')
            f.description = request.form.get('description')
            f.formula = request.form.get('output')
        else:
            f = Formula(name=request.form.get('name'), description=request.form.get('description'), formula=request.form.get('output'), id=request.form.get('id'))
        print(request.form.get('output'))
        print(f.formula)
        db.session.add(f)
        db.session.commit()
    return render_template('formula_editor.html', user=user, formula=formula)

@app.route('/formula/', defaults={'id': None})
@app.route('/formula/<id>', methods=['GET', 'PUSH'])
@login_required
def formula(id):
    user=current_user
    if id:
        formula = Formula.query.filter_by(id=id).first_or_404()
        return render_template('formula_editor.html', user=user, formula=formula)
    else:
        formulas = Formula.query.filter_by().all()
        return render_template('formulas.html', user=user, formulas=formulas)


@app.route('/mathlive.js')
def mathlive():
    return send_file('..\static\externals\mathlive\mathlive.js', mimetype='application/javascript')