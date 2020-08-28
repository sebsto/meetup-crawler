from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    custom_resources as cr,
    core)

class MeetupInfraRdsStack(core.Stack):

    cluster           = None 
    db_security_group = None 

    def __init__(self, scope: core.Construct, config: dict, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create the securty group that will allow to connect to this instance
        # I am lazy and create only 1 SG that allows TCP 5432 from itself
        # database clients (lambda functions) will have TCP 5432 authorized for themselves too, 
        # which is not necessary but harmless
        self.db_security_group = ec2.SecurityGroup(self, "Database Security Group", vpc=config['vpc'])
        self.db_security_group.add_ingress_rule(self.db_security_group, ec2.Port.tcp(5432))

        self.cluster = rds.DatabaseCluster(self, config['rds']['name'], 
            engine=rds.DatabaseClusterEngine.aurora_postgres(version=rds.AuroraPostgresEngineVersion.VER_11_7),
            default_database_name=config['rds']['databaseName'],
            master_user=rds.Login(username=config['rds']['masterUsername']),
            instance_props=rds.InstanceProps(vpc=config['vpc'],security_groups=[self.db_security_group])
        )

        # Add Secrets Manager Password rotation
        self.cluster.add_rotation_single_user()

        # aurora serverless is not yet support by CDK, https://github.com/aws/aws-cdk/issues/929
        # escape hatch https://docs.aws.amazon.com/cdk/latest/guide/cfn_layer.html#cfn_layer_raw
        # cfn_aurora_cluster = cluster.node.default_child
        # cfn_aurora_cluster.add_override("Properties.EngineMode", "serverless")
        # cfn_aurora_cluster.add_override("Properties.EnableHttpEndpoint",True) # Enable Data API
        # cfn_aurora_cluster.add_override("Properties.ScalingConfiguration", { 
        #     'AutoPause': True, 
        #     'MaxCapacity': 4, 
        #     'MinCapacity': 1, 
        #     'SecondsUntilAutoPause': 600
        # }) 
        # cluster.node.try_remove_child('Instance1') # Remove 'Server' instance that isn't required for serverless Aurora

        # create a custom resource to initialize the data schema 
        function = _lambda.Function(self, config['custom resource lambda']['name'],
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset('./custom_resources'),
            handler='app.on_event',
            vpc=config['vpc'],
            environment={ 'secretArn' : self.get_secret_arn() },
            security_groups=[ self.db_security_group ]
        )

        custom_resource_provider = cr.Provider(self, 'Custom Resource Provider',
            on_event_handler=function
        )
        core.CustomResource(self, 'Custom Resource', service_token=custom_resource_provider.service_token)

    def get_database(self):
        return self.cluster

    def get_security_group(self):
        return self.db_security_group

    def get_secret_arn(self):
        return self.cluster.secret.secret_arn
    