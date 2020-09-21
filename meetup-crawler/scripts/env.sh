    AWS_REGION=eu-west-3

    ENV=dev # or prod 

    LAMBDA_SUBNETS=$(aws cloudformation describe-stacks --region $AWS_REGION --stack-name meetup-infra-$ENV-vpc --query "Stacks[0].Outputs[?contains(ExportName,'vpclambdaSubnet')].OutputValue" --out text | python -c 'import sys; print(sys.stdin.read().replace("\t",","))')
    echo $LAMBDA_SUBNETS
    # shorter version ==> | perl -pe 's/\t\,/g'

    SECURITY_GROUP=$(aws cloudformation describe-stacks --region $AWS_REGION --stack-name meetup-infra-$ENV-rds --query "Stacks[0].Outputs[?ExportName=='db-security-groups-$ENV'].OutputValue" --out text)
    echo $SECURITY_GROUP

    SECRET_ARN=$(aws cloudformation describe-stacks --region $AWS_REGION --stack-name meetup-infra-$ENV-rds --query "Stacks[0].Outputs[?ExportName=='db-secret-name-$ENV'].OutputValue" --out text)
    echo $SECRET_ARN
    
    echo "AWS_REGION=$AWS_REGION" > .env
    echo "DB_SECRET_ARN=$SECRET_ARN" >> .env
    echo "PYTHON_LOGLEVEL=debug" >> .env
    echo "PYTHONPATH=./src" >> .env
    echo "SQS_QUEUE_NAME=$(aws cloudformation describe-stacks --region $AWS_REGION --stack-name meetup-crawler-$ENV --query "Stacks[0].Outputs[?ExportName=='SQS-QUEUE-NAME-$ENV'].OutputValue" --output text)" >> .env
    echo "DYNAMODB_TABLE_NAME=$(aws cloudformation describe-stacks --region $AWS_REGION --stack-name meetup-crawler-$ENV --query "Stacks[0].Outputs[?ExportName=='DYNAMODB-TABLE-NAME-$ENV'].OutputValue" --output text)" >> .env
    
    