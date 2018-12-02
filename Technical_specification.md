#Tech Spec - Self replicating GitHub App

November 30, 2018<br>
Author: @vnikolaiev

##Overview

####Product requirements

The result of product should be an URL. 
When a user opens the URL, the application behind the URL requests access to the user's GitHub profile and creates a repository with its own (application's) code. 
The application should not ask for the users's password or require access to  user's private repositories.
 
The repository should contain:
* The application code.
* Installation document containing instructions on how to launch the application and get a working URL that replicates the repository.
* Technical specification document describing what the application does and how.

####Assumptions

* System is written in Python. Because it's the main programming language of your company.
Overall it is easy and fast to develop and has a large number of libraries which suit us. 
* Application can't ask user's password. That means we need the OAuth authentication or pregenerated user's token.
I decided to use GitHub OAuth as more user friendly. I'll use Web Application flow.
The flow to authorize users for App is:
    * Users are redirected to request their GitHub identity
    * Users are redirected back to our site by GitHub
    * We retrieve the user's token and access the API with the user's access token 
* We need to register our App on OAuth Apps in Github [OAuth Apps Registration](https://github.com/settings/applications/new).
That's why we need hosting with direct IP address or even better domain name for our App.
I selected Google App Engine as it provides support of Python apps, simple environment setup, application deployment and free tariff plan for our needs.  

##Approach

### Components

Application consists of several parts:

##### *`GitHub.py`*
GitHUB API v3 adapter. Implements 4 operations:
* Token retrievement
* Get username of logged user
* Check repository existence
* Creating a repository
* Creating file in the repository

Function `get_token` is required in constructor. 
It is used to retrieve Github access token that is stored externally in user session.
GitHubResultCode class is used to transmit API status code to the main module.
    
`get_token_from_github` is used to retrieve token after redirection from GitHub authorisation page.
It passes 3 parameters: `client_id`, `client_secret` gotten when OAuth app registred in GitHub and `code` received
as redirect parameter.

Other functions that implements rest GitHub API operations with entities (user, repository, file) require
`Authorization` HTTP header with GitHub token. Otherwise we'll receive error 401 Unauthorised.

##### *`main.py`*
Main module with HTTP router and business logic.
Functions:

`get_token` is passed to GitHub constructor for operating with token stored in session

`listdir_nohidden` get all files (recursively) in the `path` except hidden and service files

`secret_replacer` used to replace values with <REPLACE_ME> for the keys passed in tuple parameter `keys`

`index` - default HTTP endpoint used for rendering HTML template depending on application state

`callback` - HTTP endpoint used as callback for GitHub OAuth service.

`clone` - HTTP endpoint that drives creating GitHub repository and cloning app files there    

##### *`templates/self-replicator.html`*
HTML template (Jinja2)

###Third-party libraries

* Flask 1.0.2 (http://flask.pocoo.org)
* Requests 2.20.1 (http://docs.python-requests.org/en/master/)

##Deployment

App is ready for deploy to Google App Engine service. It contains additional deployment files: 

* *`requirements.txt`*
Describes application requirements in virtualenv format.

* *`app.yaml`*
Configuration of Google App Engine application

####Installation instructions(Google App Engine)

* Install `google-cloud-sdk` [https://cloud.google.com/sdk/]()
* Clone application from GitHub using `git clone`
* Go inside the cloned directory
* Run `gcloud init` in your console
* Choose your Google account or log in
* Pick a cloud project or create the new one
* Create an application running `gcloud app create`
* Go to [https://github.com/settings/applications/new]() and register your app
  If you are using Google App Engine then your Homepage URL is [http(s)://project-name.appspot.com]()
  Authorization callback URL is [http(s)://project-name.appspot.com/callback]()
* Open 'config' file and replace `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`
  with your own obtained on the previous step
* Deploy the application running `gcloud app deploy app.yaml --project <your project name>`

Installation document is written for Google App Engine
If you like to use any other environment then you need: `python3.7`, `flask` and `requests` lib installed there.
You can use virtualenv or pip to install libs. Check `requirements.txt` for details.

Run application in *nix environment:

`export FLASK_APP=main.py; python3 -m flask run --host=0.0.0.0 --port=80`
