#
import hashlib


#
def parse_header1(rfile):
    header1 = rfile.read(1)
    _sc = int(header1[0])    # sc: Segment count.
    return header1, _sc


#
def parse_header2(rfile, _sc):
    header2 = rfile.read(_sc)
    _slls = [int(header2[i]) for i in range(_sc)]    # slls: Segments length lengths.
    return header2, _slls


#
def parse_header3(rfile, _slls):
    header3 = b""
    _sls = []    # sls: Segments lengths.
    for sll in _slls:
        bs = rfile.read(sll)    # bs: Bytes.
        header3 += bs
        _sls.append(int.from_bytes(bs, "big"))
    return header3, _sls


#
def parse_body(rfile, _sls):
    ss = [rfile.read(sl) for sl in _sls]    # ss: Segments.
    return ss


#
def check_tail(rfile, header1, header2, header3, ss):
    tail = rfile.read(40)
    hx = hashlib.sha1()
    hx.update(header1)
    hx.update(header2)
    hx.update(header3)
    for s in ss:
        hx.update(s)
    return tail, (tail.decode("ascii") == hx.hexdigest())
