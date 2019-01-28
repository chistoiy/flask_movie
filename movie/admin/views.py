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

from flask import current_app,g
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
        #g.logo = os.path.join(current_app.static_folder, 'admin','dist','img','user1-160x160.jpg')
        #print(g.logo)
        #g.logo = 'user1-160x160.jpg'
        from movie import create_app
        print('aaa',dir(create_app))
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误!")
            return redirect(url_for("admin.login"))
        # 如果是正确的，就要定义session的会话进行保存。
        session["admin"] = data["account"]
        session['logo']='user2-160x160.jpg'

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

from .forms import PwdForm
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    """
    后台密码修改
    """
    form = PwdForm()
    # 有下面这两句才有错误信息提示
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for('admin.logout'))
    return render_template("admin/pwd.html",form=form)

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
            #print('_______',current_app.config["UP_DIR"])
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


@admin.route("/movie/list/<int:page>",methods=['GET','POST'])
def movie_list(page=None):
    """
    电影列表页面
    """
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(Tag.id == Movie.tag_id).order_by(Movie.addtime.desc()).paginate(page = page,per_page=1)

    return render_template("admin/movie_list.html",page_data=page_data)

@admin.route("/movie/del/<int:id>",methods=['GET'])
def movie_del(id=None):
    """
    电影列表页面
    """
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash('电源删除成功','ok')

    return redirect(url_for("admin.movie_list",page=1))

@admin.route("/movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    """
    编辑电影页面
    """
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        # 存在一步名字叫这个的电影，有可能是它自己，也有可能是同名。如果是现在的movie不等于要提交的数据中title。那么说明有两个。
        if movie_count == 1 and movie.title != data["title"]:
            flash("片名已经存在！", "err")
            return redirect(url_for('admin.movie_edit', id=id))
        # 创建目录
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
            #os.chmod(current_app.config["UP_DIR"], "rw")
            import platform,stat
            osName = platform.system()
            if (osName == 'Windows'):
                os.chmod(current_app.config["UP_DIR"], stat.S_IWRITE and stat.S_IREAD)
            else:
                os.chmod(current_app.config["UP_DIR"], "rw")
        # 上传视频
        if form.url.data != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(os.path.join(current_app.config["UP_DIR"],movie.url))
        # 上传图片
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(os.path.join(current_app.config["UP_DIR"],movie.logo))

        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.info = data["info"]
        movie.title = data["title"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("修改电影成功！", "ok")
        return redirect(url_for('admin.movie_edit', id=movie.id))

    return render_template("admin/movie_edit.html", form=form,movie=movie)

from .forms import PreviewForm
from movie.models import Preview
@admin.route("/preview/add/",methods=['GET','POST'])
def preview_add():
    """
    上映预告添加
    """
    form = PreviewForm()
    if form.validate_on_submit():
        data= form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(current_app.config["UP_DIR"]):
            os.makedirs(current_app.config["UP_DIR"])
        #os.chmod(app.config["UP_DIR"], "rw")
            import platform, stat
            osName = platform.system()
            if (osName == 'Windows'):
                os.chmod(current_app.config["UP_DIR"], stat.S_IWRITE and stat.S_IREAD)
            else:
                os.chmod(current_app.config["UP_DIR"], "rw")
        logo = change_filename(file_logo)
        form.logo.data.save(os.path.join(current_app.config["UP_DIR"] , logo))
        preview = Preview(
            title=data["title"],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功！", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template("admin/preview_add.html",form=form)


@admin.route("/preview/list/<int:page>/", methods =["GET"])
@admin_login_req
def preview_list(page=None):
    """
    上映预告列表
    """
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
    Preview.addtime.desc()
    ).paginate(page=page, per_page=1)
    return render_template("admin/preview_list.html", page_data=page_data)

@admin.route("/preview/del/<int:id>/", methods=["GET"])
@admin_login_req
def preview_del(id=None):
    """
    预告删除
    """
    preview = Preview.query.get_or_404(id)
    db.session.delete(preview)
    db.session.commit()
    flash("预告删除成功", "ok")
    return redirect(url_for('admin.preview_list', page=1))
@admin.route("/preview/edit/<int:id>/", methods=["GET",'POST'])
@admin_login_req
def preview_edit(id):
    """
    编辑预告
    """
    form = PreviewForm()
    # 下面这行代码禁用编辑时的提示:封面不能为空
    form.logo.validators = []
    preview = Preview.query.get_or_404(int(id))
    # get方法时，为title赋初值
    if request.method == "GET":
        form.title.data = preview.title
    if form.validate_on_submit():
        data = form.data
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(os.path.join(current_app.config["UP_DIR"] ,preview.logo))
        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功！", "ok")
        return redirect(url_for('admin.preview_edit', id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


from movie.models import User
@admin.route("/user/list/<int:page>/", methods=["GET"])
@admin_login_req
def user_list(page =None):
    """
    会员列表
    """
    if page is None:
        page = 1
    page_data = User.query.order_by(
    User.addtime.desc()
    ).paginate(page=page, per_page=1)
    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login_req
def user_view(id=None):
    """
    查看会员详情
    """
    from_page = request.args.get('fp')
    # 兼容不加参数的无来源页面访问。
    if not from_page:
        from_page = 1
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user, from_page=from_page)

@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
def user_del(id=None):
    """
    删除会员
    """
    # 因为删除当前页。假如是最后一页，这一页已经不见了。回不到。
    from_page = int(request.args.get('fp')) -1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not from_page:
        from_page = 1
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功！", "ok")
    return redirect(url_for('admin.user_list', page=from_page))

from movie.models import Comment
@admin.route("/comment/list/<int:page>/", methods=["GET"])
@admin_login_req
def comment_list(page=None):
    """
    评论列表
    """
    if page is None:
        page = 1
    # 通过评论join查询其相关的movie，和相关的用户。
    # 然后过滤出其中电影id等于评论电影id的电影，和用户id等于评论用户id的用户
    page_data = Comment.query.join(
    Movie
    ).join(
    User
    ).filter(
    Movie.id == Comment.movie_id,
    User.id == Comment.user_id
    ).order_by(
    Comment.addtime.desc()
    ).paginate(page=page, per_page=1)
    return render_template("admin/comment_list.html", page_data=page_data)

@admin.route("/comment/del/<int:id>/", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    """
    删除评论
    """
    # 因为删除当前页。假如是最后一页，这一页已经不见了。回不到。
    from_page = int(request.args.get('fp')) - 1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not from_page:
        from_page = 1
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", "ok")
    return redirect(url_for('admin.comment_list', page=from_page))

from movie.models import Moviecol
@admin_login_req
@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
def moviecol_list(page=None):
    """
    电影收藏
    """
    if page is None:
        page = 1
    page_data = Moviecol.query.join(
    Movie
    ).join(
    User
    ).filter(
    Movie.id == Moviecol.movie_id,
    User.id == Moviecol.user_id
    ).order_by(
    Moviecol.addtime.desc()
    ).paginate(page=page, per_page=1)
    return render_template("admin/moviecol_list.html", page_data=page_data)

@admin.route("/moviecol/del/<int:id>/", methods=["GET"])
@admin_login_req
def moviecol_del(id=None):
    """
    收藏删除
    """
    # 因为删除当前页。假如是最后一页，这一页已经不见了。回不到。
    from_page = int(request.args.get('fp')) - 1
    # 此处考虑全删完了，没法前挪的情况，0被视为false
    if not from_page:
        from_page = 1
    moviecol = Moviecol.query.get_or_404(int(id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功！", "ok")
    return redirect(url_for('admin.moviecol_list',page=from_page))

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