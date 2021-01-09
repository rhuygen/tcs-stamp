"""
"""
import datetime
import logging
import operator
import re
import socket
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TCS-STAMP")


class SocketInterface:
    """Base class that implements the socket interface."""

    def __init__(self, hostname: str, port: int):
        self.is_connection_open = False
        self.hostname = hostname
        self.port = port
        self.socket = None

    @property
    def device_name(self):
        """The name of the device that this interface connects to."""
        raise NotImplementedError

    def connect(self):
        """
        Connect the device.

        Raises:
            ConnectionError: When the connection could not be established. Check the logging
                messages for more detail.
            TimeoutError: When the connection timed out.
            ValueError: When hostname or port number are not provided.
        """

        # Sanity checks

        if self.is_connection_open:
            logger.warning(f"{self.device_name}: trying to connect to an already connected socket.")
            return

        if self.hostname in (None, ""):
            raise ValueError(f"{self.device_name}: hostname is not initialized.")

        if self.port in (None, 0):
            raise ValueError(f"{self.device_name}: port number is not initialized.")

        # Create a new socket instance

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e_socket:
            raise ConnectionError(f"{self.device_name}: Failed to create socket.") from e_socket

        # We set a timeout of 3 sec before connecting and reset to None
        # (=blocking) after the connect. The reason for this is because when no
        # device is available, e.g during testing, the timeout will take about
        # two minutes which is way too long. It needs to be evaluated if this
        # approach is acceptable and not causing problems during production.

        try:
            logger.debug(f'Connecting a socket to host "{self.hostname}" using port {self.port}')
            self.socket.settimeout(3)
            self.socket.connect((self.hostname, self.port))
            self.socket.settimeout(None)
        except ConnectionRefusedError as exc:
            raise ConnectionError(
                f"{self.device_name}: Connection refused to {self.hostname}:{self.port}."
            ) from exc
        except TimeoutError as exc:
            raise TimeoutError(
                f"{self.device_name}: Connection to {self.hostname}:{self.port} timed out."
            ) from exc
        except socket.gaierror as exc:
            raise ConnectionError(
                f"{self.device_name}: socket address info error for {self.hostname}"
            ) from exc
        except socket.herror as exc:
            raise ConnectionError(
                f"{self.device_name}: socket host address error for {self.hostname}"
            ) from exc
        except socket.timeout as exc:
            raise TimeoutError(
                f"{self.device_name}: socket timeout error for {self.hostname}:{self.port}"
            ) from exc
        except OSError as exc:
            raise ConnectionError(f"{self.device_name}: OSError caught ({exc}).") from exc

        self.is_connection_open = True

    def disconnect(self):
        """
        Disconnect from the Ethernet connection.

        Raises:
            ConnectionError when the socket could not be closed.
        """

        try:
            if self.is_connection_open:
                logger.debug(f"Disconnecting from {self.hostname}")
                self.socket.close()
                self.is_connection_open = False
        except Exception as e_exc:
            raise ConnectionError(
                f"{self.device_name}: Could not close socket to {self.hostname}") from e_exc


class STAMPInterface(SocketInterface):
    """Connects to STAMP and sends the periodic telemetry that was received from the TCS EGSE."""

    @property
    def device_name(self):
        """The name of the device."""
        return "STAMP"

    def write(self, data: bytes):
        """Write data to the socket."""
        self.socket.sendall(data)


class TCSInterface(SocketInterface):
    """Connects to the TCS EGSE and reads periodic Telemetry from the TCS connection."""

    @property
    def device_name(self):
        """The name of the device."""
        return "TCS"

    def read(self) -> str:
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
                data = self.socket.recv(buf_size)
                n = len(data)
                n_total += n
                response += data
                if data.endswith(b'\x03'):
                    break
        except socket.timeout as e_timeout:
            logger.warning(f"Socket timeout error from {e_timeout}")
            return ""

        logger.debug(f"Total number of bytes received is {n_total}, idx={idx}")

        return response.decode(encoding='ISO-8859–1')


