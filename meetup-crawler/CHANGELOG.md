# Oct 2020 Update 

## Changes 

### MeetupCrawler 

- use 'GROUP' as DynamoDB secondary key value ([commit](https://github.com/sebsto/meetup-crawler/commit/a7c4da856da3cc9ec6875713a54ff0601099e6dc) and [commit](https://github.com/sebsto/meetup-crawler/commit/15b723a66c64a70b9912cdf19fd5c525d938d91f))
- add `script/env.sh` to help to prepare env variable ([commit](https://github.com/sebsto/meetup-crawler/commit/e58d06837c29fda5634bca4e1743935fe29da7d0))
- Add 4 new user groups to monitor [Issue #6](https://github.com/sebsto/meetup-crawler/issues/6)
- Add two scripts to update DynamoDB data model ([commit](https://github.com/sebsto/meetup-crawler/commit/a7c4da856da3cc9ec6875713a54ff0601099e6dc)). These script need to be executed once and only once.

## How to upgrade ?

```zsh
# setup the environment 
cd meetup-crawler 
./script/env.sh 
pipenv shell 

# deploy the updated code to AWS Lambda 
sam build && sam deploy --stack-name meetup-crawler-dev

# Update the dynamodb database 
python -m util.update_group_list
python -m util.update_secondary_key
```