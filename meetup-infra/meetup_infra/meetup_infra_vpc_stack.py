from aws_cdk import (
    aws_ec2 as ec2,
    core)

class MeetupInfraVpcStack(core.Stack):

    vpc = None 

    def __init__(self, scope: core.Construct, config: dict, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        self.vpc = ec2.Vpc(self, config['vpc']['name'],
            cidr="10.0.0.0/16",
            max_azs=config['vpc']['maxAzs'],
            nat_gateways=config['vpc']['natGateways']
        )

    def get_vpc(self):
        return self.vpc