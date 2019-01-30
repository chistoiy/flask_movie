
from werkzeug.utils import secure_filename
import os,uuid
from datetime import datetime
# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


import  sys, stat
import platform
from flask import current_app
def sel_chmod():
    #因为windows chmod方法第一次改变文件夹读写时会异常报错，所以修改为判断平台方式
    os.makedirs(current_app.config["FC_DIR"])
    osName = platform.system()
    if (osName == 'Windows'):
        os.chmod(current_app.config["FC_DIR"], stat.S_IWRITE and stat.S_IREAD)
    else:
        os.chmod(current_app.config["FC_DIR"], "rw")
