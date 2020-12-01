import socket
from threefive import Stream
from threefive.tools import to_stderr

"""
mcastc.py is an example multicast client for threefive.
mcastd.py is an example multicast local server.

The current mcast ip settings are optimized for 
the loopback interface. 

Usage:

start server:

    python3 mcastd.py video.ts
    
start client (in a new terminal):

    python3 mcastc.py 
    
"""


def foundit(cue):
    """
    for custom SCTE-35 cue data handling
    pass a function in to Stream.decode.
    
    example:
            Stream.decode(func=foundit)
    """
    to_stderr(cue.get_json())


class StreamFu(Stream):
    """
    StreamFu is a subclass of threefive.Stream.
    It prints the pts from the stream to show progress.
    """

    def _parse_pts(self, pkt, pid):
        """
        parse pts with output
        """
        super()._parse_pts(pkt, pid)
        ppp = self._pid_prog[pid]
        pts = self._prog_pts[ppp]
        print(f"\033[92m{round(pts,6)}\033[0m", end="\r")


def read_stream(sock):
    with sock.makefile(mode="rb") as socket_file:
        ts = StreamFu(socket_file)
        ts.decode()  # without a function being passed in.
        # ts.decode(func=foundit)   # with a function passed in.
        # ts.show()   # will display stream types by program.


def mk_sock(mcast_host, mcast_ip, mcast_port):
    """
    multicast socket setup    
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(mcast_ip) + socket.inet_aton(mcast_host),
    )
    sock.bind((mcast_host, mcast_port))
    return sock


if __name__ == "__main__":

    mcast_host = "0.0.0.0"
    mcast_ip = "224.255.0.1"
    mcast_port = 35555

    mcast_sock = mk_sock(mcast_host, mcast_ip, mcast_port)
    read_stream(mcast_sock)