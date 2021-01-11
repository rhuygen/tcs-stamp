# TCS EGSE STAMP Converter

This package converts the telemetry stream from the TCS EGSE to a STAMP specific interface format.

The TCS EGSE is a thermal controller that will be used to control the temperature of the 
PLATO Camera during ground testing. STAMP is a software package that provides data handling facilities 
to support thermal tests on spacecraft equipment.

## Install

    $ python3 -m pip install tcs-stamp-converter
          
If you need to install a new version of the package:

    $ python3 -m pip install --upgrade tcs-stamp-converter

## How to use
    
    $ tcs_stamp -h
    usage: tcs_stamp [-h] [--version] [--verbose] --tcs TCS [--stamp STAMP] [--fractional_time] [--rate RATE]
    
    Convert TCS EGSE Telemetry to a STAMP EGSE interface format.
    
    optional arguments:
      -h, --help            show this help message and exit
      --version             Prints the version number of this script.
      --verbose, -v         Print verbose messages. If this option is specified multiple times, output will be more verbose.
      --tcs TCS             The TCS EGSE endpoint, IP address or hostname and port number separated by a colon.
      --stamp STAMP         The STAMP endpoint, IP address or hostname and port number separated by a colon.
      --fractional_time, -f
                            The timestamp sent to STAMP must contain 3 fractional digits.
      --rich                Use the 'rich' module to pretty print a table for the Housekeeping values.
      --rate RATE, -r RATE  The outgoing telemetry rate to STAMP [seconds].
    
    An endpoint shall be specified as 'hostname:port'.

NOTE: When running the script on Windows, the script might not be found because e.g. the PATH is not pointing to the installation. You will get an error saying: _'tcs_stamp' is not recognized as an internal or external command, operable program or batch file._ In that case, fix the PATH to find the script or you can run the script as follows:

    python -m tcsstamp -h

**Notice there is no underscore in the _tcsstamp_ name if called like this.**

## Description

The script is a bridge between the TCS EGSE, which provides the telemetry as a stream of housekeeping values 
with their associated time, and STAMP which provides data handling functionality. The output format of the 
TCS EGSE doesn't match the input format of STAMP. This script serves as a bridge converting the TCS EGSE 
output format into the required STAMP input format.

The hostname and port should be known for both systems. The script connects to the TCS EGSE using a plain 
unix socket connection. The hostname and TCP port must be given as an argument. The script also connects to STAMP 
when the hostname and port are given as an argument, otherwise the data is sent to stdout.

An example usage in a local network might look like this:

    $ tcs_stamp --tcs 10.33.178.10:6666 --stamp 10.33.178.12:4444

You can use the simple echo server which is also installed with the package. This server will echo the received stream of data to stdout. The echo_server listens to port 4444.

    $ echo_server 
    Connected by ('127.0.0.1', 64725)
    '10.01.2021 16:12:01\tch1_pid_cv\t0000\t15.0000\n10.01.2021 16:12:01\tch1_pid_sp\t0000\t40.0000\n10.01.2021 16:12:01\tch1_pid_ts\t0000\t1.0000\n10.01.2021 16:12:01\tch2_pid_sp\t0000\t0.0000\n10.01.2021 16:12:01\tch2_pid_ts\t0000\t12.5000\n10.01.2021 16:12:01\tch1_pid_proctime\t0000\t11.7856\n10.01.2021 16:12:01\tch1_pwm_proctime\t0000\t11.7974\n10.01.2021 16:12:01\tch2_clkheater_ticks\t0000\t172120.8617\n10.01.2021 16:12:01\tch2_pid_proctime\t0000\t0.0356\n10.01.2021 16:12:01\tcpuload_realtime\t0000\tCPU1: 65.4% CPU2: 70.0% MEM: 1.4% free [3.5MB/244.4MB] CORE: 112.1MB\n10.01.2021 16:12:01\tni9401_external_clkheater_timeout\t0000\t171.4284\n10.01.2021 16:12:01\tch1_heater_status\t0000\t00001\n10.01.2021 16:12:01\tch1_pid_error\t0000\t001\n10.01.2021 16:12:01\tch2_heater_status\t0000\t00000\n10.01.2021 16:12:01\tch2_pid_error\t0000\t001\n10.01.2021 16:12:01\telapsed_time\t0000\t1d23h37m10s\n10.01.2021 16:12:01\tlogging_files\t0000\t2820\n10.01.2021 16:12:01\tlogging_packets\t0000\t13291709\n'
    '10.01.2021 16:12:01\top_mode\t0000\t6\n10.01.2021 16:12:01\tstart_time\t0000\t20210108 16:3451 UTC\n10.01.2021 16:12:01\tsync_status\t0000\t000000011\n10.01.2021 16:12:01\ttask_is_running\t0000\t1\n10.01.2021 16:12:01\tch1_iout\t0000\t0.586\n10.01.2021 16:12:01\tch1_vdc\t0000\t28.198\n10.01.2021 16:12:01\tch1_vout\t0000\t24.589\n10.01.2021 16:12:01\tch2_iout\t0000\t1.195\n10.01.2021 16:12:01\tch2_vdc\t0000\t28.173\n10.01.2021 16:12:01\tch2_vout\t0000\t28.093\n10.01.2021 16:12:01\tpsu_status\t0000\t0001\n10.01.2021 16:12:01\tpsu_vdc\t0000\t28.396\n10.01.2021 16:12:01\tch1_pout\t0000\t14399.8\n10.01.2021 16:12:01\tch2_pout\t0000\t33568.3\n10.01.2021 16:12:01\tambient_rtd\t0000\t20.8579\n10.01.2021 16:12:01\tfee_rtd_1\t0000\t0.1757\n10.01.2021 16:12:01\tfee_rtd_1_status\t0000\t00001\n10.01.2021 16:12:01\tfee_rtd_2\t0000\t0.1627\n10.01.2021 16:12:01\tfee_rtd_2_status\t0000\t00001\n10.01.2021 16:12:01\tfee_rtd_3\t0000\t0.1907\n10.01.2021 16:12:01\tfee_rtd_3_status\t0000\t00001\n10.01.2021 16:12:01\tfee_rtd_status\t0000\t00001\n10.01.2021 16:12:01\tfee_rtd_tav\t0000\t0.1757\n10.01.2021 16:12:01\tinternal_rtd\t0000\t28.2824\n10.01.2021 16:12:01\tspare_rtd_1\t0000\t0.1213\n10.01.2021 16:12:01\tspare_rtd_1_status\t0000\t00001\n10.01.2021 16:12:01\tspare_rtd_2\t0000\t0.1506\n10.01.2021 16:12:01\tspare_rtd_2_status\t0000\t00001\n10.01.2021 16:12:01\tspare_rtd_3\t0000\t0.1535\n10.01.2021 16:12:01\tspare_rtd_3_status\t0000\t00001\n10.01.2021 16:12:01\tspare_rtd_status\t0000\t00001\n'

When you don't specify the `--stamp` option, the housekeeping will be sent to stdout:

    $ tcs_stamp --tcs localhost:6666
    10.01.2021 12:50:07	storage_mmi	0000	681.5GB
    10.01.2021 12:50:10	ambient_rtd	0000	20.8766
    10.01.2021 12:50:10	fee_rtd_1	0000	0.1733
    10.01.2021 12:50:10	fee_rtd_1_status	0000	00001
    10.01.2021 12:50:10	fee_rtd_2	0000	0.1655
    10.01.2021 12:50:10	fee_rtd_2_status	0000	00001
    10.01.2021 12:50:10	fee_rtd_3	0000	0.1881
    10.01.2021 12:50:10	fee_rtd_3_status	0000	00001
    10.01.2021 12:50:10	fee_rtd_status	0000	00001
    10.01.2021 12:50:10	fee_rtd_tav	0000	0.1733

If you like to see the housekeeping in a proper table, you can use the `--rich` option. That will print out a table like below instead of the output above. Please note that the 'rich' module must be pip installed for this to work.

![Table of All Telemetry](https://github.com/rhuygen/tcsstamp/blob/main/img/screenshot-all-telemetry.png)

The STAMP interface expects the timestamp, sensor name, sensor number, and value to be separated with a TAB character and each entry ended with a newline. That is what you see in the above example, only the hk number is ignored by STAMP and therefore left 0000 for all hk entries.     

The timestamp is given in the format `'DD.MM.YYYY HH.MM.SS'`, with optionally a 3 fractional digits appended when the `--fractional_time` option is given.

    tcs_stamp --tcs localhost:6666 --fractional_time
    10.01.2021 13:01:04.949	storage_mmi	0000	681.5GB
    10.01.2021 13:01:07.836	ch1_pid_cv	0000	15.0000
    10.01.2021 13:01:07.836	ch1_pid_sp	0000	40.0000
    10.01.2021 13:01:07.836	ch1_pid_ts	0000	1.0000
    10.01.2021 13:01:07.836	ch2_pid_sp	0000	0.0000
    10.01.2021 13:01:07.836	ch2_pid_ts	0000	12.5000

Telemetry is sent out by the TCS EGSE at 1Hz and only values that have changed are transmitted. When you need a lower telemetry rate, use the `--rate` option which basically defines the number of seconds to wait before sending the next batch of housekeeping. The following command will send housekeeping out every 10 seconds.

    $ tcs_stamp --tcs 10.33.178.10:6666 --rate 10 

## Errors

You can expect the following error when:

**BrokenPipeError: [Errno 32] Broken pipe**: When the connection to STAMP or the `echo_server` was terminated at their side.

**ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host** This is the same as a BrokenPipeError, but on Windows.

**ConnectionError: STAMP: Connection refused to localhost:25001.**: When no application is listening on the other side, e.g. STAMP or `echo_server` not started? This could also be the case for TCS EGSE in which case you should check if the TCS EGSE is switched on.

**TimeoutError: STAMP: socket timeout error for 10.33.178.12:25001**: This usually happens when the IP address is wrong or unreachable. Check if you can `ping` to that IP address.

## Glossary

* PLATO: PLAnetary Transits and Oscillations of stars
* EGSE: Electric Ground Support Equipment
* STAMP: System for Thermal Analysis, Measurement, and Power supply control
