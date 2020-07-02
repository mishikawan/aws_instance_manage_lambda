import os
import json
import datetime
import boto3

region = os.environ['AWS_REGION']

def get_calendar(s3obj,bucket_name,bucket_key):
    s3 = s3obj.get_object(Bucket=bucket_name, Key=bucket_key)
    return s3['Body'].read().splitlines()

def get_ec2instances(resource):
    return resource.instances.filter(
      Filters=[{
        'Name': 'tag:BackupTarget',
        'Values': ['ON']
      }]
    )

def stop_instances(instances):
    return instances.stop()

def start_instances(instances):
    return instances.start()

def lambda_handler(event,context):

    resource = boto3.resource('ec2')
    client   = boto3.client('ec2')
    s3obj    = boto3.client('s3')
    method  = 'none'

    if 'method' in event:
        method = event['method']
    if 'bucket_name' in event:
        bucket_name = event['bucket_name']
    if 'bucket_key' in event:
        bucket_key = event['bucket_key']

    instances = get_ec2instances(resource)

    check_dates = get_calendar(s3obj,bucket_name,bucket_key)
    check_dates = [ x.decode('utf8') for x in check_dates ]
    now_date    = datetime.datetime.now().strftime('%Y%m%d')

    if now_date in check_dates:
      response = {
  	"Region"   	: region,
  	"Method"   	: method,
  	"Response"   	: "non-ope",
        "Instances"	: [(i.id) for i in instances]
      }
    else:
      if list(instances):
        if method == 'stop':
          response = stop_instances(instances)
        if method == 'start':
          response = start_instances(instances)
  
      response = {
  	"Region"   	: region,
  	"Method"   	: method,
  	"Response"   	: response,
        "Instances"	: [(i.id) for i in instances]
      }
    return response
