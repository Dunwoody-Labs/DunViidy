# Dunviidy S3 Module
This module is for creating 2 S3 buckets for Dunviidy's Cloud environment. These buckets are labeled Input and Output and work with the lambda module for the environments success.
## What S3 Input Does
The S3 input bucket stores files that are transferred from DataSync every hour. The bucket then stores the files for 2 days from creation then deletes them forever. The files transferred should be a .txt file containing an email and a .mp4 file containing a video.
## What S3 Output Does 
The S3 output bucket stores the transcribe file that is created from the function and the video that was stored in input. These 2 files are then sent to the user via SES.