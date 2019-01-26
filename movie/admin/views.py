from .import admin
from flask import render_template,redirect,session,url_for,flash,sessions,request

from functools import wraps

def admin_login_req(f):
    """
    登录装饰器
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function

from movie.admin.forms import LoginForm
from movie.models import Admin
@admin.route("/login/",methods=['POST','GET'])
def login():
    """
    后台登录
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误!")
            return redirect(url_for("admin.login"))
        # 如果是正确的，就要定义session的会话进行保存。
        session["admin"] = data["account"]
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html",form=form)
'''from werkzeug.security import generate_password_hash

    admin = Admin(
        name="mtianyan",
        pwd=generate_password_hash("123456")
'''


@admin.route("/logout/")
def logout():
    """
    后台注销登录
    """
    session.pop("admin", None)
    return redirect(url_for("admin.login"))


@admin.route("/")
def index():
    return render_template("admin/index.html")

@admin.route("/pwd/")
@admin_login_req
def pwd():
    """
    后台密码修改
    """
    return render_template("admin/pwd.html")

from .forms import TagForm
from movie.models import Tag
from movie import db
@admin.route("/tag/add/",methods=['POST','GET'])
@admin_login_req
def tag_add():
    """
    标签添加与编辑
    """
    form = TagForm()
    if form.validate_on_submit():
        data=form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash("标签已存在", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("标签添加成功", "ok")
    return render_template("admin/tag_add.html", form=form)


@admin.route("/tag/list/<int:page>/", methods= ["GET"])
@admin_login_req
def tag_list(page=None):
    """
    标签列表
    """
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
    Tag.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/tag_list.html", page_data=page_data)
@admin.route("/tag/del/<int:id>/", methods= ["GET"])
@admin_login_req
def tag_del(id=None):
    """
    标签删除
    """
    # filter_by在查不到或多个的时候并不会报错，get会报错。
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签<<{0}>>删除成功".format(tag.name), "ok")
    return redirect(url_for("admin.tag_list", page=1))

@admin.route("/tag/edit/<int:id>", methods=["GET", "POST"])
@admin_login_req
def tag_edit(id=None):
    """
    标签编辑
    """
    form = TagForm()
    form.submit.label.text = "编辑"
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data["name"]).count()
    # 说明已经有这个标签了,此时向添加一个与其他标签重名的标签。
        if tag.name != data["name"] and tag_count == 1:
            flash("标签已存在", "err")
            return redirect(url_for("admin.tag_edit", id=tag.id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("标签修改成功", "ok")
        redirect(url_for("admin.tag_edit", id=tag.id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)

from werkzeug.utils import secure_filename
import os,uuid
from datetime import datetime
# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename

from .forms import MovieForm
from flask import  current_app
from movie.models import Movie
@admin.route("/movie/add/", methods=["GET", "POST"])
def movie_add():
    """
    编辑电影页面
    """
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(current_app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(current_app.config["UP_DIR"])
            print('_______',current_app.config["UP_DIR"])
            import  sys, stat
            import platform
            #因为windows chmod方法第一次改变文件夹读写时会异常报错，所以修改为判断平台方式
            osName = platform.system()
            if (osName == 'Windows'):
                os.chmod(current_app.config["UP_DIR"], stat.S_IWRITE and stat.S_IREAD)
            else:
                os.chmod(current_app.config["UP_DIR"], "rw")



        url = change_filename(file_url)
        logo = change_filename(file_logo)
        # 保存
        form.url.data.save(os.path.join(current_app.config["UP_DIR"] , url))
        form.logo.data.save(os.path.join(current_app.config["UP_DIR"] , logo))
        # url,logo为上传视频,图片之后获取到的地址
        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            tag_id=int(data["tag_id"]),
            playnum=0,
            commentnum=0,
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！", "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/list/")
def movie_list():
    """
    电影列表页面
    """
    return render_template("admin/movie_list.html")

@admin.route("/preview/add/")
def preview_add():
    """
    上映预告添加
    """
    return render_template("admin/preview_add.html")


@admin.route("/preview/list/")
def preview_list():
    """
    上映预告列表
    """
    return render_template("admin/preview_list.html")

@admin.route("/user/list/")
def user_list():
    """
    会员列表
    """
    return render_template("admin/user_list.html")


@admin.route("/user/view/")
def user_view():
    """
    查看会员
    """
    return render_template("admin/user_view.html")

@admin.route("/comment/list/")
def comment_list():
    """
    评论列表
    """
    return render_template("admin/comment_list.html")

@admin.route("/moviecol/list/")
def moviecol_list():
    """
    电影收藏
    """
    return render_template("admin/moviecol_list.html")

@admin.route("/oplog/list/")
def oplog_list():
    """
    操作日志管理
    """
    return render_template("admin/oplog_list.html")


@admin.route("/adminloginlog/list/")
def adminloginlog_list():
    """
    管理员日志列表
    """
    return render_template("admin/adminloginlog_list.html")


@admin.route("/userloginlog/list/")
def userloginlog_list():
    """
    会员日志列表
    """
    return render_template("admin/userloginlog_list.html")

@admin.route("/auth/add/")
def auth_add():
    """
    添加权限
    """
    return render_template("admin/auth_add.html")


@admin.route("/auth/list/")
def auth_list():
    """
    权限列表
    """
    return render_template("admin/auth_list.html")

@admin.route("/role/add/")
def role_add():
    """
    添加角色
    """
    return render_template("admin/role_add.html")


@admin.route("/role/list/")
def role_list():
    """
    角色列表
    """
    return render_template("admin/role_list.html")

@admin.route("/admin/add/")
def admin_add():
    """
    添加管理员
    """
    return render_template("admin/admin_add.html")


@admin.route("/admin/list/")
def admin_list():
    """
    管理员列表
    """
    return render_template("admin/admin_list.html")