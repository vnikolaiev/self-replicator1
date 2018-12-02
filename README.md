# self-replicator

Installation instructions(Google App Engine)

* Install `google-cloud-sdk` [https://cloud.google.com/sdk/]()
* Clone application from GitHub using `git clone`
* Go inside the cloned directory
* Run `gcloud init` in your console
* Choose your account or log in
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
Check `requirements.txt` for details

Run in *nix environment:

`export FLASK_APP=main.py; python3 -m flask run --host=0.0.0.0 --port=80`

For more details check official flask doc
[http://flask.pocoo.org/docs/1.0/]()
