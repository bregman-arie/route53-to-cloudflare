# route_53_cloudflare

Our Python tool easily gets all the route53 zones and recods of spesific aws account 
and parse them into Terraform cloudflare resources.

In addition the tool will create tests to validate the new records in cloudflare 
compared with the current global DNS records, using nslookup.

To make the result code organized, we separated the terraform files based on DNS records types (for example A.tf, CANME.tf).
If you would prefer to use one terraform file swith branch to oneTF.
oneTF - records will be writen to one file named records.tf. The records will be orderd by type.

## Installation

To install our version of this project, just clone the repository and install the
module:

```bash
git clone https://github.com/GuySaar8/route53-to-cloudflare.git
cd route_53_cloudflare
python3 setup.py install
```

## Usage

* export aws account 
```bash
export AWS_PROFILE=<PROFILE_NAME>
```
* cli command to run the tool

```bash
route53-to-cloudflare -id <CLOUDFLARE_ACCOUNT_ID> -ns <CLOUDFLARE_NS_RECORDS_OF_YOUR_ACCOUNT> -awsID <AWS_ACCOUNT_ID>
```

Since the tool ignores the top NS record and the SOA record.
In the countRecord.txt we will see 2 records missing. (check Limitations)

## Requirements

OS - Linux based

Other than the OS requirements, there are no specific requirements except a few weel-known and widelly used Python
modules listed in the [requirements.txt](requirements.txt) and automatically
installed with module.

## Limitations
Even though we tried to get catch as many edge cases as we could, there still might be some that we missed.
In order to over come those cases we created a summry file, named 'countRecords.txt', that will compare the number of records
that were templated as terraform cloudflare resources with the actual number records in the aws route53 zone.

So we can see that we didn't miss any record.

For example:
```
    A                   = "108"
    AAAA                = "0" 
    CNAME               = "14" 
    MX                  = "0"
    SPF                 = "0"
    TXT                 = "4"
    NS                  = "0"
  -------------------------------------------------
  total records Created = "127"
    
  total recrds in AWS   = "129"
  -------------------------------------------------
    A                   = "108"
    AAAA                = "0" 
    CNAME               = "14" 
    MX                  = "1"
    SPF                 = "0"
    TXT                 = "4"
    NS                  = "1"
```

**Note:** Becuase we exclude the top level NS record and the SOA, ***a deficit of 2*** record means that all records were 
parased and created as terraform resources.

## Validation
As disscused before, there might be some edge cases that we missed.
That is why we created a validation script that compares the records value in cloudflare with the values of the 
current known records in the global DNS server.

**curently SPF validation is not complete.**

**We highly recommend manual validation as well**

## Supported DNS records types

Currently this module supports the next types of DNS records:

- A
- AAAA
- CNAME
- MX
- SPF
- TXT
- NS

Other types of DNS records can be added based on the need. 
Also, contrinutions are always welcome.