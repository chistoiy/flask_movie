from flask import request,session,render_template,redirect,url_for
from . import home

@home.route('/',methods=["GET"])
def index():
    return render_template('/home/index.html')

#登录
@home.route("/login/")
def login():
    return render_template("home/login.html")

#退出
@home.route("/logout/")
def logout():
    return redirect(url_for('home.login'))

# 会员注册
@home.route("/register/")
def register():
    return render_template("home/register.html")

@home.route("/user/")
def user():
    """
    用户中心
    """
    return render_template("home/user.html")


@home.route("/pwd/")
def pwd():
    """
    修改密码
    """
    return render_template("home/pwd.html")


@home.route("/comments/")
def comments():
    """
    评论记录
    """
    return render_template("home/comments.html")


@home.route("/loginlog/")
def loginlog():
    """
    登录日志
    """
    return render_template("home/loginlog.html")


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

