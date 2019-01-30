from flask import request,session,render_template,redirect,url_for,flash
from . import home

@home.route('/',methods=["GET"])
def index():
    return render_template('/home/index.html')
from functools import wraps
def user_login_req(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#登录
from movie.models import Userlog
from .forms import LoginForm
@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if not user or not user.check_pwd(data["pwd"]):
            flash("账号或密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = user.name
        session["user_id"] = user.id
        userlog = Userlog(
        user_id=user.id,
        ip=request.remote_addr
        )
        db.session.add(userlog)
        db.session.commit()
        return redirect(url_for("home.user"))
    return render_template("home/login.html", form=form)

#退出
@home.route("/logout/")
def logout():
    """
    退出登录
    """
    # 重定向到home模块下的登录。
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for('home.login'))

# 会员注册
from .forms import  RegistForm
from movie.models import User
import uuid
from movie import db
from werkzeug.security import  generate_password_hash
@home.route("/register/", methods=["GET", "POST"])
def register():
    """
    会员注册
    """
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
        name=data["name"],
        email=data["email"],
        phone=data["phone"],
        pwd=generate_password_hash(data["pwd"]),
        uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("注册成功！", "ok")
    return render_template("home/register.html", form=form)
#@user_login_req
from .forms import UserdetailForm
import os
from flask import current_app
from movie.util.toos import change_filename,sel_chmod
from werkzeug.utils import secure_filename
@home.route("/user/", methods=["GET", "POST"])
def user():
    """
    用户中心个人资料
    """
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    #form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info

    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            #print(type(form.face.data))

            # file_face = secure_filename(form.face.data)
            if not os.path.exists(current_app.config["FC_DIR"]):
                # os.makedirs(current_app.config["FC_DIR"])
                # os.chmod(current_app.config["FC_DIR"], "rw")
                sel_chmod()
            user.face = change_filename(file_face)
            form.face.data.save(os.path.join(current_app.config["FC_DIR"], user.face))

        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("昵称已经存在！", "err")
            return redirect(url_for("home.user"))

        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("邮箱已经存在！", "err")
            return redirect(url_for("home.user"))

        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("手机号码已经存在！", "err")
            return redirect(url_for("home.user"))

        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


from .forms import PwdForm
@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    """
    修改密码
    """
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        if not user.check_pwd(data["old_pwd"]):
            flash("旧密码错误！", "err")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('home.logout'))
    return render_template("home/pwd.html", form=form)


@home.route("/comments/")
def comments():
    """
    评论记录
    """
    return render_template("home/comments.html")


@home.route("/loginlog/<int:page>/", methods=["GET"])
@user_login_req
def loginlog(page=None):
    """
    会员登录日志
    """
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
    user_id=int(session["user_id"])
    ).order_by(
    Userlog.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("home/loginlog.html", page_data=page_data)

@home.route("/moviecol/")
def moviecol():
    """
    收藏电影
    """
    return render_template("home/moviecol.html")

'''
# 列表
@home.route("/")
def index():
    return render_template("home/index.html")
'''
# 动画
@home.route("/animation/")
def animation():
    return render_template("home/animation.html")

@home.route("/search/")
def search():
    """
    搜索
    """
    return render_template("home/search.html")

@home.route("/play/")
def play():
    """
    播放
    """
    return render_template("home/play.html")

