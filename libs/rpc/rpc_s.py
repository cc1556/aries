#
from .libs import qcb


#
from .rpc_types import types_allowed as _types_allowed
from .rpc_types import types_ids_map as _types_ids_map
from .rpc_types import types_indicators_map as _types_indicators_map


#
class RPCHost:


    #
    def __init__(self):
        self.procs = {}


    #
    def reg(
                self,
                proc:type(lambda:None),
                name:str,
                override=False
            ):
        if not len(name) > 0:
            raise RuntimeError("过程名不可为空字符串。")
        if name in self.procs:
            if not self.procs[name] == proc:
                if not override:
                    raise RuntimeError("过程名已被注册。")
        self.procs[name] = proc
        return


    #
    def handle(self, rfile, wfile):
        try:
            # 接收。
            qcbr = qcb.get(rfile)
            assert(len(qcbr) >= 1)
            # 提取并验证过程名。
            proc_name = qcbr[0].decode("ascii")
            if not proc_name in self.procs:
                raise RuntimeError("客户端请求的过程名不存在。")
            # 提取参数。
            args = []
            for s in qcbr[1:]:
                if not s[0:1] in _types_indicators_map:
                    raise RuntimeError(
                            "\
                            客户端发送的数据使用了不受支持的数据类型，type_indicator: \
                            " + int.from_bytes(s[0:1], "big") + "。\
                            "
                        )
                res_type = _types_indicators_map[s[0:1]]
                arg = res_type.from_bytes(s[1:])    # 小心长数据x2。
                args.append(arg)
            # 获取过程本体。
            proc = self.procs[proc_name]
            # 调用过程。
            ret = proc(*args)
            if not type(ret) == tuple:
                rets = (ret, )
            else:
                rets = ret
            # 打包状态指示字段和返回值。
            ss = []
            ss.append(b"\x00")
            for ret in rets:
                if id(type(ret)) in _types_allowed:
                    ret_type = _types_ids_map[id(type(ret))]
                    s = ret_type.to_bytes(ret)
                    ti = ret_type.type_indicator
                    ss.append(ti + s)
                else:
                    raise RuntimeError("过程返回值包含不受支持的RPC数据类型。")
        except Exception as e:
            # 处理错误。
            ss = []
            ss.append(b"\xff")
            ss.append(repr(e).encode("utf8"))
        # 发送。
        qcb.put(wfile, ss)
