"""Process Telemetry data."""
import datetime
import logging
import re
from typing import Dict, List

logger = logging.getLogger()

housekeeping = dict()


def process_telemetry(data: str) -> Dict:
    """
    Process the housekeeping telemetry that was received from the TCS EGSE.

    Args:
        data (str): a string containing the telemetry from the TCS EGSE.

    Returns:
        A dictionary where the key is the housekeeping parameter name and the value is a list
        containing the timestamp, name, and value of the housekeeping parameter. Only the last
        sample in kept in the dictionary.
    """
    global housekeeping

    data = data.split('\x03')
    data = [x for x in data if x]
    if not data:
        logger.warning("Format error: no new housekeeping values received.")
        return housekeeping
    data = data[0].split('\r\n')
    data = [x.split('\t') for x in data]

    # We do not need to sort by timestamp since the data is already sorted by time.
    # The
    # data = sorted(data, key=operator.itemgetter(0))  # sort by date

    for x in data:
        date = convert_date(x[0])
        name = x[1]
        value = extract_value(x[1], x[2])
        housekeeping[name] = [date, name, value]

    return housekeeping


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
    if time_fraction:
        return dt.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
    else:
        return dt.strftime("%d.%m.%Y %H:%M:%S")


def timestamp_key(items: List) -> float:
    """
    Return a timestamp of the first element in the list.
    The can be used as a key in the sorted function.
    """
    date = items[0]
    fmt = "%d.%m.%Y %H:%M:%S" if len(date) < 20 else "%d.%m.%Y %H:%M:%S.%f"
    dt = datetime.datetime.strptime(date, fmt)
    return dt.timestamp()


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
