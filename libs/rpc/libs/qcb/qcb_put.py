#
import hashlib


#
def make_header(ss:list):
    header1 = len(ss).to_bytes(1, "big")
    header2 = b""
    header3 = b""
    for s in ss:
        sll = (len(s).bit_length() + 7) // 8
        assert(sll <= 255)
        header2 += sll.to_bytes(1, "big")
        header3 += len(s).to_bytes(sll, "big")
    headers = (header1, header2, header3)
    return headers


#
def put_header(wfile, headers):
    wfile.write(headers[0])
    wfile.write(headers[1])
    wfile.write(headers[2])


#
def put_body(wfile, ss:list):
    for s in ss:
        wfile.write(s)


#
def put_tail(wfile, headers, ss:list):
    hx = hashlib.sha1()
    hx.update(headers[0])
    hx.update(headers[1])
    hx.update(headers[2])
    for s in ss:
        hx.update(s)
    wfile.write(hx.hexdigest().encode("ascii"))
