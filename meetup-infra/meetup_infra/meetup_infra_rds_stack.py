from aws_cdk import (
    aws_rds as rds,
    core)

class MeetupInfraRdsStack(core.Stack):

    def __init__(self, scope: core.Construct, config: dict, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        cluster = rds.DatabaseCluster(self, config['rds']['name'], 
            engine=rds.DatabaseClusterEngine.aurora_postgres(version=rds.AuroraPostgresEngineVersion.VER_11_7),
            default_database_name=config['rds']['databaseName'],
            master_user=rds.Login(username=config['rds']['masterUsername']),
            instance_props=rds.InstanceProps(vpc=config['vpc'])
        )

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

        # Add Secrets Manager Password rotation
        cluster.add_rotation_single_user()        
    