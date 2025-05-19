# Dunviidy Terraform/Cloud Architecture
This folder contains everything needed to set up a working basic architecture for Dunviidy's cloud portion of the project. The code in here on creation will call on 2 modules labeled Lambda and S3. These modules when the code is run will create:
- 2 S3 buckets
- 1 Lambda function
- 1 Lambda role

This Terraform's job is to create the subtitles of a video and to distribute that and the same video to users so they can upload it to the Dunviidy platform. It works in tandem with the physical on-premises environment and is synced via DataSync.

Every module here has readme.md files as well in them for further reading, the ones below are basic summaries. DataSync though should be read as it is the guide on how to set up DataSync for the cloud environment.

## Lambda Module
The Lambda module contains a Lambda function and its needed IAM permissions for what it does. The basic overview is that the function, when a video is sent to the input bucket, will trigger and transcribe the video for subtitles in the .vtt format and will store the video in the output bucket. It then sends an email to the email stored in email.txt file in the input bucket and sends it 2 links to the video and .vtt file.

## S3 Module
The S3 module contains 2 S3 buckets that are used by the Lambda module for its processing and storing, labeled input and output respectively. It also works with DataSync for storing files from the on-premises environment to the S3 input bucket. The output bucket is used for storing the files processed via the Lambda module.

## DataSync
**THIS CAN ONLY BE DONE AFTER YOUR INFRASTRUCTURE IS CREATED**
DataSync unlike the rest of this will need to be configured manually. You will need to set up a DataSync agent on your on-premises environment and then create 2 locations. A guide for setting up DataSync is here: [DataSync Guide](https://docs.aws.amazon.com/datasync/latest/userguide/deploy-agents.html)

### Setting Up DataSync
1. The locations you will need to configure will be:
   - Location pointing toward the created S3 Input bucket
   - Location pointing toward the physical server's "processed_vids" or a folder where your videos and .txt files are stored

2. Once this is done create a task using the location pointing towards the physical server as the source and the S3 location as the destination. 
   - Set the DataSync task to run every hour and to transfer all files you need to the .txt and .mp4 files to be sent to the input bucket.

3. Run a test to validate it is properly working, once it is DataSync is now set up.

## Setting up Cost Explorer
Setting up cost explorer is important for this environment, as it will allow the organization to track the expenses for the cloud portion. Each created resource has been tagged for this purpose, and can be tracked in AWS Cost Explorer.
1. Navigate to AWS Cost Explorer
2. Select Cost Allocation Tags on the left menu
3. Select the tag used to track resources (default: "dunviidy"), and activate
4. The resources should now be tracked for Cost Analysis

## Known Problems
SES needs to be configured manually for every user, it is not scalable in its current moment a fix needs to be implemented down the line.

The Lambda function only triggers on a video being added and the function needs both the video and email.txt file to work.

S3 input bucket lifecycle policy must be configured to only recognize files over 10 bytes for the scope, this is so the datasync metadata file is not deleted every 2 days.
