# TCS EGSE STAMP Converter

This package converts the telemetry stream from the TCS EGSE to a STAMP specific interface format.

The TCS EGSE is a thermal control equipment that will be used to control the temperature of the PLATO Camera during ground testing.

## How to use

    $ python -m tcsstamp -h
    usage: tcs_stamp_converter [-h] [--version] [--verbose] --tcs TCS [--stamp STAMP] [--fractional_time] [--rate RATE]

    Convert TCS EGSE Telemetry to a STAMP EGSE interface format.

    optional arguments:
      -h, --help            show this help message and exit
      --version             Prints the version number of this script.
      --verbose, -v         Print verbose messages. If this option is specified multiple times, output will be more verbose.
      --tcs TCS             The TCS EGSE endpoint, IP address or hostname and port number separated by a colon.
      --stamp STAMP         The STAMP endpoint, IP address or hostname and port number separated by a colon.
      --fractional_time, -f
                            The timestamp sent to STAMP must contain 3 fractional digits.
      --rate RATE, -r RATE  The outgoing telemetry rate to STAMP [seconds].

    An endpoint shall be specified as 'hostname:port'.
