#
from .libs import qcb


#
from .rpc_types import types_allowed as _types_allowed
from .rpc_types import types_ids_map as _types_ids_map
from .rpc_types import types_indicators_map as _types_indicators_map


#
class RPCRemote:


    #
    def __init__(self, rfile, wfile):
        #
        self.rfile = rfile
        self.wfile = wfile
        #
        self.rpc = self.pc    # 别名。


    #
    def pc(self, proc_name:str):
        assert(len(proc_name) > 0)
        return lambda *args: self._pc(proc_name, *args)


    #
    def _pc(self, proc_name:str, *args):
        # 打包远程过程名和参数。
        ss = []
        ss.append(proc_name.encode("ascii"))    # 可以调整。
        for arg in args:
            if id(type(arg)) in _types_allowed:
                arg_type = _types_ids_map[id(type(arg))]
                s = arg_type.to_bytes(arg)
                ti = arg_type.type_indicator
                ss.append(ti + s)
            else:
                raise RuntimeError("调用传入了不受支持的RPC参数数据类型。")
        # 发送。
        qcb.put(self.wfile, ss)
        # 接收。
        qcbr = qcb.get(self.rfile)
        # 判断成功\失败。
        if qcbr[0] == b"\xff":
            err_msg = qcbr[1].decode("utf8")
            raise RuntimeError("服务端执行RPC操作失败。错误：" + err_msg)
        if not qcbr[0] == b"\x00":
            raise RuntimeError("服务端返回的RPC操作成功\失败指示字段不合法。")
        # 提取返回数据。
        results = []
        for s in qcbr[1:]:
            if not s[0:1] in _types_indicators_map:
                raise RuntimeError(
                        "\
                        服务端返回的数据使用了不受支持的数据类型，type_indicator: \
                        " + int.from_bytes(s[0:1], "big") + "。\
                        "
                    )
            res_type = _types_indicators_map[s[0:1]]
            d = res_type.from_bytes(s[1:])    # 小心长数据。
            results.append(d)
        #
        return results
