"""
This package is specific of the PLATO Project Test Campaign for the STM model.

This script converts the telemetry stream that it received from the TCS EGSE to
a format that is understood by STAMP.

"""

import argparse
import datetime
import operator
import sys
import time

import tcsstamp
import tcsstamp.process
from tcsstamp import STAMPInterface, TCSInterface, print_table


class BooleanAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(BooleanAction, self).__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, not option_string.startswith('--no'))


def parse_arguments():
    """
    Prepare the arguments that are specific for this application.
    """

    parser = argparse.ArgumentParser(
        prog="tcs_stamp",
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
        "--rich",
        action='store_true',
        help="Use the 'rich' module to pretty print a table for the Housekeeping values.",
    )
    parser.add_argument(
        "--rate", "-r",
        type=int, default=0,
        help="The outgoing telemetry rate to STAMP [seconds].",
    )
    parser.add_argument(
        "--clear", "--no-clear", dest='clear',
        type=bool, action=BooleanAction, default=True,
        help="Clear the housekeeping history on each new read.",
    )
    parser.add_argument(
        "--sort-by-name", dest='sort_by_name',
        action="store_true",
        help="Sort the HK table by name instead of time.",
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
    rate = args.rate
    rich = args.rich

    if args.stamp:
        stamp_hostname, stamp_port = args.stamp.split(':')
        stamp = STAMPInterface(stamp_hostname, int(stamp_port))
        stamp.connect()
    else:
        stamp = None

    tcs_hostname, tcs_port = args.tcs.split(':')
    tcs = TCSInterface(tcs_hostname, int(tcs_port))
    tcs.connect()

    start = time.perf_counter()

    if args.sort_by_name:
        sort_key = tcsstamp.process.name_key
    else:
        sort_key = tcsstamp.process.timestamp_key

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

            if time.perf_counter() - start > rate:
                sorted_tm_data = sorted(tm_data.values(), key=sort_key)
                for entry in sorted_tm_data:
                    line = f"{entry[0]}\t{entry[1]}\t0000\t{entry[2]}\n"
                    if stamp:
                        stamp.write(bytes(line, 'utf-8'))
                    elif not rich:
                        print(line, end='')
                if not stamp and rich:
                    print_table(sorted_tm_data)
                if args.clear:
                    tcsstamp.process.housekeeping.clear()
                start = time.perf_counter()

        except KeyboardInterrupt:
            break

    tcs.disconnect()
    stamp and stamp.disconnect()


if __name__ == "__main__":
    main()
