# DUNVIIDY Video Management System - Capstone Project Spring 2025 

## Overview

**DUNVIIDY** is a modular, self-hosted video upload and delivery system designed for academic environments such as Dunwoody College. It combines a Flask-based upload website, a transcoding pipeline powered by Handbrake, and a MediaCMS streaming platform to support secure, scalable, and role-based access to educational video content.

This system allows students and faculty to easily upload, process, and access multimedia materials while maintaining administrative control, format consistency, and flexible deployment options.

---

## Quick Start

> These instructions assume you are working on a Linux environment with Docker and Docker Compose installed.

### Upload Website (Flask + Dropzone)

```bash
# Navigate to the upload-site directory
cd flask_dropzone 

# Start the Flask app and Nginx reverse proxy
docker-compose up -d 

# Access the upload site in your browser
http://localhost:8000 or http://<your-domain>:8080
```

### MediaCMS

```bash
# Navigate to the MediaCMS directory
cd mediacms

# Launch MediaCMS platform
docker-compose up -d

# Access MediaCMS dashboard
http://localhost or http://<your-domain>
```

> For detailed installation and setup instructions, refer to the `/4_Deployment_Guide.pdf`.

---

## Key Technologies

| Component          | Tool / Stack          | Purpose                                      |
|---------------------|-----------------------|----------------------------------------------|
| Upload Website      | Flask, Dropzone.js    | Drag-and-drop media uploads with validation  |
| Transcoder          | Handbrake (CLI)       | Auto-convert videos to MP4 for compatibility |
| Media Platform      | MediaCMS              | Video streaming, role access, subtitle support |
| Deployment          | Docker + Nginx        | Containerized hosting and reverse proxying   |
| Infrastructure      | Linux (CentOS/Ubuntu) | Tested in on-prem and cloud-like environments |


---

# Dunviidy Terraform/Cloud Architecture
This folder contains everything needed to set up a working basic architecture for Dunviidy's cloud portion of the project. The code in here on creation will call on 2 modules labeled Lambda and S3. These modules when the code is run will create:
- 2 S3 buckets
- 1 Lambda function
- 1 Lambda role

This Terraform's job is to create the subtitles of a video and to distribute that and the same video to users so they can upload it to the Dunviidy platform. It works in tandem with the physical on-premises environment and is synced via DataSync.

Every module here has readme.md files as well in them for further reading, the ones below are basic summaries. DataSync though should be read as it is the guide on how to set up DataSync for the cloud environment.

## Lambda Module
The Lambda module contains a Lambda function and its needed IAM permissions for what it does. The basic overview is that the function, when a video is sent to the input bucket, will trigger and transcribe the video for subtitles in the .vtt format and will store the video in the output bucket. It then sends an email to the email stored in email.txt file in the input bucket and sends it 2 links to the video and .vtt file. The sender email is currently assigned to a variable in the Lambda function itself, and will need to be changed to suit the needs of the user.

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

---

## Features

- 🎥 Drag-and-drop video uploads with progress tracking
- 🧹 Auto-conversion to MP4 format using Handbrake
- 🔐 Role-based video access via MediaCMS (e.g., student, instructor)
- 🔎 Full-text search, subtitle support, and resource attachments (e.g., PDFs)
- 📦 Dockerized for easy deployment and modular upgrades
- 🎬 Subtitle and media distribution
- ☁️🔐 Secure file transfer from on-premises to cloud environment

---

## Known Limitations

- No Single Sign-On (SSO) integration
- Currently tuned for MP4 format only
- Manual restart needed if transcoding script fails
- Datasync if it transfers too early will transfer corrupted videos
- SES needs to be configured manually for every user, it is not scalable in its current moment a fix needs to be implemented
down the line.
- The Lambda function only triggers on a video being added and the function needs both the video and email.txt file to work.
- S3 input bucket lifecycle policy must be configured to only recognize files over 10 bytes for the scope, this is so the datasync metadata file is not deleted every 2 days.

---

## License & Credits

All open-source components are cited in the Refreneces Section with their respective licenses. DUNVIIDY’s custom code is available under the [MIT License](https://opensource.org/licenses/MIT).


---

## Contact

### **Author:** Omar Elkhodary, Duy Vo, Lucas Rassmussen, Mason Helmel
---
**Instructor:** Paul Flowers  
**Course:** CLDE2291-01 Summative Experience  

## References
This project uses open source libraries and assets from the following:

- [MediaCMS](https://github.com/mediacms-io/mediacms) by Markos Gogoulos, licensed under [MediaCMS License](https://github.com/mediacms-io/mediacms/blob/main/LICENSE.txt)
- [HandBrake](https://github.com/HandBrake/HandBrake) by The HandBrake Team, licensed under [HandBrake License](https://github.com/HandBrake/HandBrake/blob/master/LICENSE)
- [DataSync Guide](https://docs.aws.amazon.com/datasync/latest/userguide/deploy-agents.html)
