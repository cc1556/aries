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
        lambda d: d.to_bytes((d.bit_length() + 7)//8, "big"),
        lambda d: int.from_bytes(d, "big"),
        (2).to_bytes(1, "big")
    )


#
types_allowed = {
        id(bytes),
        id(str),
        id(int),
    }


#
types_ids_map = {
        id(bytes): type_pybuiltin_bytes,
        id(str): type_pybuiltin_str,
        id(int): type_pybuiltin_int,
    }


#
types_indicators_map = {
        type_pybuiltin_bytes.type_indicator: type_pybuiltin_bytes,
        type_pybuiltin_str.type_indicator: type_pybuiltin_str,
        type_pybuiltin_int.type_indicator: type_pybuiltin_int,
    }
