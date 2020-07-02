import os
import json
import datetime
import boto3

region      = os.environ['AWS_REGION']
method = os.environ['instance_method']
bucket_name = os.environ['bucket_name']
bucket_key  = os.environ['bucket_key']

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
      ret = ''
      if list(instances):
        if method == 'stop':
          ret = stop_instances(instances)
        if method == 'start':
          ret = start_instances(instances)
  
      response = {
  	"Region"   	: region,
  	"Method"   	: method,
  	"Response"   	: ret,
        "Instances"	: [(i.id) for i in instances]
      }
    return response
