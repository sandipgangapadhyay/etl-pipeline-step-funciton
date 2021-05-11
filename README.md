# Writing a Sample

** Version 1.0.0 **

This pattern explain how to build a serverless  ETL pipeline to validate, transform, compress, 
and partition large csv dataset for performance and cost optimization. 
The pipeline is orchestrated by serverless AWS Step Functions with error handling, retry and end user notification.
When a csv file is uploaded to AWS S3 (Simple Storage Service) Bucket source folder, ETL pipeline is triggered. 
The pipeline validates the content and the schema of the source csv file, transform csv file to compressed parquet format, 
partition the dataset with year/month/day  and store in a transformed folder for  analytics tools to consume.

## Prerequisites 
Prerequisites 
An active AWS account with programmatic access
AWS CLI with AWS account configuration, so that you can create AWS resources by deploying cloudformation stack
Amazon S3 bucket 
CSV dataset with correct schema ( attached is a sample csv file with correct schema and data type)
Chrome web browser
AWS Glue console access
AWS Step Functions console access

## Limitations
AWS Step Functions:

Execution History: The maximum limit for keeping execution history logs is 90 days.
For more details refer: 
AWS Step Functions Limits Overview

## Product versions
Python 3 for AWS Lambda
AWS Glue version 2#

## Architecture

<img src="images/ETL_Orchestration.jpg">

## High level work flow


User uploads a csv file 
AWS S3 Notification event tiggers a AWS Lambda function that starts the step function state machine
AWS Lambda function validates the schema and data type of the raw file
AWS Glue Crawler create the schema of the raw file and move the file to stage folder
AWS Glue job transform, compress and partition the raw file into Parquet format
AWS Glue job also move the file to transform folder.
AWS Glue Crawler create the schema from the transformed file . The Resulting Schema can be used by analytics job
AWS SNS sends succesful notification
File moved to error folder if validation fails
AWS SNS sends error notification for any error inside workflow
Amazon Athena can be used for any adhoc query on partitioned dataset. 

## Deploy
This pattern can be deployed through AWS Cloudformation. See the attachment for the Cloudformation template file.

Follow the below step to deploy this pattern using Cloudformation template

1.	Clone the Repo
2.	Navigate to the Directory
3.	Update parameter.json file as follows - 
    a.	pS3BucketName 	        - Unique bucket name. This bucket will be created to store all the dataset. 
                                  As, S3 Bucket name is globally unique, provide a unique name.
    b.	pEmailforNotification 	- A valid email address to receive success/error notification.
    c.	pSourceFolder 		    - Folder name (inside bucket created mentioned in 3.a) where source csv file will be uploaded inside 
    d.	pStageFolder 		    - Folder name (inside bucket created mentioned in 3.a) used to staging area for AWS Glue Jobs 
    e.	pTransformFolder 	    - Folder name (inside bucket created mentioned in 3.a) where transformed and portioned dataset will be stored 
    f.	pArchiveFolder 		    - Folder name (inside bucket created mentioned in 3.a) where source csv file will be archived 
    g.	pErrorFolder 		    - Folder name (inside bucket created mentioned in 3.a) where source csv file will be moved for any error 
    h.  pDatasetSchema          - 

Execute the following AWS CLI command with pre-configured AWS CLI profile . Replace “Profile_Name” with a valid aws cli profile name
stack_name                              – Provide a unique stack name
existing_bucket_name_in_the_same_region – Provide an existing S3 bcuket name in the same region where the stack will be deployed

4.	aws cloudformation package --template-file template.yml --s3-bucket <existing_bucket_name_in_the_same_region> --output-template-file packaged.template --profile <Profile_Name>
5.	aws cloudformation deploy --stack-name <stack_name> --template-file packaged.template  --parameter-overrides file://parameter.json --capabilities CAPABILITY_IAM --profile <Profile_Name>
6.	Check the progress of CloudFormation stack deployment in console and wait for it to finish


## Test

Once, stack deployment is completed, navigate to source folder inside S3 bucket ( which was provided in Step 3a above)
Upload a sample csv file ( attached) to trigger the ETL Pipeline through AWS Step Functions.
Check the ETL pipeline status in the AWS Step Functions.
Once ETL pipeline completes, partitioned dataset will be available in transform folder inside S3 Bucket ( set in Step 3a)
Partitioned Table will be available in AWS Glue Catalog. 
Optionally, Amazon Athena can be used for adhoc query on the partitioned/transformed dataset

## Successful ETL pipeline execution
<img src="images/Successful_Execution.png">


## ETL pipeline execution with input validation error
<img src="images/Failed_Execution.png">