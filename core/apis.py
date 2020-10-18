#
import base64
import fcntl
import hashlib
import os
import os.path
import re
import shutil
import stat
import subprocess
import sqlite3


#
import Crypto.Hash.SHA512
import Crypto.PublicKey.RSA
import Crypto.Signature.PKCS1_v1_5
import jinja2


#
from config import config


#
RPC_SERVER_NET_ADDR = config["RPC_SERVER_NET_ADDR"]
RPC_SERVER_TCP_PORT = config["RPC_SERVER_TCP_PORT"]
FLOCKS_DIR_PATH = config["GLOBAL_FLOCKS_DIR_PATH"]
DATABASE_PATH = config["APIS_DATABASE_PATH"]
GIT_DIR_PATH = config["APIS_GIT_DIR_PATH"]
GIT_HOOKS_PATH = config["APIS_GIT_HOOKS_PATH"]


###
### 添加新项目（Project）。
### 参数:
###     project：新项目名。
### 返回值：
###     0：创建新项目成功。
###     -1：创建失败，给定的项目名已c.cursor()存在于数据库中。
###     -2：创建失败，给定的项目名与已存在的目录冲突。
###     -999：创建失败，运行时错误。
###
def add_project(project:str):
    try:
        with open(FLOCKS_DIR_PATH + "/aries." + ".project." + project + ".lock", "wb") as l:    # flock实现同步。
            fcntl.flock(l.fileno(), fcntl.LOCK_EX)    # 锁。
            with sqlite3.connect(DATABASE_PATH) as conn:
                # 查询数据库，检查project是否已存在。    #########
                c = conn.cursor()
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    return [-1, None]
                if os.path.exists(project + ".git"):
                    return [-2, None]
                #    #########
                os.mkdir(GIT_DIR_PATH + "/" + project + ".git")
                # 创建仓库。    #########
                subprocess.run(
                        ("git init --bare").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git"
                    )
                # 配置仓库user.name。    #########
                p = subprocess.run(
                        ("git config --local user.name").split() + ["\"SCM Core\""],
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 配置仓库user.email。    #########
                p = subprocess.run(
                        ("git config --local user.email scm-core@aries").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 创建README.md对象。    #########
                p = subprocess.run(
                        ("git hash-object -w --stdin").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        input=(project + "\n"),
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                readme_md_hash = re.match(r"[0-9a-f]{40}", p.stdout.strip()).string
                # 更新README.md到index中。    #########
                p = subprocess.run(
                        ("git update-index --add --cacheinfo 100644 " + readme_md_hash + " README.md").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 写入tree对象。    #########
                p = subprocess.run(
                        ("git write-tree").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                tree_hash = re.match(r"[0-9a-f]{40}", p.stdout.strip()).string
                # 创建初始commit对象。    #########
                p = subprocess.run(
                        ("git commit-tree " + tree_hash).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        input=("Initial commit\n"),
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                commit_hash = re.match(r"[0-9a-f]{40}", p.stdout.strip()).string
                # 更新master分支到初始commit。    #########
                p = subprocess.run(
                        ("git update-ref refs/heads/master " + commit_hash).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 创建develop分支到初始commit。    #########
                p = subprocess.run(
                        ("git update-ref refs/heads/develop " + commit_hash).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 清空hooks文件夹。    #########
                for fname in os.listdir(GIT_DIR_PATH + "/" + project + ".git/hooks"):
                    fpath = GIT_DIR_PATH + "/" + project + ".git/hooks/" + fname
                    assert(os.path.isfile(fpath))
                    os.remove(fpath)
                # 渲染钩子模板。    #########
                with open(GIT_HOOKS_PATH + "/update.jinja", "r") as f_tmpl:
                    tmpl = f_tmpl.read()
                tmpl = jinja2.Template(tmpl)
                args = {
                        "core_apis": {
                                "addr": RPC_SERVER_NET_ADDR,
                                "port": RPC_SERVER_TCP_PORT,
                            },
                        "project_name": project,
                    }
                with open(GIT_DIR_PATH + "/" + project + ".git/hooks/update", "w") as f_hook:
                    f_hook.write(tmpl.render(args=args))
                # 修改钩子权限。    #########
                for fname in os.listdir(GIT_DIR_PATH + "/" + project + ".git/hooks"):
                    fpath = GIT_DIR_PATH + "/" + project + ".git/hooks/" + fname
                    if os.path.isfile(fpath):
                        os.chmod(fpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IROTH)    # chmod 744
                # 复制钩子后端桥。    #########
                shutil.copytree(GIT_HOOKS_PATH + "/_bridges", GIT_DIR_PATH + "/" + project + ".git/hooks/_bridges")
                # 更新数据库。    #########
                c.execute(
                        " \
                        INSERT \
                            INTO projects \
                            VALUES (\"" + project + "\") \
                        "
                    )
                conn.commit()
    except Exception as e:
        return [-999, repr(e)]
    return [0, None]


###
### 添加新目标（Object）。
### 参数：
###     object：新目标名。
###     project：新目标隶属项目。
### 返回值：
###     0：创建新目标成功。
###     -1：创建失败，项目不存在于数据库中。
###     -2：创建失败，目标分支已存在于项目中。
###     -3：创建失败，目标分支与项目中已有的，但未记录于数据库的分支冲突。
###     -999：创建失败，运行时错误。
###
def add_object(object:str, project:str):
    try:
        lp = open(FLOCKS_DIR_PATH + "/aries." + ".project." + project + ".lock", "wb")
        lo = open(FLOCKS_DIR_PATH + "/aries." + ".object." + project + "." + object + ".lock", "wb")
        with lp, lo:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lo.fileno(), fcntl.LOCK_EX)
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                # 查询project是否存在。   #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
                # 查询object是否存在于project中并已由数据库跟踪。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM objects \
                            WHERE \
                                name=\"" + object + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                for row in r:
                    return [-2, None]
                # 检查object是否与refs/heads中已有分支冲突。    #########
                p = subprocess.run(
                        ("git show-ref refs/heads/" + object).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    if (len(p.stdout.strip()) == (40 + 1 + len("refs/heads/" + object)) and re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/" + object, p.stdout.strip())):
                        return [-3, None]
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 获取develop当前指向的commit。    #########
                p = subprocess.run(
                        ("git show-ref refs/heads/develop").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == (40 + 1 + len("refs/heads/develop")) and re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/develop", p.stdout.strip())):
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                dev_commit_hash = re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/develop", p.stdout.strip()).string[0:40]
                # 添加新object。    #########
                p = subprocess.run(
                        ("git update-ref refs/heads/" + object + " " + dev_commit_hash).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 写入数据库。    #########
                c.execute(
                        " \
                        INSERT \
                            INTO objects \
                            VALUES (\"" + object + "\", \"" + project + "\") \
                        "
                    )
                conn.commit()
    except Exception as e:
        return [-999, repr(e)]
    return [0, None]


###
### 添加新任务（Task）。
### 参数：
###     task：新任务名。
###     object：新任务隶属目标。
###     project：新任务隶属项目。
### 返回值：
###     0：创建新目标成功。
###     -1：创建失败，项目不存在于数据库中。
###     -2：创建失败，目标分支不存在于项目中。
###     -3：创建失败，任务分支已存在于项目中。
###     -4：创建失败，任务分支与项目中已有的，但未记录于数据库的分支冲突。
###     -999：创建失败，运行时错误。
###
def add_task(task:str, object:str, project:str):
    try:
        lp = open(FLOCKS_DIR_PATH + "/aries." + ".project." + project + ".lock", "wb")
        lo = open(FLOCKS_DIR_PATH + "/aries." + ".object." + project + "." + object + ".lock", "wb")
        lt = open(FLOCKS_DIR_PATH + "/aries." + ".task." + project + "." + object + "." + task + ".lock", "wb")
        with lp, lo, lt:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lo.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lt.fileno(), fcntl.LOCK_EX)
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                # 查询project是否存在。   #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
                # 查询object是否存在于project中并已由数据库跟踪。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM objects \
                            WHERE \
                                name=\"" + object + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-2, None]
                # 查询task是否存在于project中并已由数据库跟踪。    #########
                r = c.execute(    # task分支可能与object分支及其附属task分支冲突。
                        " \
                        SELECT * \
                            FROM tasks \
                            WHERE \
                                name=\"" + task + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                for row in r:
                    return [-3, None]
                # 检查task是否与refs/heads中已有分支冲突。    #########
                p = subprocess.run(
                        ("git show-ref refs/heads/" + task).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    if (len(p.stdout.strip()) == (40 + 1 + len("refs/heads/" + task)) and re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/" + task, p.stdout.strip())):
                        return [-4, None]
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 获取object当前指向的commit。    #########
                p = subprocess.run(
                        ("git show-ref refs/heads/" + object).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == (40 + 1 + len("refs/heads/" + object)) and re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/" + object, p.stdout.strip())):
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                obj_commit_hash = re.match(r"[0-9a-f]{40}[\s]{1}refs/heads/" + object, p.stdout.strip()).string[0:40]
                # 添加新task。    #########
                p = subprocess.run(
                        ("git update-ref refs/heads/" + task + " " + obj_commit_hash).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                # 写入数据库。    #########
                c.execute(
                        " \
                        INSERT \
                            INTO tasks \
                            VALUES (\"" + task + "\", \"" + object + "\", \"" + project + "\") \
                        "
                    )
                conn.commit()
    except Exception as e:
        return [-999, repr(e)]
    return [0, None]


###
### 列出所有项目（Project）。
### 参数：
###     （无）
### 返回值：
###     0：列出成功。
###     -999：列出失败，运行时错误。
###
def list_projects():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            r = c.execute(
                    " \
                    SELECT * \
                        FROM projects \
                    "
                )
            projects = []
            for row in r:
                project = {
                        "name": row[0],
                    }
                projects.append(project)
    except Exception as e:
        return [-999, repr(e)]
    return [0, projects]


###
### 列出项目（Project）内的所有目标（Object）。
### 参数：
###     project：将列出的项目。
### 返回值：
###     0：列出成功。
###     -1：列出失败，项目不存在。
###     -999：列出失败，运行时错误。
###
def list_objects(project:str):
    try:
        lp = open(FLOCKS_DIR_PATH + "/aries.project." + project + ".lock", "wb")
        with lp:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                # 查询project是否存在。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
                # 查询objects。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM objects \
                            WHERE project=\"" + project + "\" \
                        "
                    )
                objects = []
                for row in r:
                    object = {
                            "name": row[0],
                        }
                    objects.append(object)
    except Exception as e:
        return [-999, repr(e)]
    return [0, objects]


###
### 列出项目（Project）中隶属于目标（Object）的所有任务。
### 参数：
###     object：将列出的目标。
###     project：将列出的项目。
### 返回值：
###     0：列出成功。
###     -1：列出失败，项目不存在。
###     -2：列出失败，项目中不存在目标。
###     -999：列出失败，运行时错误。
###
def list_tasks(object:str, project:str):
    try:
        lp = open(FLOCKS_DIR_PATH + "/aries.project." + project + ".lock", "wb")
        lo = open(FLOCKS_DIR_PATH + "/aries.object." + project + "." + object + ".lock", "wb")
        with lp, lo:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lo.fileno(), fcntl.LOCK_EX)
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                # 查询project是否存在。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
                # 查询object是否存在。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM objects \
                            WHERE \
                                name=\"" + object + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-2, None]
                # 查询tasks。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM tasks \
                            WHERE \
                                object=\"" + object + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                tasks = []
                for row in r:
                    task = {
                            "name": row[0],
                        }
                    tasks.append(task)
    except Exception as e:
        return [-999, repr(e)]
    return [0, tasks]


###
### 创建merge review。
### 参数：
###     project：要操作的项目。
###     object：要合并的目标。
###     rev：要合并版本的hash值。
###     message：提交信息。
### 返回值：
###     0：创建成功。
###     -1：创建失败，project不存在。
###     -2：创建失败，project中object不存在。
###     -3：创建失败，rev不在object分支上。
###
def create_merge(project:str, object:str, rev:str, message:str):
    try:
        assert(len(rev) == 40)
        lp = open(FLOCKS_DIR_PATH + "/aries.project." + project + ".lock", "wb")
        lo = open(FLOCKS_DIR_PATH + "/aries.object." + project + "." + object + ".lock", "wb")
        with lp, lo:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lo.fileno(), fcntl.LOCK_EX)
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                # 查询project是否存在。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM projects \
                            WHERE name=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
                # 查询object是否存在。    #########
                r = c.execute(
                        " \
                        SELECT * \
                            FROM objects \
                            WHERE \
                                name=\"" + object + "\" \
                                AND project=\"" + project + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-2, None]
                # 获取develop分支的头部。    #########
                p = subprocess.run(
                        ("cat refs/heads/develop").split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Command raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                    raise RuntimeError("Command print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                develop_hashes = [re.match(r"[0-9a-f]{40}", p.stdout.strip()).string]
                # 获取object分支的头部。    #########
                p = subprocess.run(
                        ("cat refs/heads/" + object).split(),
                        cwd=GIT_DIR_PATH + "/" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Command raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                    raise RuntimeError("Command print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                object_hashes = [re.match(r"[0-9a-f]{40}", p.stdout.strip()).string]
                # 查询object分支的起始位置。    #########
                if not object_hashes[0] in develop_hashes:
                    is_develop_at_initial_commit = False
                    is_object_at_initial_commit = False
                    while True:
                        # 回溯develop分支。    #########
                        if not is_develop_at_initial_commit:
                            p = subprocess.run(
                                    ("git cat-file -p " + develop_hashes[-1]).split(),
                                    cwd=GIT_DIR_PATH + "/" + project + ".git",
                                    capture_output=True,
                                    text=True
                                )
                            if not p.stderr == "":
                                raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                            if re.match(r"tree [0-9a-f]{40}\nparent [0-9a-f]{40}\n", p.stdout.strip()[0:94]):
                                commit_hash = p.stdout.strip()[53:93]
                                develop_hashes.append(commit_hash)
                                if commit_hash in object_hashes:
                                    break
                            elif re.match(r"tree [0-9a-f]{40}\nauthor", p.stdout.strip()[0:52]):
                                is_develop_at_initial_commit = True
                            else:
                                raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                        # 回溯object分支。    #########
                        if not is_object_at_initial_commit:
                            p = subprocess.run(
                                    ("git cat-file -p " + object_hashes[-1]).split(),
                                    cwd=GIT_DIR_PATH + "/" + project + ".git",
                                    capture_output=True,
                                    text=True
                                )
                            if not p.stderr == "":
                                raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                            if re.match(r"tree [0-9a-f]{40}\nparent [0-9a-f]{40}\n", p.stdout.strip()[0:94]):
                                commit_hash = p.stdout.strip()[53:93]
                                object_hashes.append(commit_hash)
                                if commit_hash in develop_hashes:
                                    break
                            elif re.match(r"tree [0-9a-f]{40}\nauthor", p.stdout.strip()[0:52]):
                                is_object_at_initial_commit = True
                            else:
                                raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
                        if is_develop_at_initial_commit and is_object_at_initial_commit:
                            raise RuntimeError("develop分支和\"" + object + "\"分支没有共同祖先。")
                else:
                    commit_hash = object_hashes[0]
                object_hashes = object_hashes[:object_hashes.index(commit_hash)+1]
                # 查询rev是否在object分支上。    #########
                if not rev in object_hashes:
                    return [-3, None]
                # 生成review id。    #########
                message_b64 = base64.b64encode(message.encode("utf8")).decode("ascii")
                review_base = (project + object + rev + message_b64 + develop_hashes[0]).encode("ascii")
                h = hashlib.sha512()
                h.update(review_base)
                review_id = h.hexdigest()
                # 写入数据库。    #########
                c.execute(
                        " \
                        INSERT \
                            INTO merges \
                            VALUES ( \
                                    \"" + review_id +  "\", \
                                    \"" + project + "\", \
                                    \"" + object + "\", \
                                    \"" + rev + "\", \
                                    \"" + develop_hashes[0] + "\", \
                                    \"" + message_b64 + "\" \
                                ) \
                        "
                    )
                conn.commit()
    except Exception as e:
        return [-999, repr(e)]
    return [0, review_id, develop_hashes[0]]


###
### Review merge。
### 参数：
###     review_id：Review id。
###     signature：特权用户提供关于review_id的数字签名，表示审核通过。
### 返回值：
###     0：审核成功。
###     -1：审核失败，review_id不存在。
###     -2：审核失败，数据库中没有特权用户的记录。
###     -3：审核失败，签名无效。
###
def review_merge(review_id:str, signature_b64:str):
    try:
        assert(len(review_id) == 128)
        # 检查review_id是否存在。    #########
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            r = c.execute(
                    " \
                    SELECT * \
                        FROM merges \
                        WHERE review_id=\"" + review_id + "\" \
                    "
                )
            for row in r:
                break
            else:
                return [-1, None]
        # 取回review信息。    #########
        project = row[1]
        object = row[2]
        object_rev = row[3]
        develop_rev = row[4]
        message_b64 = row[5]
        message = base64.b64decode(message_b64.encode("ascii")).decode("utf8")
        # 加锁。    #########
        lp = open(FLOCKS_DIR_PATH + "/aries.project." + project + ".lock", "wb")
        lo = open(FLOCKS_DIR_PATH + "/aries.object." + project + "." + object + ".lock", "wb")
        with lp, lo:
            fcntl.flock(lp.fileno(), fcntl.LOCK_EX)
            fcntl.flock(lo.fileno(), fcntl.LOCK_EX)
            # 检查review_id是否存在。    #########
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                r = c.execute(
                        " \
                        SELECT * \
                            FROM merges \
                            WHERE review_id=\"" + review_id + "\" \
                        "
                    )
                for row in r:
                    break
                else:
                    return [-1, None]
            # 确认锁定的review信息正确。    #########
            assert(project == row[1])
            assert(object == row[2])
            assert(object_rev == row[3])
            assert(develop_rev == row[4])
            assert(message_b64 == row[5])
            # 取回特权用户信息。    #########
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                r = c.execute(
                        " \
                        SELECT * \
                            FROM powerusers \
                        "
                    )
                powerusers = [row for row in r]
                if len(powerusers) == 0:
                    return [-2, None]
            # 验证签名。    #########
            for user in powerusers:
                uid = user[0]
                uname = user[1]
                upubkey = base64.b64decode(user[2])
                h = Crypto.Hash.SHA512.new(review_id.encode("ascii"))
                k = Crypto.PublicKey.RSA.importKey(upubkey)
                s = Crypto.Signature.PKCS1_v1_5.new(k)
                if s.verify(h, base64.b64decode(signature_b64)):
                    break
                else:
                    return [-3, None]
            # 获取rev对应的tree对象。    #########
            p = subprocess.run(
                    ("git cat-file -p " + object_rev).split(),
                    cwd=GIT_DIR_PATH + "/" + project + ".git",
                    capture_output=True,
                    text=True
                )
            if not p.stderr == "":
                raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
            if not re.match(r"tree [0-9a-f]{40}\nparent [0-9a-f]{40}\n", p.stdout.strip()[0:94]):
                raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
            tree_hash = p.stdout.strip()[5:45]
            # 创建merge commit对象。    #########
            p = subprocess.run(
                    ("git commit-tree " + tree_hash + " -p " + develop_rev + " -p " + object_rev).split(),
                    cwd=GIT_DIR_PATH + "/" + project + ".git",
                    capture_output=True,
                    input=message,
                    text=True
                )
            if not p.stderr == "":
                raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
            if not (len(p.stdout.strip()) == 40 and re.match(r"[0-9a-f]{40}", p.stdout.strip())):
                raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
            commit_hash = re.match(r"[0-9a-f]{40}", p.stdout.strip()).string
            # 更新develop分支。    #########
            p = subprocess.run(
                    ("git update-ref refs/heads/develop " + commit_hash).split(),
                    cwd=GIT_DIR_PATH + "/" + project + ".git",
                    capture_output=True,
                    text=True
                )
            if not p.stderr == "":
                raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
            if not p.stdout == "":
                raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
            # 从数据库中删除review。    #########
            with sqlite3.connect(DATABASE_PATH) as conn:
                c = conn.cursor()
                r = c.execute(
                        " \
                        DELETE \
                            FROM merges \
                            WHERE review_id=\"" + review_id + "\" \
                        "
                    )
                conn.commit()
    except Exception as e:
        return [-999, repr(e)]
    return [0, None]
