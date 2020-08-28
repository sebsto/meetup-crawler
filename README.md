# Meetup Crawler 

This is the code for the Meetup Crawler Project. The goal of the project is to collect AWS User's Group data from meetup.com for analytics purposes.  Data collected are the ones available through the public API of meetup.com, it includes data such as the number of members, the number of events organised, the number of rsvp per event etc.

Project architecture is illustrated below.

## Requirements

You need to have an AWS Account, and permissions to create all the services used. 

In addition, you need to have :

- python 3.8 (`brew install python@3.8`)
- pipenv (`brew install pipenv`)
- sam (`brew tap aws/tap && brew install aws-sam-cli`). This requires `docker`
- cdk (`npm install -g aws-cdk`)

## Contribute 

Please send your GitHub's username to [stormacq@amazon.com](mailto:stormacq@amazon.com?subject=I%20want%20to%20join%20the%20Meetup%20Crawler%20GitHub%20project) to be invited to the project.

Or send your [pull requests](https://github.com/sebsto/meetup-crawler/pulls).

## Data Model

If you rely on this project to create analytics solutions, here is the data model you can rely on.

### Group Table

This table contains the AWS User Group's details and their historical information. Each time the crawler run, a record is added to this table with the current data for the group. The record having the latest `last_updated_at` is the current record.

```text
data model
```

### Group View

This is a view built on the 'Group Table'. It only shows the latest record for each group.

The list of columns and their respective data types is the same as the Group Table.

The view is defined as:
```text 
CREATE OR REPLACE VIEW meetup_group_latest AS
    SELECT * 
    FROM meetup_group AS MG
    WHERE last_updated_at = (SELECT max(last_updated_at) FROM meetup_group WHERE MG.id = id);  
```

### Event Table 

This table contains the events organised by each group. It only tracks events in the past. As such, an event does not change once inserted into that table.

```text
datamodel
```

## Deployment

To deploy this project on your own account, follow the below instructions.

0. Download the project sources :

```zsh
git clone https://github.com/sebsto/meetup-crawler.git
```

1. Create a virtual environment for `meetup-infra` 

Install dependencies for meetup-infra

Deploy the infra 

```zsh
cdk deploy -c env=dev "*"
```

2. Collect resources IDs to inject into meetup-crawler 

3. Create a virtual environment for meetup-crawler

Install dependencies for meetup-crawler

Deploy the crawler

```zsh
# The first time 
sam build && sam deploy --guided 

# for subsequent deployments 
sam build && sam deploy 
```

5. Import initial list of User Group



