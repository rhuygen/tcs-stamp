import argparse
import logging
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 4444         # Port to listen on (non-privileged ports are > 1023)

logger = logging.getLogger("echo server")


def read(conn) -> str:
    """
    Read the telemetry from the socket until the EOT ('\x03') is received.

    Returns:
        A bytes object containing the received telemetry.
    """
    idx, n_total = 0, 0
    buf_size = 1024 * 4
    response = bytes()

    try:
        for idx in range(100):
            # time.sleep(0.01)  # Give the device time to fill the buffer
            data = conn.recv(buf_size)
            n = len(data)
            n_total += n
            response += data
            # if data.endswith(b'\n'):
            if n < buf_size:
                break
    except socket.timeout as e_timeout:
        logger.warning(f"Socket timeout error from {e_timeout}")
        return ""

    logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")

    return response.decode(encoding='ISO-8859–1')


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """

    parser = argparse.ArgumentParser(
        prog="echo_server",
        description="Listen on the given port [default=4444] and echo stream to stdout.",
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=PORT,
        help="The TCP port to listen for incoming connections.",
    )

    arguments = parser.parse_args()
    return arguments


def main():

    args = parse_arguments()
    port = args.port

    print(f"Listening on {HOST}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Accepted connection from', addr)
            try:
                while True:
                    data = read(conn)
                    if not data:
                        break
                    print(repr(data))
            except KeyboardInterrupt:
                print("Keyboard interrupt, closing.")


if __name__ == "__main__":
    main()
