#!/usr/bin/env python3

def set_MX_value(records_value):
    setPV="" 
    setPV2=""
    setPV3=""
    setPV4=""
    setPV5=""
    if int(len(records_value)) == 1:
        # get priority and value
        setPV = records_value[0]['Value'].split()

    elif int(len(records_value)) == 2:
        # get priority and value
        setPV = records_value[0]['Value'].split()
        setPV2 = records_value[1]['Value'].split()  

    elif int(len(records_value)) == 3:
        # get priority and value
        setPV = records_value[0]['Value'].split()
        setPV2 = records_value[1]['Value'].split()
        setPV3 = records_value[2]['Value'].split() 

    elif int(len(records_value)) == 4:
        # get priority and value
        setPV = records_value[0]['Value'].split()
        setPV2 = records_value[1]['Value'].split()
        setPV3 = records_value[2]['Value'].split()
        setPV4 = records_value[3]['Value'].split()

    elif int(len(records_value)) == 5:
        # get priority and value
        setPV = records_value[0]['Value'].split()
        setPV2 = records_value[1]['Value'].split()
        setPV3 = records_value[2]['Value'].split()
        setPV4 = records_value[3]['Value'].split()
        setPV5 = records_value[4]['Value'].split()

    return setPV, setPV2, setPV3, setPV4, setPV5