#
import io


#
from .libs import qcb
from .libs.qcb import qcb_put


#
class RPCType:


    #
    def __init__(
                self,
                to_bytes:type(lambda:None),
                from_bytes:type(lambda:None),
                type_indicator:bytes
            ):
        self.to_bytes = to_bytes
        self.from_bytes = from_bytes
        assert(len(type_indicator) == 1)
        self.type_indicator = type_indicator


###
### bytes。
###
type_pybuiltin_bytes = RPCType(
        lambda d: d,
        lambda d: d,
        (0).to_bytes(1, "big")
    )


###
### str。
###
type_pybuiltin_str = RPCType(
        lambda d: d.encode("utf-8"),
        lambda d: d.decode("utf-8"),
        (1).to_bytes(1, "big")
    )


###
### int。
###
type_pybuiltin_int = RPCType(
        lambda d: d.to_bytes((d.bit_length() + 7)//8, "big", signed=True),
        lambda d: int.from_bytes(d, "big", signed=True),
        (2).to_bytes(1, "big")
    )


###
### NoneType。
###
type_pybuiltin_NoneType = RPCType(
        lambda d: b"\x00",
        lambda d: None,
        (127).to_bytes(1, "big")
    )


###
### list。
### 复合类型，使用qcb。
###
def type_pybuiltin_list_to_bytes(ds:list):
    bs = []
    for d in ds:
        assert(id(type(d)) in types_allowed)
        dt = types_ids_map[id(type(d))].type_indicator
        db = types_ids_map[id(type(d))].to_bytes(d)
        b = dt + db
        bs.append(b)
    hs = qcb_put.make_header(bs)
    return b"".join(hs) + b"".join(bs) + qcb_put.make_tail(hs, bs)    # 直接拼接qcb串。
#
def type_pybuiltin_list_from_bytes(bs):
    bs =  qcb.get(io.BytesIO(bs))    # 也不是不行。
    return [types_indicators_map[b[0:1]].from_bytes(b[1:]) for b in bs]
#
type_pybuiltin_list = RPCType(
        type_pybuiltin_list_to_bytes,
        type_pybuiltin_list_from_bytes,
        (128).to_bytes(1, "big")
    )


###
### dict。
### 复合类型，使用qcb。
###
def type_pybuiltin_dict_to_bytes(ds:dict):
    for k in ds:    # k: key。
        assert(id(type(k)) in types_allowed)
        assert(id(type(ds[k])) in types_allowed)
    bs = []
    for k in ds:
        kt = types_ids_map[id(type(k))].type_indicator
        kb = types_ids_map[id(type(k))].to_bytes(k)
        bs.append(kt + kb)
        vt = types_ids_map[id(type(ds[k]))].type_indicator
        vb = types_ids_map[id(type(ds[k]))].to_bytes(ds[k])
        bs.append(vt + vb)
    hs = qcb_put.make_header(bs)
    return b"".join(hs) + b"".join(bs) + qcb_put.make_tail(hs, bs)    # 直接拼接qcb串。
#
def type_pybuiltin_dict_from_bytes(bs):
    bs = qcb.get(io.BytesIO(bs))    # 也不是不行。
    assert(len(bs) % 2 == 0)
    ds = {}
    for i in range(int(len(bs)/2)):
        kb = bs[i*2]
        k = types_indicators_map[kb[0:1]].from_bytes(kb[1:])
        vb = bs[i*2+1]
        v = types_indicators_map[vb[0:1]].from_bytes(vb[1:])
        ds[k] = v
    return ds
#
type_pybuiltin_dict = RPCType(
        type_pybuiltin_dict_to_bytes,
        type_pybuiltin_dict_from_bytes,
        (129).to_bytes(1, "big")
    )


#
types_allowed = {
        id(bytes),
        id(str),
        id(int),
        id(type(None)),
        id(list),
        id(dict),
    }


#
types_ids_map = {
        id(bytes): type_pybuiltin_bytes,
        id(str): type_pybuiltin_str,
        id(int): type_pybuiltin_int,
        id(type(None)): type_pybuiltin_NoneType,
        id(list): type_pybuiltin_list,
        id(dict): type_pybuiltin_dict,
    }


#
types_indicators_map = {
        type_pybuiltin_bytes.type_indicator: type_pybuiltin_bytes,
        type_pybuiltin_str.type_indicator: type_pybuiltin_str,
        type_pybuiltin_int.type_indicator: type_pybuiltin_int,
        type_pybuiltin_NoneType.type_indicator: type_pybuiltin_NoneType,
        type_pybuiltin_list.type_indicator: type_pybuiltin_list,
        type_pybuiltin_dict.type_indicator: type_pybuiltin_dict,
    }
