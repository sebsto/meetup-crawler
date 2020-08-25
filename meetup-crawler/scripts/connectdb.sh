AWS_REGION=eu-west-3
SECRET_ID=meetupcrawlerdatabaseSecret-IotH2oBYYAAG
SECRET_JSON=$(aws secretsmanager --region $AWS_REGION get-secret-value --secret-id $SECRET_ID --query SecretString | sed -e 's/\\"/"/g' | sed -e 's/"{/{/g' | sed -e 's/}"/}/g')
echo $SECRET_JSON | jq

USERNAME=$(echo $SECRET_JSON | jq -r .username)
PASSWORD=$(echo $SECRET_JSON | jq -r .password)
HOST=$(echo $SECRET_JSON | jq -r .host)
PORT=$(echo $SECRET_JSON | jq -r .port)
DBNAME=$(echo $SECRET_JSON | jq -r .dbname)

# psql -h $HOST -p $PORT -U $USERNAME -W $PASSWORD
psql postgresql://$USERNAME:$PASSWORD@$HOST:$PORT/$DBNAME