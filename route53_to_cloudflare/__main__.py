#!/usr/bin/env python3

##TODO jinja templates to spesific folders

import argparse
from threading import activeCount
import jinja2
import re
import boto3
import os
from .mod.MX import set_MX_value
from .mod.TXT import fix_TXT_Value, set_TXT_value

globals
ENV = jinja2.Environment(loader=jinja2.PackageLoader(
    'route53_to_cloudflare', 'templates'))

# used to count records that were created
resources = {
    'A': {},
    'AAAA': {},
    'CNAME': {},
    'MX': {},
    'NS': {},
    'SPF': {},
    'SRV': {},
    'TXT': {},
}

def set_ZoneName(zone):
    # set zone name
    zoneName=zone['Name'].replace('.', '_')
    # slice the last '_' from the folder name
    if zone['Name'].endswith('.'):
        zoneName=zoneName[0:-1]
    return zoneName

def set_ResourceName(record):
    """sets the name of the resources in 
    for example resources['A'][the name of the resource]"""
    if record['Name'].endswith('.'):
        name = record['Name'][0:-1].replace('.', '_')
    else:
        name = record['Name'].replace('.', '_')
    if re.match(pattern=r'^\d', string=name):
        name = '_{}'.format(name)
    if name.startswith('\\052'):
        name = name.replace('\\052', 'star')
    return name

# sets the of the name of the record
# removing the . at the end of the name
# changeing boto3 output of \052 back to star
# if subDomain - get only the subDomain name - remove the xxx.com from the name 
def set_RecordName(name):
    if name.startswith('\\052'):
        recordName = name.replace('\\052', '*')
    else:
        recordName = name
        
    if recordName.endswith('.'):
        recordName = recordName[0:-1]

    # if 2 means that it must be the parrent zone so we dont need any change
    # else means we have more than 1 subdomain so we will add the subdomains name for example test.tikal.updater.com ->
    # the name of the record will be test.tikal -> we will strip the last 2 names
    if len(recordName.split('.')) != 2:
        subDomainRecordName = ""
        for i in range(0, len(recordName.split('.'))-2):
            subDomainRecordName = subDomainRecordName +"."+ recordName.split('.')[i]
        # set records name after the loop
        recordName = subDomainRecordName[1:]
    return recordName

def removeDotFromEnd(value):
    """Remove trailing . for values"""
    if value.endswith('.'):
        value=value[0:-1]
    return value


def render_single_value_records(temp_path, zoneName, recordName, ttl, value, resource, aws_account_id,):
    
    template = ENV.get_template(f'{temp_path}.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/{temp_path}.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, value=value, 
        terrafromResource=resource, zone_id=zoneName))


def render_MX_records(temp_path, zoneName, recordName, ttl, resource, aws_account_id,
    value1, praiority1, value2="", praiority2="", value3="", praiority3="", 
    value4="", praiority4="", value5="", praiority5=""):
    
    template = ENV.get_template(f'{temp_path}.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/MX.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
                value1=value1, priority1=praiority1, 
                value2=value2, priority2=praiority2,
                value3=value3, priority3=praiority3,
                value4=value4, priority4=praiority4,
                value5=value5, priority5=praiority5,
                terrafromResource=resource, zone_id=zoneName)) 


def render_NS_records(temp_path, zoneName, recordName, ttl, resource, aws_account_id, 
    value1, value2="", value3="", value4=""):

    
    template = ENV.get_template(f'{temp_path}.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/NS.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
        value1=value1, value2=value2, value3=value3,
        value4=value4,
        terrafromResource=resource, zone_id=zoneName)) 


def render_TXT_records(temp_path, zoneName, recordName, ttl, resource, aws_account_id,
    value1, value2="", value3="", 
    value4="", value5="", value6="", 
    value7="", value8="", value9="", 
    value10=""):

    
    template = ENV.get_template(f'{temp_path}.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/TXT.tf', 'a') as target:
        target.write(template.render(name=recordName, ttl=ttl, 
        value1=value1, value2=value2, value3=value3,
        value4=value4, value5=value5, value6=value6,
        value7=value7, value8=value8, value9=value9,
        value10=value10,
        terrafromResource=resource, zone_id=zoneName)) 

# addes resources to resources['A'] 
def a(zoneName, record, aws_account_id):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'A')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in record:
            # add to A record dictinary
            resources['A'][resource] = { 'name': recordName }

            render_single_value_records("A", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource, aws_account_id)
        elif 'AliasTarget' in record:
            # add to CNAME record dictinary
            resources['CNAME'][resource] = { 'name': recordName }

            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource, aws_account_id)   
        return True
    return False

# addes resources to resources['AAAA'] 
def aaaa(zoneName, record, aws_account_id):
    match = (record['Type'] == 'AAAA')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        if 'ResourceRecords' in  record:
            # add to AAAA record dictinary
            resources['AAAA'][resource] = { 'name': recordName }                 
            render_single_value_records("AAAA", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource), aws_account_id
        elif 'AliasTarget' in record:
            # add to CNAME record dictinary
            resources['CNAME'][resource] = { 'name': recordName }
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource, aws_account_id) 
        return True
    return False

# addes resources to resources['CNAME'] 
def cname(zoneName, record, aws_account_id):
    # match = re.match(CNAME, record)
    match = (record['Type'] == 'CNAME')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        # add to CNAME record dictinary
        resources['CNAME'][resource] = { 'name': recordName }  
        if 'ResourceRecords' in  record:   
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['ResourceRecords'][0]['Value']), resource, aws_account_id)
        elif 'AliasTarget' in record:
            render_single_value_records("CNAME", zoneName, recordName, 1, 
                removeDotFromEnd(record['AliasTarget']['DNSName']), resource, aws_account_id)
        return True
    return False

# addes resources to resources['MX'] 
def mx(zoneName, record, aws_account_id):
    # match = re.match(MX, record)
    match = (record['Type'] == 'MX')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['MX'][resource] = { 'name': recordName } 
        # set priority and value
        setPV, setPV2, setPV3, setPV4, setPV5 = set_MX_value(record['ResourceRecords'])

        x = int(len(record['ResourceRecords']))
        if x == 1:
            render_MX_records("MX", zoneName, recordName, 1, resource, aws_account_id,
                removeDotFromEnd(setPV[1]), setPV[0])

        elif x == 2:
            render_MX_records("MX2", zoneName, recordName, 1, resource, aws_account_id, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0])

        elif x == 3:
            render_MX_records("MX3", zoneName, recordName, 1, resource, aws_account_id, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0])

        elif x == 4:
            render_MX_records("MX4", zoneName, recordName, 1, resource, aws_account_id, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0],
                removeDotFromEnd(setPV4[1]), setPV4[0])

        elif x == 5:
            render_MX_records("MX5", zoneName, recordName, 1, resource, aws_account_id, 
                removeDotFromEnd(setPV[1]), setPV[0],
                removeDotFromEnd(setPV2[1]), setPV2[0], 
                removeDotFromEnd(setPV3[1]), setPV3[0],
                removeDotFromEnd(setPV4[1]), setPV4[0],
                removeDotFromEnd(setPV5[1]), setPV5[0])
        return True
    return False



# adds resources to resources['TXT'] 
def txt(zoneName, record, aws_account_id):
    # match = re.match(TXT, record)
    match = (record['Type'] == 'TXT')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['TXT'][resource] = { 'name': recordName }
        # set TXT value 
        value1, value2, value3, value4, value5, value6,value7, value8, value9, value10 = set_TXT_value(record['ResourceRecords'])

        if (len(record['ResourceRecords'])) == 1:

            render_TXT_records("TXT", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1)

        elif (len(record['ResourceRecords'])) == 2:

            render_TXT_records("TXT2", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2)

        elif (len(record['ResourceRecords'])) == 3:

            render_TXT_records("TXT3", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3)

        elif (len(record['ResourceRecords'])) == 4:

            render_TXT_records("TXT4", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4)

        elif (len(record['ResourceRecords'])) == 5:

            render_TXT_records("TXT5", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5)

        elif (len(record['ResourceRecords'])) == 6:

            render_TXT_records("TXT6", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6)

        elif (len(record['ResourceRecords'])) == 7:

            render_TXT_records("TXT7", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7)

        elif (len(record['ResourceRecords'])) == 8:

            render_TXT_records("TXT8", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8)


        elif (len(record['ResourceRecords'])) == 9:
            
            render_TXT_records("TXT9", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9)

        elif (len(record['ResourceRecords'])) == 10:

            render_TXT_records("TXT10", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                value10=value10)

        elif (len(record['ResourceRecords'])) > 10:
            
            render_TXT_records("TXT10", zoneName, recordName, 1, resource, aws_account_id,
                value1=value1, value2=value2, value3=value3, 
                value4=value4, value5=value5, value6=value6, 
                value7=value7, value8=value8, value9=value9, 
                value10="##TODO_MORE_THAN_10_VALUES")
        return True
    return False

# addes resources to resources['NS'] 
def ns(zoneName, record, aws_account_id):
    # match = re.match(NS, record)
    print(record)
    match = (record['Type'] == 'NS')
    if match:
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['NS'][resource] = { 'name': recordName }  
      # check the number of values in the ns record
        x = int(len(record['ResourceRecords']))
        if x == 1:
            resources['NS'][resource] = {'name': recordName}
            
            render_NS_records("NS", zoneName, recordName, 1, resource, aws_account_id,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']))

        elif x == 2:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS2", zoneName, recordName, 1, resource, aws_account_id,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']))
        
        elif x == 3:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS3", zoneName, recordName, 1, resource, aws_account_id,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']))

        elif x == 4:           
            resources['NS'][resource] = {'name': recordName}

            render_NS_records("NS3", zoneName, recordName, 1, resource, aws_account_id,
                value1=removeDotFromEnd(record['ResourceRecords'][0]['Value']), 
                value2=removeDotFromEnd(record['ResourceRecords'][1]['Value']), 
                value3=removeDotFromEnd(record['ResourceRecords'][2]['Value']),
                value4=removeDotFromEnd(record['ResourceRecords'][3]['Value']))
                 
        return True
    return False

# addes resources to resources['SPF'] 
def spf(zoneName, record, aws_account_id):
    # match = re.match(A, record)
    print(record)
    match = (record['Type'] == 'SPF')
    if match:
        
        # fix replace '"' with ''  and fix DKIM value
        value = fix_TXT_Value(record['ResourceRecords'][0]['Value'])
        resource = set_ResourceName(record)
        recordName = set_RecordName(record['Name'])
        resources['SPF'][resource] = { 'name': recordName }  

        render_single_value_records("SPF", zoneName, recordName, 1, value, resource, aws_account_id)

        return True
    return False

# input parametes for script
def parse_arguments():
    """
    Function to handle argument parser configuration (argument definitions, default values and so on).
    :return: :obj:`argparse.ArgumentParser` object with set of configured arguments.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-id',
        '--account_id',
        help='cloudlfare account id',
        default=str(),
        required=True,
        type=str
    )
    parser.add_argument(
        '-ns',
        '--cloudflare_ns_record',
        help='cloudlfare ns record, required for nslookup testing. Example Record: "guy.ns.cloudflare.com"',
        default=str(),
        required=True,
        type=str
    )
    parser.add_argument(
        '-awsID',
        '--aws_account_id',
        help='aws account id',
        default=str(),
        required=True,
        type=str
    )
    return parser

# parsing through the records
def parse_zone(zone, rs, aws_account_id):
    for record in rs['ResourceRecordSets']:
        print(record)
        # if not comment(record=record):
        if a(set_ZoneName(zone), record, aws_account_id):
            continue
        if aaaa(set_ZoneName(zone), record, aws_account_id):
            continue
        if cname(set_ZoneName(zone), record, aws_account_id):
            continue
        if mx(set_ZoneName(zone), record, aws_account_id):
            continue
        if txt(set_ZoneName(zone), record, aws_account_id):
            continue
        if spf(set_ZoneName(zone), record, aws_account_id):
            continue
        # exclude NS records of the parent zone
        if record['Name'] != zone['Name'] and ns(set_ZoneName(zone), record, aws_account_id):
            continue
        print(record)

# render for all files
def render(zone, rs, zoneName, account_id, cloudflare_ns_record, aws_account_id):

    # main.tf
    template = ENV.get_template('main.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/main.tf', 'w') as target:
        target.write(template.render(account_id=account_id, zoneName=zoneName))

    # Zone.tf
    # cloudflare_zone_name=zoneName - replacing the _ with .
    template = ENV.get_template('Zone.tf.j2')
    with open(f'./{aws_account_id}/{zoneName}/zone.tf', 'w') as target:
        target.write(template.render(terrafromResource=zoneName, cloudflare_zone_name=zoneName.replace('_', '.')))

    # countRecords.txt
    recordA         = len(resources['A'])
    recordAAAA      = len(resources['AAAA'])
    recordCANME     = len(resources['CNAME'])
    recordMX        = len(resources['MX'])
    recordSRV       = len(resources['SRV'])
    recordTXT       = len(resources['TXT'])
    recordNS        = len(resources['NS'])
    recordSPF       = len(resources['SPF'])
    recordsCreated  = recordA + recordAAAA + recordCANME + recordMX + recordSRV + recordTXT + recordNS + recordSPF
    awsArecord      = 0
    awsAAAArecord   = 0
    awsMXrecord     = 0
    awsTXTrecord    = 0
    awsCNAMErecord  = 0
    awsSRVrecord    = 0
    awsNSrecord     = 0
    awsSPFrecord    = 0
    for i in rs['ResourceRecordSets']:
        if i['Type'] == 'A':
            awsArecord += 1
        elif i['Type'] == 'NS':
            awsNSrecord += 1
        elif i['Type'] == 'AAAA':
            awsAAAArecord += 1
        elif i['Type'] == 'MX':
            awsMXrecord += 1
        elif i['Type'] == 'TXT':
            awsTXTrecord += 1
        elif i['Type'] == 'CNAME':
            awsCNAMErecord += 1
        elif i['Type'] == 'SRV':
            awsSRVrecord += 1
        elif i['Type'] == 'SPF':
            awsSPFrecord += 1

    template = ENV.get_template('countRecords.txt.j2')
    with open(f'./{aws_account_id}/{zoneName}/countRecords.txt', 'w') as target:
        target.write(template.render(recordsCreated=recordsCreated, recordA=recordA, recordAAAA=recordAAAA,
        recordCANME=recordCANME, recordMX=recordMX, recordSRV=recordSRV, recordTXT=recordTXT, 
        recordNS=recordNS, awsArecord=awsArecord, awsAAAArecord=awsAAAArecord, awsMXrecord=awsMXrecord, 
        awsTXTrecord=awsTXTrecord, awsCNAMErecord=awsCNAMErecord, awsSRVrecord=awsSRVrecord, awsNSrecord=awsNSrecord,
        awsSPFrecord=awsSPFrecord, recordSPF=recordSPF, rs=(len(rs['ResourceRecordSets']))))
    
    # 0 subzones
    if recordNS == 0 and len(zoneName.split('_')) == 2:
        with open(f'./{aws_account_id}/{aws_account_id}_noSubZones.txt', 'a') as target:
            target.write(zoneName.replace('_', '.') + "\n")
    else:
        with open(f'./{aws_account_id}/{aws_account_id}_zonesWithSubDomains.txt', 'a') as target:
            target.write(zoneName.replace('_', '.') + "\n")

    # nslookup                
    for item in resources:
        # create file only for the necessary records
        if not len(resources[item]) == 0:

            parentDomain=zoneName.replace('_', '.')
            #set parent domain name if subDomain has seperated Subzone
            if int(len(zoneName.split("_"))) > 2:
                parentDomainName = ""
                for i in range(len(zoneName.split('_'))-2, len(zoneName.split('_'))):
                    parentDomainName = parentDomainName +"."+ zoneName.split('_')[i]
                    # remove the '.' from the start of the parent domain name
                    parentDomain = parentDomainName[1:].replace('_', '.')

            template = ENV.get_template(f'nslookup{item}.sh.j2')
            with open(f"./{aws_account_id}/{zoneName}/validateRecords/nslookup{item}.sh", 'a') as target:
                target.write(template.render(resources=resources[item], parentDomain=parentDomain, 
                cloudflare_ns_record=cloudflare_ns_record, space=" "))

            # Read in the file
            with open(f"./{aws_account_id}/{zoneName}/validateRecords/nslookup{item}.sh", 'r') as file :
                filedata = file.read()

            # Replace the target string
            # replace duplicate parent domain name in nslookup file
            # for example: facebook.com.facebook.com -> facebook.com
            filedata = filedata.replace(f"{zone['Name'][0:-1]}.{zone['Name'][0:-1]}", f"{zone['Name'][0:-1]}")

            # Write the file out again
            with open(f"./{aws_account_id}/{zoneName}/validateRecords/nslookup{item}.sh", 'w') as file:
                file.write(filedata)

def main():
    # get input parameters
    args = parse_arguments().parse_args()
    account_id = args.account_id
    cloudflare_ns_record = args.cloudflare_ns_record
    aws_account_id = args.aws_account_id
    
    # get zones list
    client = boto3.client('route53')
    hostedzone=client.list_hosted_zones()

    # check if folder exists
    if not os.path.exists(f'./{aws_account_id}'):
        os.mkdir(f'./{aws_account_id}')
    
    # filter out private domains
    for zone in hostedzone["HostedZones"]:
        if not zone["Config"]["PrivateZone"]:
            # get all the records from the zone
            rs=client.list_resource_record_sets(HostedZoneId=zone["Id"],MaxItems='2000')

            # set zone name for folder name and resource name
            zoneName = set_ZoneName(zone)
            # check if folder exists
            if not os.path.exists(f'./{aws_account_id}/{zoneName}'):
                os.mkdir(f'./{aws_account_id}/{zoneName}')

            # check if folder exists
            if not os.path.exists(f'./{aws_account_id}/{zoneName}'+"/validateRecords"):
                os.mkdir(f'./{aws_account_id}/{zoneName}'+"/validateRecords")
            
            # parsing through the records list and write records to 'record_type.tf'
            parse_zone(zone, rs, aws_account_id)

            # validation files, zone file, main file
            render(zone, rs, zoneName, account_id, cloudflare_ns_record, aws_account_id)

            # terraform fmt check
            os.system('cd ./'+aws_account_id+'/'+zoneName+' && terraform fmt && cd -')

            # change premissions:
            os.system('cd ./'+aws_account_id+'/'+zoneName+'/validateRecords && chmod +x *.sh && cd -')

            # empty resources dict for new zone
            for i in resources:
                resources[i].clear()
                
        # if it's a private zone - write the filtered zone name to file
        else:
            zoneName = set_ZoneName(zone)
            with open(f'./{aws_account_id}/{aws_account_id}_PrivateZoneFiltered.txt', 'a') as target:
                target.write(zoneName.replace('_', '.') + "\n")


if __name__ == '__main__':
    main()
