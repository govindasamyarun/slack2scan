# Slack2Scan

## About The Project

The Slack2scan application will make the security testing process easier and help increase security adoption. 

It abstracts away the complexity and provides a simple command to run security scans using Slack. Results get published to the same slack channel. 

The application is written in Python Flask. The modular code makes it easier to write a library for any new security tools. 

## Getting started

### Prerequisites

* Docker
* Docker-compose

### Installation

1. Create an app in your Slack account 

   ```sh
   https://api.slack.com/apps
   ```
   
2. Select Create App -> From Scratch 
   
3. Enter App Name & select a workspace to deploy the app 

4. Copy the Signing Secret 

5. Set OAuth & Permissions and the following scopes 

   ```sh
   channels:read
   chat:write
   chat:write.public
   commands
   ```
6. Install the app in the workspace 

7. Slash Commands -> Create New Command -> Save

   ```sh
   Command: /scan
   Request URL: https://<FQDN>/s2s/scan
   Short Description: Scan repository
   Usage Hints: /scan <URL> <Branch - Optional>
   ```
   
8. Turn on Interactivity & Shortcuts -> Save Changes

   ```sh
   https://<FQDN>/s2s/interactive
   ```

9. Clone the repository

   ```sh
   cd /Data
   git clone https://github.com/govindasamyarun/slack2scan.git
   ```
   
10. Edit docker-compose.yml file to include signing secret and application host name values 


   ```sh
   pwd: /Data/slack2scan
   vi docker-compose.yml
   ```
   
   ```yaml
    environment:
      SLACK_SIGNING_SECRET: <Paste the signing secret>
      S2S_HOST_NAME: <Enter the application hostname>
   ```
11. Start the container

   ```sh
   pwd: /Data/slack2scan
   
   docker-compose up --detach
   ```

## Support

Use the issues tab to report any problems or issues.

## License

Distributed under the MIT License. See LICENSE for more information. 