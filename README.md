# TCS EGSE STAMP Converter

This package converts the telemetry stream from the TCS EGSE to a STAMP specific interface format.

The TCS EGSE is a thermal controller that will be used to control the temperature of the 
PLATO Camera during ground testing. STAMP is a software package that provides data handling facilities 
to support thermal tests on spacecraft equipment.

## Install

    $ python3 -m pip install tcs-stamp-converter


## How to use
    
    $ tcsstamp -h
    usage: tcsstamp [-h] [--version] [--verbose] --tcs TCS [--stamp STAMP] [--fractional_time] [--rate RATE]
    
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

## Description

The script is a bridge between the TCS EGSE, which provides the telemetry as a stream of housekeeping values 
with their associated time, and STAMP which provides data handling functionality. The output format of the 
TCS EGSE doesn't match the input format of STAMP. This script serves as a bridge converting the TCS EGSE 
output format into the required STAMP input format.

The hostname and port should be known for both systems. The script connects to the TCS EGSE using a plain 
unix socket connection. The hostname and TCP port must be given as an argument. The script also connects to STAMP 
when the hostname and port are given as an argument, otherwise the data is sent to stdout.

An example usage in a local network might look like this:

    $ tcsstamp --tcs 10.33.178.10:6666 --stamp 10.33.178.12:4444


## Glossary

* PLATO: PLAnetary Transits and Oscillations of stars
* EGSE: Electric Ground Support Equipment
* STAMP: System for Thermal Analysis, Measurement, and Power supply control
