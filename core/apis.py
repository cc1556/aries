#
import fcntl
import os
import os.path
import re
import subprocess
import sqlite3


#
from config import config


#
DATABASE_PATH = config["APIS_DATABASE_PATH"]


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
        with open("/var/lock/aries." + ".project." + project + ".lock", "wb") as l:    # flock实现同步。
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
                os.mkdir(project + ".git")
                # 创建仓库。    #########
                subprocess.run(
                        ("git init --bare").split(),
                        cwd=("./" + project + ".git")
                    )
                # 配置仓库user.name。    #########
                p = subprocess.run(
                        ("git config --local user.name").split() + ["\"SCM Core\""],
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
                        capture_output=True,
                        text=True
                    )
                if not p.stderr == "":
                    raise RuntimeError("Git raise STDERR while creating README.md:\n" + "$ " + " ".join(p.args) + "\n" + p.stderr)
                if not p.stdout == "":
                    raise RuntimeError("Git print unexpected message to STDOUT:\n" + "$ " + " ".join(p.args) + "\n" + p.stdout)
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
        lp = open("/var/lock/aries." + ".project." + project + ".lock", "wb")
        lo = open("/var/lock/aries." + ".object." + project + "." + object + ".lock", "wb")
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
        lp = open("/var/lock/aries." + ".project." + project + ".lock", "wb")
        lo = open("/var/lock/aries." + ".object." + project + "." + object + ".lock", "wb")
        lt = open("/var/lock/aries." + ".task." + project + "." + object + "." + task + ".lock", "wb")
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
                        cwd="./" + project + ".git",
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
        lp = open("/var/lock/aries.project." + project + ".lock", "wb")
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
        lp = open("/var/lock/aries.project." + project + ".lock", "wb")
        lo = open("/var/lock/aries.object." + project + "." + object + ".lock", "wb")
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
