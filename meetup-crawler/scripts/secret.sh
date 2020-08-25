AWS_REGION=eu-west-3
SECRET_ID=meetupcrawlerdatabaseSecret-pDbdefjrmmIg
SECRET_JSON=$(aws secretsmanager --region $AWS_REGION get-secret-value --secret-id $SECRET_ID --query SecretString | sed -e 's/\\"/"/g' | sed -e 's/"{/{/g' | sed -e 's/}"/}/g')
echo $SECRET_JSON | jq