from articleapp.models import Users,Articles
from articleapp.forms import( RegisterForm,LoginForm,
                            ArticleForm,RequestPasswordResetForm,
                            UpdateArticleForm,ResetPasswordForm,UpdateProfileForm)
from slugify import slugify 

from werkzeug.utils import secure_filename
from datetime import datetime
import secrets
import os
from articleapp import app,db,mail
from passlib.hash import sha256_crypt
from functools import wraps
from flask import  (render_template,flash, redirect,
                    url_for,request, session, logging)
from flask_mail import Message


#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Unauthorized, Please login','danger')
            return redirect(url_for('login'))
    return wrap



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

# @app.route('/articles/<int:page_num>')
@app.route('/articles')

def articles(page_num=1):

        return render_template('articles.html')


    
@app.route('/article/<string:id>/<string:slug>')
# @is_logged_in
def article(id,slug):
   profile_img  = 'default.jpg'
   article = Articles.query.filter_by(id=id).first()
   user = Users.query.filter_by(username=article.author).first()
   if user:
       profile_img = user.profile_img 
       print("User_profile ",profile_img)    
   else:
       profile__img = 'default.jpg'
        
   image_file = url_for('static', filename='profile_pics/' +profile_img)
   return render_template('article.html',article=article,image_file=image_file)






####################MODIFIED CODE#############################
@app.route('/api/data')
def data():
    data = []
    for article in Articles.query.all():
        url = url_for('article',id=article.id,slug=article.slug)
        title = f"<a href='{url}'>{article.title}<a/>"

        data.append({
            'id':article.id,
            'title':title,
            'author':article.author,
            'updated_at':article.updated_at.strftime('%d-%b-%Y %H:%M %p'),

        })
    return {'data': data}

####################MODIFIED CODE#############################

@app.route('/register',methods=['GET','POST'])
def register():
    form  = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        #execute query
        db.session.add(Users(name=name,email=email,username=username,password=password))
        
        # commit changes
        db.session.commit()

        # flash message after successful registration
        flash('You are now registered and can log in','success')

        return redirect(url_for('login'))    
    
    return render_template('register.html',form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/update_profile/<string:id>',methods=['GET','POST'])
@app.route('/update_profile',methods=['GET','POST'])
@is_logged_in
def update_profile(id=None):
   
    id = session['id']
    user = Users.query.filter_by(id=id).first()
    
    form = UpdateProfileForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        print("THis is FOrm DATA :-",request.files['file'])
        fill = request.files['file']
        filename = secure_filename(fill.filename)
        if filename != '':
            profile_file = save_picture(fill)
            user.profile_img = profile_file
            
        
        user.name = form.name.data
        user.email = form.email.data
        user.username = form.username.data
        db.session.commit()

        #execute query
        Articles.query.filter_by(author=user.username).update(dict(author=user.username))
      
        # commit changes
        db.session.commit()

        # flash message after successful registration
        flash('Profile Updated Successfully','success')

        return redirect(url_for('dashboard'))

    elif form.is_submitted() == True: 
        if user.username != form.username.data and Users.query.filter_by(username=form.username.data).first() is not None:
            flash(f'username {form.username.data}  already exists','danger')
            return redirect(url_for('update_profile'))
        elif Users.query.filter_by(email=form.email.data).first() is not None:
            flash(f'email {form.email.data}  already exists','danger')
            return redirect(url_for('update_profile'))
        
    
    image_file = url_for('static', filename='profile_pics/' + user.profile_img)
    form = UpdateProfileForm(request.form)
    form.name.data = user.name
    form.email.data = user.email
    form.username.data = user.username
    form.profile_img.data = user.profile_img
    return render_template('update_profile.html',form=form,image_file=image_file)

        
   



@app.route('/login',methods=['GET','POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        
        username = form.username.data
        password_candidate = form.password.data
        print(username)
        print(password_candidate)

        #getting user
        result = Users.query.filter_by(username=username).all()

        # db.session.row_factory = dict_factory
            
        if len(result) > 0:
            # get stored hash
            password = result[0].password

            # compare passwords
            if sha256_crypt.verify(password_candidate,password):
                # app.logger.info('PASSWORD_MATCHED')
                session['logged_in'] = True
                session['username'] = username
                session['id'] = result[0].id
                flash("You are now logged in",'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html',error=error,form=form)

        else:
            error  = 'Username not found'
            return render_template('login.html',error=error,form=form)


    return render_template('login.html',form=form)




@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash("You are not logged out","success")
    return redirect(url_for('login'))


@app.route('/dashboard/<int:page_num>')
@app.route('/dashboard')
@is_logged_in
def dashboard(page_num=1):

    username = session['username']
    articles = Articles.query.filter_by(author=username).order_by(Articles.id.desc()).paginate(per_page=5,page=page_num,error_out=True)
    # print("Type of Article is ",type(articles))

    if articles.total > 0:
      return render_template('dashboard.html',articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html',articles=articles)




# Add Article
@app.route('/add_article',methods=['GET','POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        username = session['username']
        #execute query
        article = Articles(title=title,body=body,author=username)
        db.session.add(article)
        print("Article Slug",article.slug)
        #commit changes
        db.session.commit()

        flash('Article Created','success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html',form=form)


# Edit Article
@app.route('/edit_article/<string:id>/<string:slug>',methods=['GET','POST'])
@is_logged_in
def edit_article(id,slug):
    # get article by id
    article = Articles.query.filter_by(id=id).first()
    
    # print(type(article))
    # get form
    form = UpdateArticleForm(request.form)

    # populate article form fields
    form.title.data = article.title
    form.body.data = article.body
    
    
    if request.method == "POST" and form.validate():
        
        print("In Post")
        title = request.form['title']
        body = request.form['body']
        username = session['username']

        if article.slug != slugify(title) and Articles.query.filter_by(slug=slugify(title)).first():
            flash(f'Article with title: "{title}" already exists','danger')
            return redirect(url_for('edit_article',id=id,slug=slug))

        # execute query
        Articles.query.filter_by(id=id).update({'title':title,'body':body,'updated_at':datetime.now()})

        # commit changes
        db.session.commit()

        flash('Article Updated','success')
        print("Addded")
        return redirect(url_for('dashboard'))
    
    return render_template('edit_article.html',form=form)


# Delete Article
@app.route('/delete_article/<string:id>/<string:slug>',methods=['POST'])
@is_logged_in
def delete_article(id,slug):
    # delete article with id
    Articles.query.filter_by(id=id).delete()

    # commit changes
    db.session.commit()

    #flash message
    flash('Article Deleted','success')

    return redirect(url_for('dashboard'))




def send_reset_email(user):
    token = user.get_reset_token()
    message = Message('Password Reset Request',
                sender='noreply@demo.com',
                recipients=[user.email])
    message.body = f'''<i><h3>To reset your password, visit the following link:</i></h3>
{url_for('reset_password',token=token,_external=True)}
If you did not make this request ,then simply ignore this email,and  no changes will be made.
'''
    mail.send(message)


@app.route('/request_password_reset',methods=['GET','POST'])
def request_password_reset():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    form = RequestPasswordResetForm(request.form)
    if form.validate_on_submit():
       user = Users.query.filter_by(email=form.email.data).first()
       send_reset_email(user) 
       flash('Password Reset link sent to mail','success')

       return redirect(url_for('login'))

    return render_template('request_password_reset.html',form=form)
 


@app.route('/reset_password/<string:token>',methods=['GET','POST'])
def reset_password(token):
    if 'username' in session:
        return redirect(url_for('dashboard'))
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('request_password_reset'))

    form = ResetPasswordForm()  
    if form.validate_on_submit():
        hashed_password = sha256_crypt.hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated','success')
        return redirect(url_for('login'))
    return render_template('reset_password.html',form=form)
