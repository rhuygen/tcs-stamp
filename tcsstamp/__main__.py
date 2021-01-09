"""
This package is specific of the PLATO Project Test Campaign for the STM model.

This script converts the telemetry stream that it received from the TCS EGSE to
a format that is understood by STAMP.

"""

import argparse
import datetime
import sys

import tcsstamp
import tcsstamp.process

from tcsstamp import STAMPInterface, TCSInterface


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """

    parser = argparse.ArgumentParser(
        prog="tcsstamp",
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
        default=0,
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
    parser.version = f"version {tcsstamp.__version__}"
    arguments = parser.parse_args()
    return arguments, parser


def main():
    args, parser = parse_arguments()

    # Add some sanity checks before doing the actual work

    if ':' not in args.tcs:
        print(f"{parser.prog}: error: "
              f"The endpoint for the --tcs argument shall be specified as 'hostname:port'")
        sys.exit(0)

    tcsstamp.process.time_fraction = args.fractional_time
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
            tm_data = tcsstamp.process.process_telemetry(tm_data)
            verbose > 2 and print(f"{tm_data=}")
            verbose > 0 and print(
                f"{datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]} "
                f"nr of telemetry values = {len(tm_data)}"
            )

            # Write the converted data to the STAMP or stdout

            for entry in tm_data:
                line = f"{entry[0]}\t{entry[1]}\t0000\t{entry[2]}\n"
                if stamp:
                    stamp.write(bytes(line, 'utf-8'))
                else:
                    print(line, end='')
        except KeyboardInterrupt:
            break

    tcs.disconnect()
    stamp and stamp.disconnect()


if __name__ == "__main__":
    main()
