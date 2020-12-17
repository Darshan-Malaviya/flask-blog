from flask import Flask, render_template, request, session, redirect
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from werkzeug import *
from datetime import datetime
import json
import os
import math

# secure_filename




with open("G:\mysite\DarshanMalaviyaBlog\config.json", 'r') as c:
    params = json.load(c)["params"]






local_server = True
app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["UPLOAD_FOLDER"] = params["uploader_location"]

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)

mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)









class Tbl_message(db.Model):
    '''m_no	name	emails	phone_no	messages	date_time	'''
    m_no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable = False)
    emails = db.Column(db.String(30), nullable = False)
    phone_no = db.Column(db.Integer, nullable = False)
    messages = db.Column(db.String(120), nullable = False)
    date_time = db.Column(db.String(20), nullable = False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    sub_title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)










@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts) / int(params["no_posts"]))
    page = request.args.get("page")
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params["no_posts"]) : (page-1)*int(params["no_posts"])+int(params["no_posts"])]
        
    if (page == 1):
        prev = ""
        next = "/?page=" + str(page + 1)
    elif (page == last):
        prev = "/?page=" + str(page - 1)
        next = ""
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    return render_template("index.html", params=params, posts = posts, prev = prev, next = next)



@app.route("/about")
def about():
    return render_template("about.html", params=params)




@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ("user" in session and session["user"] == params['admin_user']):  #checking user is logged in or not ?
        if(request.method=='POST'):
            title = request.form.get('title')
            sub_title = request.form.get('sub_title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == "0":
                post = Posts(title = title, sub_title = sub_title, slug = slug, content = content, img_file = img_file, date = date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Posts.query.filter_by(sno = sno).first()
                post.title = title
                post.sub_title = sub_title
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)
                

        post = Posts.query.filter_by(sno = sno).first()
        return render_template("edit.html", params=params, post = post,sno = sno)










@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if ("user" in session and session["user"] == params['admin_user']):  #checking user is logged in or not ?
        post = Posts.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")











@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ("user" in session and session["user"] == params['admin_user']):  #checking user is logged in or not ?
        if(request.method=='POST'):
            f = request.files["file1"]
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(f.filename) ))
            return "Uploaded Successfuly"












@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    
    if ("user" in session and session["user"] == params['admin_user']): #checking user is logged in or not ?
        posts = Posts.query.all()
        return render_template("dashboard.html", params=params, posts = posts)


    if request.method == 'POST':
        username = request.form.get("uname")
        userpass = request.form.get("pass")
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session["user"] = username
            posts = Posts.query.all()
            return render_template("dashboard.html", params=params, posts = posts)
        else:
            return redirect("/dashboard")


    else:
        return render_template("login.html", params=params)







@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/dashboard")




@app.route("/post/<post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)








@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        '''m_no	name	emails	phone_no	messages	date_time	'''

        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Tbl_message(name=name, phone_no = phone, messages = message, date_time = datetime.now(),emails = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name + email,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = "new contact message from blog\nsender name : " + name +"\nmail : " + email + "\nmessage : " + message + "\ncontact no. : " + phone
                          )

    return render_template("contact.html", params=params)


app.run(debug=True)
