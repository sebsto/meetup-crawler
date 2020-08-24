#!/usr/bin/env python3
import os 
import sys
import json 

import boto3
from botocore.config import Config

from aws_cdk import core

from meetup_infra.meetup_infra_vpc_stack import MeetupInfraVpcStack
from meetup_infra.meetup_infra_rds_stack import MeetupInfraRdsStack

def prepareBotoConfig(config):

    return Config(
        region_name = config['env']['region'],
    )

app = core.App()

# AWS SDK Configuration
config_aws = None 

# read the configuration file 
env = app.node.try_get_context("env")
if env is None:
    print("An environment context must be provided (-c env=prod|dev)")
    sys.exit(-1)

config_file = f'./conf/config.{env}.json'
try:
    with open(config_file) as json_file:
        config = json.load(json_file)

        # when provided on the CLI, overwrite the region param
        region = app.node.try_get_context("region")
        if region is not None:
            config['env']['region'] = region
            print(f"Using region from context (-c region={region})")
        else: 
            print(f"Using region from conf file (region={config['env']['region']})")

        # Create a CDK configuration to use this region 
        # https://docs.aws.amazon.com/cdk/latest/guide/environments.html
        cdk_env = core.Environment(region=config['env']['region'])

        # instanciate all our stacks 
        vpc = MeetupInfraVpcStack(app, config, f'meetup-infra-{env}-vpc', env=cdk_env)
        config['vpc'] = vpc.get_vpc()
        database = MeetupInfraRdsStack(app, config, f'meetup-infra-{env}-rds', env=cdk_env)

except IOError as error:
    print(f"Can not read {config_file}")
    print(error)
    sys.exit(-1)

app.synth()
