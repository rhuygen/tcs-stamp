"""

This script converts the Telemetry stream that it received from the TCS EGSE to
a CSV stream that is understood by STAMP.

"""
import argparse
import datetime
import logging
import operator
import re
import socket
import sys
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TCS-STAMP")

__version__ = "0.1"


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


def process_telemetry(data: str) -> List[List[str]]:
    """
    Process the housekeeping telemetry that was received from the TCS EGSE.

    Args:
        data (str): a string containing the telemetry from the TCS EGSE.

    Returns:
        A nested list where the inner lists contain the name, timestamp and value of a housekeeping
        parameter.
    """
    data = data.split('\x03')
    data = [x for x in data if x]
    if not data:
        logger.warning("Format error: no housekeeping value received.")
        return []
    data = data[0].split('\r\n')
    data = [x.split('\t') for x in data]
    data = sorted(data, key=operator.itemgetter(0))

    data = [[convert_date(x[0]), x[1], extract_value(x[1], x[2])] for x in data]

    return data


def convert_date(date: str):
    """
    Convert the datetime string that is sent by the TCS EGSE to a format that is required by STAMP.

    Args:
        date (str): datetime as "YYYY/MM/DD HH:MM:SS.ms UTC"

    Returns:
        A date string in the format "DD.MM.YYYY HH:MM:SS"
    """
    global time_fraction

    dt = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S.%f UTC")
    return dt.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3] if time_fraction \
        else dt.strftime("%d.%m.%Y %H:%M:%S")


time_fraction = False

# Define different regex patterns, e.g. for temperature, time, power, etc.

temperature_pattern = re.compile(r'(.*) ºC')
seconds_pattern = re.compile(r'(.*) s')
milliseconds_pattern = re.compile(r'(.*) ms')
current_pattern = re.compile(r'(.*) A \[(.*) Apk\]')
voltage_pattern = re.compile(r'(.*) V')
voltage_peak_pattern = re.compile(r'(.*) V \[(.*) Vpk\]')
power_avg_pattern = re.compile(r'(.*) mW \[(.*) mWavg\]')
power_pattern = re.compile(r'(.*) W')
storage_pattern = re.compile(r'\[(.*)\]')
op_mode_pattern = re.compile(r'(.*) \[(.*)\]')
match_all_pattern = re.compile(r'(.*)')

# Assign parsing patterns to each of the parameters that need specific parsing.

patterns = {
    'ambient_rtd': temperature_pattern,
    'ch1_clkheater_period': milliseconds_pattern,
    'ch1_clkheater_ticks': seconds_pattern,
    'ch1_iout': current_pattern,
    'ch1_pid_proctime': seconds_pattern,
    'ch1_pid_sp': temperature_pattern,
    'ch1_pid_ts': seconds_pattern,
    'ch1_pid_cv': power_pattern,
    'ch1_pout': power_avg_pattern,
    'ch1_pwm_ontime': milliseconds_pattern,
    'ch1_pwm_offtime': milliseconds_pattern,
    'ch1_pwm_proctime': seconds_pattern,
    'ch1_tav': temperature_pattern,
    'ch1_vdc': voltage_pattern,
    'ch1_vout': voltage_peak_pattern,
    'ch2_clkheater_period': milliseconds_pattern,
    'ch2_clkheater_ticks': seconds_pattern,
    'ch2_iout': current_pattern,
    'ch2_pid_proctime': seconds_pattern,
    'ch2_pid_sp': temperature_pattern,
    'ch2_pid_ts': seconds_pattern,
    'ch2_pout': power_avg_pattern,
    'ch2_pwm_ontime': milliseconds_pattern,
    'ch2_pwm_proctime': seconds_pattern,
    'ch2_tav': temperature_pattern,
    'ch2_vdc': voltage_pattern,
    'ch2_vout': voltage_peak_pattern,
    'fee_rtd_1': temperature_pattern,
    'fee_rtd_2': temperature_pattern,
    'fee_rtd_3': temperature_pattern,
    'fee_rtd_tav': temperature_pattern,
    'internal_rtd': temperature_pattern,
    'ni9401_external_clkheater_period': seconds_pattern,
    'ni9401_external_clkheater_timeout': seconds_pattern,
    'psu_vdc': voltage_pattern,
    'spare_rtd_1': temperature_pattern,
    'spare_rtd_2': temperature_pattern,
    'spare_rtd_3': temperature_pattern,
    'spare_rtd_tav': temperature_pattern,
    'storage_mmi': storage_pattern,
    'storage_realtime': storage_pattern,
    'tou_rtd_1': temperature_pattern,
    'tou_rtd_2': temperature_pattern,
    'tou_rtd_3': temperature_pattern,
    'tou_rtd_tav': temperature_pattern,
    'op_mode': op_mode_pattern,
    'task_is_running': op_mode_pattern,
}


def extract_value(key, value):
    """
    Extract the actual value from the string containing the value and unit plus potential
    additional info. Parsing is done with dedicated regular expressions per parameter, e.g.
    parsing a temperature takes the 'ºC' into account when extracting the actual value.

    Args:
        key (str): name of the parameter
        value (str): the value as returned by the TCS EGSE
    """

    if key not in patterns:
        return value

    match = patterns[key].search(value)
    if match is not None:
        value = match.group(1)
    return value


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """

    parser = argparse.ArgumentParser(
        prog="tcs_stamp_converter",
        description="Convert TCS EGSE Telemetry to a STAMP EGSE interface format.",
        epilog="An endpoint shall be specified as 'hostname:port'.",
    )
    parser.add_argument(
        "--version",
        action='version',
        help="Prints the version number of this script.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        help=("Print verbose messages. "
              "If this option is specified multiple times, output will be more verbose.")
    )
    parser.add_argument(
        "--tcs",
        type=str,
        required=True,
        help="The TCS EGSE endpoint, IP address or hostname and port number separated by a colon.",
    )
    parser.add_argument(
        "--stamp",
        type=str,
        help="The STAMP endpoint, IP address or hostname and port number separated by a colon.",
    )
    parser.add_argument(
        "--fractional_time", "-f",
        action='store_true',
        help="The timestamp sent to STAMP must contain 3 fractional digits.",
    )
    parser.add_argument(
        "--rate", "-r",
        type=int,
        help="The outgoing telemetry rate to STAMP [seconds].",
    )
    parser.version = f"version {__version__}"
    arguments = parser.parse_args()
    return arguments, parser


if __name__ == "__main__":

    args, parser = parse_arguments()

    # Add some sanity checks before doing the actual work

    if ':' not in args.tcs:
        print(f"{parser.prog}: error: "
              f"The endpoint for the --tcs argument shall be specified as 'hostname:port'")
        sys.exit(0)

    time_fraction = args.fractional_time
    verbose = args.verbose

    if args.stamp:
        stamp_hostname, stamp_port = args.stamp.split(':')
        stamp = STAMPInterface(stamp_hostname, int(stamp_port))
        stamp.connect()
    else:
        stamp = None

    tcs_hostname, tcs_port = args.tcs.split(':')
    tcs = TCSInterface(tcs_hostname, int(tcs_port))
    tcs.connect()

    while True:
        try:
            # Read the Telemetry from the TCS EGSE

            tm_data = tcs.read()
            tm_data = process_telemetry(tm_data)
            verbose > 1 and print(f"{tm_data=}")
            verbose > 0 and print(
                f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')} {len(tm_data)=}")

            # Write the converted data to the STAMP or stdout

            for entry in tm_data:
                line = f"{entry[0]}\t{entry[1]}\t0000\t{entry[2]}\n"
                if stamp:
                    stamp.write(bytes(line, 'utf-8'))
                else:
                    verbose == 3 and print(line, end='')
        except KeyboardInterrupt:
            break

    tcs.disconnect()
    stamp and stamp.disconnect()
