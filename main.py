############################ IMPORT #################################
#pip install flask
#pip install Flask-SQLAlchemy
from flask import Flask, render_template, redirect, request, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_restful import Resource,Api,fields,marshal_with,reqparse
import os
import datetime
import re


########################### CONFIGURATION ############################

app = Flask(__name__)
app.config[
  'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database_bloglite_bk4.sqlite3'
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key='bloglitesecretkey'
api = Api(app)

db = SQLAlchemy(app)  #creating a model db

########################### MODELS ###############################

class Userdetails(db.Model):
  first_name = db.Column(db.String, nullable=False)
  middle_name = db.Column(db.String, nullable=True)
  last_name = db.Column(db.String, nullable=False)
  dob = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False, unique=True)
  username = db.Column(db.String,
                       nullable=False,
                       primary_key=True,
                       unique=True)
  password = db.Column(db.String, unique=True, nullable=False)


class Posts(db.Model):
  post_id = db.Column(db.Integer,
                      nullable=False,
                      unique=True,
                      primary_key=True)
  user = db.Column(db.String,
                   db.ForeignKey("userdetails.username"),
                   nullable=False)
  title = db.Column(db.String, nullable=False)
  description = db.Column(db.String, nullable=False)
  content = db.Column(db.String, nullable=False)
  date = db.Column(db.String, nullable=False)


class Image(db.Model):
  image_id = db.Column(db.Integer,
                       nullable=False,
                       unique=True,
                       primary_key=True)
  post_id = db.Column(db.Integer,
                      db.ForeignKey("posts.post_id"),
                      nullable=False)
  img_path = db.Column(db.String, nullable=False)


class Follow(db.Model):
  user = db.Column(db.String,
                   db.ForeignKey("userdetails.username"),
                   nullable=False,
                   primary_key=True)
  following = db.Column(db.String,
                        db.ForeignKey("userdetails.username"),
                        nullable=False,
                        primary_key=True)

class Like(db.Model):
  p_id=db.Column(db.Integer,db.ForeignKey("userdetails.username"),nullable=False,primary_key=True)
  by=db.Column(db.String,db.ForeignKey("posts.post_id"),nullable=False,primary_key=True)


###################################### Data Validation Fns #############################
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validemail(email):
  valid_email = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
  if re.match(valid_email,email):
    return True
  return False

########################### MODELS-API ##############################
create_post_parser=reqparse.RequestParser()
create_post_parser.add_argument('title', type=str, required=True, help='Title of the post')
create_post_parser.add_argument('description', type=str, required=True, help='Description of the post')
create_post_parser.add_argument('content', type=str, required=True, help='Content of the post')
create_post_parser.add_argument('date', type=str, required=True, help='Date of the post')
create_post_parser.add_argument('username', type=str, required=True, help='Username of the user')

create_image_parser=reqparse.RequestParser()
create_image_parser.add_argument('img_path', type=str, required=True, help='Path of the image')

class PostAPI(Resource):
  def get(self,user_name,p_id):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
    else:
      post = Posts.query.filter_by(post_id=p_id,user=user_name).first()  
      if post is None:
        return {'Error':'Post not found 404'}
      else:
        return {'user_name':user_name,'post_id':p_id,'post_title':post.title,'post_description':post.description,'post_content':post.content,'post_date':post.date}
        
  def post(self,user_name):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
    data=request.get_json()
    post = Posts(user=user_name,title=data.get("title"),
                description=data.get("description"),
                content=data.get("content"),
                date=datetime.datetime.now())
    db.session.add(post)
    db.session.commit()
    return      {'user_name':user_name,'post_id':post.post_id,'post_title':post.title,'post_description':post.description,'post_content':post.content,'post_date':post.date}     
    
  def put(self,user_name,p_id):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
      
    data=request.get_json()
    post = Posts.query.filter_by(post_id=p_id).first()
    if post is None:
      return {'Error':'Post not found 404'}
      
    post.title = data.get('title')
    post.description = data.get('description')
    post.content = data.get('content')
    post.date = datetime.datetime.now()
    db.session.add(post)
    db.session.commit()
    return {'user_name':user_name, 'post_id':p_id,'Edit':'Success'}
    
  def delete(self,user_name,p_id):          
    user = Userdetails.query.filter_by(username=user_name).first()
    
    if user is None:
      return {'Error':'User not found 404'}
      
    post = Posts.query.filter_by(post_id=p_id).first()
               
    if post is None:
      return {'Error':'Post not found 404'}
      
    db.session.delete(post)
               
    db.session.commit()
               
    return {'Delete':'Success'}
api.add_resource(PostAPI, '/api/<user_name>/<p_id>','/api/<user_name>')

class UserAPI(Resource):
  def get(self,user_name):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
      
    return {'user_username':user.username}

  def post(self,user_name):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User Exists'}
      
    data=request.get_json()
    user = Userdetails(username=data.get('username'),
                       password=data.get('password'),
                       email=data.get('email'),
                       first_name=data.get('first_name'),
                                      middle_name=data.get('middle_name'),
                                      last_name=data.get('last_name'),dob=data.get('dob'))
    db.session.add(user)
    db.session.commit()
    return {'user_username':user.username,'New User Added':'Success'}
    
  def put(self,user_name):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
      
    data=request.get_json()
    user.username = data.get('username')
    user.password = data.get('password')
    user.email = data.get('email')
    user.first_name = data.get('first_name')
    user.last_name= data.get('last_name')
    user.middle_name=data.get('middle_name')
    user.dob=data.get('dob')
    db.session.add(user)
    db.session.commit()
    return {'user_name':user.username,'Edit':'Success'}
    
  def delete(self,user_name):
    user = Userdetails.query.filter_by(username=user_name).first()
    if user is None:
      return {'Error':'User not found 404'}
      
    db.session.delete(user)
               
    db.session.commit()
               
    return {'Delete':'Success'}
    
api.add_resource(UserAPI, '/api/user/<user_name>')


########################### APP ROUTE FNS ###############################
########################### WELCOME ###################################

@app.route('/')
def home():
  db.create_all()
  return render_template('welcome.html')

########################### LOGIN ###################################
  
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template('login.html')
  
  else:
    global user_name
    user_name = request.form["username"]
    p = Userdetails.query.filter_by(username=request.form["username"]).first()
  
    if p == None:
      return redirect('/registration')
    
    else:
      pp = request.form["password"]
      print(p)
    
      if p.password == pp:
        #return redirect('/'+user_name+'/profile')
        return redirect('/' + user_name + '/home')
      
      else:
        message='User Credentials are Wrong.'
        return render_template('login.html',message=message)

########################### SIGNUP  ##############################

@app.route('/registration', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')
  
  else:
    exist = Userdetails.query.filter_by(
      username=request.form["username"]).first()
  
    if exist == None:
    
      if validemail(request.form['email']):
      
        if request.form["password"] == request.form["repassword"]:
          exist = Userdetails.query.filter_by(email=request.form["email"]).first()
        
          if exist == None:
            First_Name = request.form["first_name"]
            Middle_Name = request.form["middle_name"]
            Last_Name = request.form["last_name"]
            DOB = request.form["dob"]
            Email = request.form["email"]
            Username = request.form["username"]
            Password = request.form["password"]
            UserDet = Userdetails(first_name=First_Name,
                                  middle_name=Middle_Name,
                                  last_name=Last_Name,
                                  dob=DOB,
                                  email=Email,
                                  username=Username,
                                  password=Password)
            db.session.add(UserDet)
            db.create_all()
            db.session.commit()
            return redirect('/' + Username + '/profile')
          else:
            message="Use another email-id which has not been used "
            return render_template('register.html',message=message)
        else:
          message="Password and Re-Entered Password Did Not Match "
          return render_template('register.html',message=message)
      
      else:       
        message="Invalid Email ID "
        return render_template('register.html',message=message)
    
    else:
      message="Username already in use. Try another username. "
      return render_template('register.html',message=message)



########################### HOME ###################################
      
@app.route('/<user_name>/home', methods=['GET', 'POST','DELETE'])
def homepage(user_name):
  
  if request.method == 'GET':
    db.create_all()
    q = request.args.get('q')
    pos = Posts.query.all()
    P = []
    I=None
  
    for i in pos:
      if i.user != user_name:
        d=i.date
        I=Image.query.filter_by(post_id=i.post_id).first()
        L=Like.query.filter_by(p_id=i.post_id,by=user_name).first()
      
        if I:
        
          if L:
            P.append(['get',
                      'liked',
                      i.user,
                      i.title,
                      i.content,
                      d[0:19],
                      i.post_id,
                      '/static/'+I.img_path])
          
          else:
            P.append(['post',
                      'notliked',
                      i.user, 
                      i.title,
                      i.content,
                      d[0:19],
                      i.post_id,
                      '/static/'+I.img_path])
        
        else:
          
          if L:
            P.append(['get',
                      'liked',
                      i.user, 
                      i.title,
                      i.content,
                      d[0:19],
                      i.post_id])
          
          else:
            P.append(['post',
                      'notliked',
                      i.user,
                      i.title,
                      i.content,
                      d[0:19],
                      i.post_id])
    
    if q:
      uu = user_name
      u = Userdetails.query.filter(Userdetails.username.contains(q))
      su = []
      for i in u:
        if i.username!=user_name:
          su.append([i.username, i.first_name])
      return render_template('home.html',
                             results=su,
                             uu=uu,
                             user_name=user_name)
    
    else:
      return render_template('home0.html', P=P, user_name=user_name,I=I)

############################# LIKE #####################################
@app.route('/<user_name>/<post_id>/like',methods=['GET','POST'])
def like(post_id,user_name):
  Li=Like.query.filter_by(p_id=post_id,by=user_name).first()
  L=Like(p_id=post_id,by=user_name)
  
  if request.method=='GET':
    l=request.args.get('l')
    
    if l:
        db.session.delete(Li)
        db.session.commit()
        return redirect('/'+user_name+'/home')

  else:
    db.session.add(L)
    db.create_all()
    db.session.commit()
    return redirect('/'+user_name+'/home')
    
      

########################### PROFILE OF #################################
      
@app.route('/<user_name>/profileof/<user__name>')
def profileof(user__name, user_name):
  db.create_all()
  q = request.args.get('followb')
  f1 = Follow.query.filter_by(user=user__name).count()
  f2 = Follow.query.filter_by(following=user__name).count()
  f3 = Posts.query.filter_by(user=user__name).count()
  U = Userdetails.query.filter_by(username=user__name).first()
  F1 = U.username
  F2 = U.first_name + ' ' + U.last_name
  F3 = U.dob
  F4 = U.email
  F = [F1, F2, F3, F4]
  f = [f1, f2, f3]
  b = Posts.query.filter_by(user=user__name).all()
  blogs = []
  
  for i in b:
    blogs.append([i.title, i.content,i.date[0:19]])
  fo = Follow.query.filter_by(user=user_name).all()
  foo = []
  
  for i in fo:
    foo.append(i.following)
  
  if user__name in foo:
    fl = "Unfollow"
  
  else:
    fl = "Follow"
  
  if not q:
    return render_template('profileof.html', f=f, blogs=blogs, fl=fl, F=F,user_name=user_name)
  
  else:
    
    if q == "Follow":
      ff = Follow(user=user_name, following=user__name)
      db.session.add(ff)
      db.session.commit()
      db.create_all()
      return redirect("/" + user_name + '/profile')
    
    else:
      ffff = Follow.query.filter_by(user=user_name,
                                    following=user__name).first()
      db.session.delete(ffff)
      db.session.commit()
      return redirect("/" + user_name + '/profile')

########################### PROFILE ###################################
      
@app.route('/<user_name>/profile', methods=['GET', 'POST'])
def profile(user_name):
  db.create_all()
  f1 = Follow.query.filter_by(user=user_name).count()
  f2 = Follow.query.filter_by(following=user_name).count()
  f3 = Posts.query.filter_by(user=user_name).count()
  f = [f1, f2, f3]
  U = Userdetails.query.filter_by(username=user_name).first()
  F1 = U.username
  F2 = U.first_name + ' ' + U.last_name
  F3 = U.dob
  F4 = U.email
  F = [F1, F2, F3, F4]
  
  if request.method == 'GET':
    q = request.args.get('dub')
  
    if q:
      return redirect("/" + "/edit")
    
    else:
      return render_template('profile.html', f=f, user_name=user_name, F=F)
  
  else:
    Title = request.form["title"]
    Desc = request.form["description"]
    Content = request.form["content"]
    Date = datetime.datetime.now()
    pic = request.files["pic"]
  
    if pic:
      filename = secure_filename(pic.filename)
      pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    P = Posts(user=user_name,
              title=Title,
              description=Desc,
              content=Content,
              date=Date)
    db.session.add(P)
    db.session.commit()
    P=Posts.query.filter_by(user=user_name,
                            description=Desc,
                            title=Title,
                            date=Date).first()
    p=P.post_id
    
    if 'jpg' in pic.filename or 'png' in pic.filename or 'jpeg' in pic.filename:
      I=Image(post_id=p,img_path=filename)
      db.session.add(I)
      db.create_all()
      db.session.commit()
    return redirect("/" + user_name + '/profile')

########################### EDIT ###################################
    
@app.route('/<user_name>/<p_id>/edit', methods=['GET', 'POST', 'DELETE'])
def edit(user_name, p_id):
  post = Posts.query.filter_by(post_id=p_id).first()
  Img=Image.query.filter_by(post_id=p_id).first()
  
  if request.method == 'GET':
    Title = post.title
    Desc = post.description
    Content = post.content
    
    if Img:
      I=Img.img_path
    else:
      I=""
    i='/static/'+I
    return render_template('blogupdate.html',
                           Title=Title,
                           Desc=Desc,
                           Content=Content,
                           user_name=user_name,i=i)
  else:
    Title = post.title
    Desc = post.description
    Content = post.content
    Date = datetime.datetime.now()
    #Image=request.form["pic"]
    #Image_D=request.form["pic_desc"]
    TTitle = request.form['title']
    DDesc = request.form['description']
    CContent = request.form['content']
    post = Posts.query.filter_by(post_id=p_id).first()
    post.title = TTitle
    post.description = DDesc
    post.content = CContent
    PP = Posts(user=user_name,
               title=TTitle,
               description=
               DDesc,
               content=CContent,
               date=Date)
    db.create_all()
    #db.session.delete(P)
    #db.session.add(PP)
    PP.verified = True
    pic = request.files["pic"]
    
    if pic:
      i=Image.query.filter_by(post_id=p_id).first()
      filename = secure_filename(pic.filename)
      pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      i.img_path=filename
      II=Image(post_id=p_id,img_path=filename)
      II.verified = True
    db.session.commit()
    return redirect("/" + user_name + '/profile')

########################### DELETE ###################################
@app.route('/<user_name>/<p_id>/delete')
def delete_post(user_name, p_id):
  post = Posts.query.filter_by(post_id=p_id).first()
  Img=Image.query.filter_by(post_id=p_id).first()
  q = request.args.get("B")
  
  if not q:
    Title = post.title
    Desc = post.description
    Content = post.content
    
    if Img:
      return render_template('blogdelete.html',
                            Title=Title,
                            Desc=Desc,
                            Content=Content,
                            user_name=user_name,i='/static/'+Img.img_path)
    else:
      return render_template('blogdelete.html',
                            Title=Title,
                            Desc=Desc,
                            Content=Content,
                            user_name=user_name)
  else:
    db.session.delete(post)
    db.session.commit()
    
    if Img:
      db.session.delete(Img)
      db.session.commit()
    return redirect("/" + user_name + '/profile')

    F=Like.query.filter_by(post_id=p_id).first()
    if F:
      db.session.delete(F)
      db.session.commit()
    return redirect("/" + user_name + '/profile')

####################### Follow #########################3333
@app.route('/<user_name>/following', methods=['GET'])
def follow(user_name):
  follow = Follow.query.filter_by(user=user_name).all()
  F = []
  
  if request.method == 'GET':
    for i in follow:
      following = Userdetails.query.filter_by(username=i.following).first()
      F.append([following.username, following.first_name])
    return render_template('following.html', F=F, user_name=user_name)

########################### BLOGS PAGE #################################
@app.route('/<user_name>/blogs')
def myblogs(user_name):
  db.create_all()
  f1 = Follow.query.filter_by(user=user_name).count()
  f2 = Follow.query.filter_by(following=user_name).count()
  f3 = Posts.query.filter_by(user=user_name).count()
  U = Userdetails.query.filter_by(username=user_name).first()
  F1 = U.username
  F2 = U.first_name + ' ' + U.last_name
  F3 = U.dob
  F4 = U.email
  F = [F1, F2, F3, F4]
  f = [f1, f2, f3]
  b = Posts.query.filter_by(user=user_name).all()
  P = []
  for i in b:
    Img=Image.query.filter_by(post_id=i.post_id).first()
    if Img:
      P.append([i.title, 
                i.content,
                i.description, 
                i.post_id,
                i.date[0:19],
                '/static/'+Img.img_path])
    
    else:
      P.append([i.title, 
                i.content, 
                i.description, 
                i.post_id,
                i.date[0:19]])
      
  return render_template('myblogs.html', f=f, P=P, F=F, user_name=user_name)


################################# FAV ############################
@app.route('/<user_name>/favourites', methods=['GET', 'POST'])
def fav(user_name):
  L=Like.query.filter_by(by=user_name).all()
  POSTS=[]
  
  for i in L:
    P=Posts.query.filter_by(post_id=i.p_id).all()
    for j in P:
      I=Image.query.filter_by(post_id=j.post_id).first()
      if I:
        POSTS.append([j.user, 
                      j.title, 
                      j.content,
                      j.date[0:19],
                      j.post_id,
                      '/static/'+I.img_path])
      
      else:
        POSTS.append([j.user, 
                      j.title, 
                      j.content,
                      j.date[0:19],
                      j.post_id])
  
  return render_template('favourites.html',POSTS=POSTS,user_name=user_name)


########################### RUN ###################################

if __name__ == '__main__':
  #app.run(debug=True)
  app.debug=True
  app.run(host='0.0.0.0', port='8080')