#!/usr/bin/env python3

import re

# fix replace '"' with ''  and fix DKIM value
def fix_TXT_Value(input_value):
    value = input_value.replace('"', '')
    if re.match(r'.*DKIM', value):
        value = '; '.join(re.sub(pattern=r'\s+|\\;', repl='', string=value).split(';')).strip()
    return value

def set_TXT_value(record_values):
    value1 = ""
    value2 = ""
    value3 = ""
    value4 = ""
    value5 = ""
    value6 = ""
    value7 = ""
    value8 = ""
    value9 = ""
    value10 = ""
    if (len(record_values)) > 0:
        value1 = fix_TXT_Value(record_values[0]['Value'].replace('"', ''))
    if (len(record_values)) > 1:
        value2 = fix_TXT_Value(record_values[1]['Value'].replace('"', ''))
    if (len(record_values)) > 2:
        value3 = fix_TXT_Value(record_values[2]['Value'].replace('"', ''))
    if (len(record_values)) > 3:
        value4 = fix_TXT_Value(record_values[3]['Value'].replace('"', ''))
    if (len(record_values)) > 4:
        value5 = fix_TXT_Value(record_values[4]['Value'].replace('"', ''))
    if (len(record_values)) > 5:
        value6 = fix_TXT_Value(record_values[5]['Value'].replace('"', ''))
    if (len(record_values)) > 6:
        value7 = fix_TXT_Value(record_values[6]['Value'].replace('"', ''))
    if (len(record_values)) > 7:
        value8 = fix_TXT_Value(record_values[7]['Value'].replace('"', ''))
    if (len(record_values)) > 8:
        value9 = fix_TXT_Value(record_values[8]['Value'].replace('"', ''))
    if (len(record_values)) == 10:
        value10 = record_values[9]['Value'].replace('"', '')
    return value1, value2, value3, value4, value5, value6, value7, value8, value9, value10
