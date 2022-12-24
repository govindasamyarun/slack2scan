# Slack2Scan

## About The Project

The Slack2scan application scans the GitHub repository for hardcoded secrets using Gitleaks. It will make security testing easier and help increase security adoption. Not limited to hardcoded secrets, it can be extended to perform SAST & DAST scans. 

Abstracts away the complexity and provides a simple command to run security scans using Slack. The results get published to the same slack channel. Developers can perform the scan independently, eliminating the dependency on DevOps and AppSec teams. 

The application is written in Python Flask. And it is easier to add a library for any new security tools. 

<img width="1167" alt="Screenshot 2022-12-24 at 1 06 39 PM" src="https://user-images.githubusercontent.com/69586504/209426225-1e1ffa1e-cb17-44bb-9ae3-9c144321bcd4.png">

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

## Demo

https://user-images.githubusercontent.com/69586504/209426286-25068277-ee3e-432a-a5e2-43eafa8bca50.mov

## Support

Use the issues tab to report any problems or issues.

## License

Distributed under the MIT License. See LICENSE for more information. 
