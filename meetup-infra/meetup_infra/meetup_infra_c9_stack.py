from aws_cdk import (
    aws_ec2 as ec2,
    aws_cloud9 as cloud9,
    core)

class MeetupInfraCloud9Stack(core.Stack):

    vpc = None 

    def __init__(self, scope: core.Construct, config: dict, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # config['db_security_group'] ??

        # The code that defines your stack goes here
        cloud9.Ec2Environment(self, 'Meetup Crawler Cloud9', 
            vpc=config['vpc'],
        )
