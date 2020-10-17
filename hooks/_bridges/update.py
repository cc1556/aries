#!/usr/bin/env python3


#
import sys


#
from libs.tcp_rpc_c import TCPRPCRemote


#
CORE_APIS_RPC_ADDR = sys.argv[1]
CORE_APIS_RPC_PORT = int(sys.argv[2])
HOOK_PROJECT_NAME = sys.argv[3]
HOOK_PUSHED_REF = sys.argv[4]
HOOK_PUSHED_OLD_REV = sys.argv[5]
HOOK_PUSHED_NEW_REV = sys.argv[6]


#
try:


    #
    r = TCPRPCRemote(CORE_APIS_RPC_ADDR, CORE_APIS_RPC_PORT)


    ###
    ### 推送到master分支。
    ###
    if HOOK_PUSHED_REF == "refs/heads/master":
        raise NotImplementedError("master")


    ###
    ### 推送到develop分支。
    ###
    if HOOK_PUSHED_REF == "refs/heads/develop":
        raise NotImplementedError("develop")


    ###
    ### 检查是否推送到object分支。
    ###
    result = r.pc("list_objects")(HOOK_PROJECT_NAME)
    assert(type(result) == list)
    assert(len(result) == 1)
    assert(type(result[0] == list))
    assert(len(result[0]) == 2)
    if result[0][0] == 0:
        objects = [object["name"] for object in result[0][1]]
    else:
        raise RuntimeError("RPC failure:", result[0][0], result[0][1])
    for object in objects:
        if "refs/heads/" + object == HOOK_PUSHED_REF:
            
            # 推送到object分支。
            raise NotImplementedError("object")


    ###
    ### 检查是否推送到task分支。
    ###
    for object in objects:    # coreAPI设计有问题。
        result = r.pc("list_tasks")(object, HOOK_PROJECT_NAME)
        assert(type(result) == list)
        assert(len(result) == 1)
        assert(type(result[0] == list))
        assert(len(result[0]) == 2)
        if not result[0][0] == 0:
            raise RuntimeError("RPC failure:", result[0][0], result[0][1])
        for task in result[0][1]:
            if "refs/heads/" + task["name"] == HOOK_PUSHED_REF:

                # 推送到task分支。
                print("[_bridges/update.py]" + "可以更新分支\"" + task["name"] + "\"。")
                sys.exit(0)


    ###
    ### 目标分支不存在。
    ###
    else:
        raise RuntimeError("目标分支不存在。", result[0][0], result[0][1])


#
except Exception as e:
    print("[_bridges/update.py]" + repr(e))
    sys.exit(255)
