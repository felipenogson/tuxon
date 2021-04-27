import os
import secrets
from webapp import app, db
from webapp.models import OAuth, User, Postcoin, Tuxcoin
from flask import render_template, flash, redirect, url_for, request, send_from_directory, abort, make_response, session
from werkzeug.utils import secure_filename
import pdfkit

from flask_login import current_user, login_user, logout_user, login_required

from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage

# esta linea es temporal para probar el login sin el https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

google_blueprint = make_google_blueprint(
    client_id= app.config['GOOGLE_ID'],
    client_secret= app.config['GOOGLE_SECRET'],
    scope = ['https://www.googleapis.com/auth/userinfo.email',
           'https://www.googleapis.com/auth/userinfo.profile', 'openid'], 
    offline=True,
    reprompt_consent=True,
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
    )

app.register_blueprint(google_blueprint)

@app.route('/')
def index():
    google_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    if current_user.is_authenticated and google.authorized:
        google_data = google.get(user_info_endpoint).json()
    postcoins = Postcoin.query.all()
    return render_template('index.html', title="Easter Egg Hunting",  google_data=google_data, posts=postcoins)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/post', methods=['POST', 'GET'])
@login_required
def post():
    user_info_endpoint = '/oauth2/v2/userinfo'
    google_data = google.get(user_info_endpoint).json()
    if request.method != 'POST':
        return render_template('post.html', title="Hide an egg!", google_data=google_data)
    else:
        # Codigo para subir las fotos
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(photo_path)
            
            coinToken = secrets.token_urlsafe()
            post = Postcoin(
                    title = request.form['title'], 
                    description = request.form.get('description'),
                    #  lat =
                    #  lng =
                    token = coinToken,
                    # Ojo aqui, cambiar el protocolo de http a https para subir a produccion
                    url = request.url_root[:-1] + url_for('found', token=coinToken),
                    img = filename,
                    posted = True,
                    user = current_user,
                )
            db.session.add(post)
            db.session.commit()
            flash('Your egg has been posted!', 'success')        
            return redirect(url_for('index'))

@app.route('/view/<id>')
@login_required
def view(id):
    user_info_endpoint = '/oauth2/v2/userinfo'
    google_data = google.get(user_info_endpoint).json()
    post = Postcoin.query.filter_by(id=id).first()
    if post == None:
        return abort(404)
    return render_template('view.html', title="View", google_data=google_data, post=post) 

@app.route('/qr/<token>', methods=['GET','POST'])
@login_required 
def qr(token):
    post = Postcoin.query.filter_by(token = token).first()

    if post:
        rendered = render_template('pdf_template.html', title=post.title, post=post)
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        pdf = pdfkit.from_string(rendered, False, configuration=config)

        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename={post.title}.pdf'
        return response
    else: 
        # rendered = render_template('pdf_template.html', name='QR Code', )
        return abort(404) 

@app.route('/found/<token>')
@login_required
def found(token):
   post = Postcoin.query.filter_by(token=token).first()
   tuxcoin = Tuxcoin.query.filter_by(user=current_user).filter_by(post=post).first()

   if not post:
       return "I don't know how do you get this far"
   elif tuxcoin:
       flash("You already have found this place before", 'warning')
       return redirect(url_for('view', id=tuxcoin.post.id))
   else:
       tuxcoin = Tuxcoin(
           user = current_user,
           post= post
       )
       db.session.add(tuxcoin)
       db.session.commit()
       flash(f'Congratulations! You just found {post.title}', 'success')
       if current_user.tuxcoins.count() >= 5:
            google_data = None
            user_info_endpoint = '/oauth2/v2/userinfo'
            posts = Tuxcoin.query.filter_by(user_id=current_user.id).all()
            if current_user.is_authenticated and google.authorized:
                google_data = google.get(user_info_endpoint).json()
            return render_template('winner.html', google_data=google_data, posts=posts)

       return redirect(url_for('view', id=post.id ))

@app.route('/tuxcoins')
@login_required
def tuxcoins():
    google_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    if current_user.is_authenticated and google.authorized:
        google_data = google.get(user_info_endpoint).json()
    posts = Tuxcoin.query.filter_by(user_id=current_user.id).all()
    return render_template('tuxcoins.html', posts=posts, google_data=google_data)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route('/photo/<filename>')
def photo(filename):
    ''' This view is for dispatch photos to the templates '''
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    resp = blueprint.session.get('/oauth2/v2/userinfo')
    user_info = resp.json()
    user_id = str(user_info['id'])
    oauth = OAuth.query.filter_by(provider=blueprint.name, provider_user_id=user_id).first()

    if not oauth:
        oauth = OAuth(provider=blueprint.name,
                provider_user_id=user_id,
                token=token)
    else:
        oauth.token = token
        db.session.add(oauth)
        db.session.commit()
        login_user(oauth.user) 

    if not oauth.user:
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(email=user_info['email'],
                        name=user_info['name'])
        db.session.add(user)
        oauth.user = user
        db.session.add(oauth)
        db.session.commit() 
        login_user(user)

    next = session.pop('next', url_for('index'))
    return redirect(next)
    return False