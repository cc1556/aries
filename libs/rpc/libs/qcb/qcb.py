#
from .qcb_get import parse_header1, parse_header2, parse_header3, parse_body, check_tail
from .qcb_put import make_header, put_header, put_body, put_tail


#
def get(rfile):
    header1, _sc = parse_header1(rfile)
    header2, _slls = parse_header2(rfile, _sc)
    header3, _sls = parse_header3(rfile, _slls)
    ss = parse_body(rfile, _sls)
    _, verified = check_tail(rfile, header1, header2, header3, ss)
    if not verified:
        raise RuntimeError("Checksum error detected.")
    else:
        return ss


#
def put(wfile, ss):
    headers = make_header(ss)
    put_header(wfile, headers)
    put_body(wfile, ss)
    put_tail(wfile, headers, ss)
