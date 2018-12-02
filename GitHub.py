import json
import requests
import base64

"""
GitHub API request result code
"""


class GitHubResultCode:
    def __init__(self, code, message):
        self.code = code
        self.message = message


class GitHub:
    _GITHUB = 'https://github.com'
    _GITHUB_API = 'https://api.github.com'
    _authenticated = False

    """
    token_provider - function that returns externally stored token
    """

    def __init__(self, token_provider):
        self.get_token = token_provider

    def get_token_from_github(self, client_id, client_secret, code):
        url = self._GITHUB + '/login/oauth/access_token'
        headers = {'Accept': 'application/json'}
        payload = {'client_id': client_id, 'client_secret': client_secret, 'code': code}
        r = requests.post(url, headers=headers, data=payload)
        return json.loads(r.text).get('access_token', None)

    def get_token(self):
        raise NotImplementedError

    """
    Create a repository
    :calls: `GET /user`
    :rtype: string | :class:`GitHub.GitHubResultCode`
    """

    def get_user(self):
        if self.get_token() is None:
            return GitHubResultCode(0, 'GitHub token not found')
        # GET /user
        url = self._GITHUB_API + '/user'
        headers = {'Accept': 'application/json', 'Authorization': 'token ' + self.get_token()}
        r = requests.get(url, headers=headers)
        if r.status_code == 401:
            return GitHubResultCode(401, "Unauthorized. Probably GitHub access token is expired")
        elif r.status_code != 200:
            return GitHubResultCode(r.status_code, 'Retrieve user name failed: Code - {code}, Message - {message}' \
                                    .format(code=r.status_code, message=json.loads(r.text).get('message', None)))
        else:
            return json.loads(r.text).get('login', None)

    """
    Create a repository
    :calls: `GET /repos/:owner/:repo`
    :param repo_name: string, (required), name of repository
    :rtype: bool | :class:`GitHub.GitHubResultCode`
    """

    def is_repo_exists(self, repo_name):
        if self.get_token() is None:
            return GitHubResultCode(0, 'GitHub token not found')
        # GET /repos/:owner/:repo
        user = self.get_user()
        if type(user) is GitHubResultCode:
            return user
        url = self._GITHUB_API + '/repos/{owner}/{repo_name}'.format(owner=user, repo_name=repo_name)
        headers = {'Accept': 'application/json', 'Authorization': 'token ' + self.get_token()}
        r = requests.get(url, headers=headers)
        if r.status_code == 401:
            return GitHubResultCode(401, "Unauthorized. Probably GitHub access token is expired")
        elif r.status_code == 200:
            return True
        else:
            return False

    """
    Create a repository
    :calls: `POST /user/repos`
    :param repo_name: string, (required), name of repository
    :rtype: :class:`GitHub.GitHubResultCode`
    """

    def create_repo(self, repo_name):
        if self.get_token() is None:
            return GitHubResultCode(0, 'GitHub token not found')
        is_exists = self.is_repo_exists(repo_name)
        if type(is_exists) is GitHubResultCode:
            return is_exists
        if is_exists:
            return GitHubResultCode(409, 'Repository already exists')
        # POST /user/repos
        url = self._GITHUB_API + '/user/repos'
        headers = {'Accept': 'application/json', 'Authorization': 'token ' + self.get_token()}
        payload = json.dumps({'name': repo_name, 'description': 'This is self-replicating app repo'})
        r = requests.post(url, headers=headers, data=payload)
        if r.status_code == 401:
            return GitHubResultCode(401, "Unauthorized. Probably GitHub access token is expired")
        elif r.status_code != 201:
            return GitHubResultCode(r.status_code, 'Repo {repo} not created: Code - {code}, Message - {message}' \
                                    .format(repo=repo_name, code=r.status_code,
                                            message=json.loads(r.text).get('message', None)))
        else:
            return GitHubResultCode(201, 'Repository created')

    """
    Create a file in repository
    :calls: `PUT /repos/:owner/:repo/contents/:path`
    :param repo_name: string, (required), name of repository where file will be placed 
    :param path: string, (required), path of the file in the repository
    :param content: string, (required), the content of the file
    :rtype: :class:`GitHub.GitHubResultCode`
    """

    def put_file(self, repo_name, path, content):
        if self.get_token() is None:
            return GitHubResultCode(0, 'GitHub token not found')
        # PUT /repos/:owner/:repo/contents/:path
        user = self.get_user()
        if type(user) is GitHubResultCode:
            return user
        url = self._GITHUB_API + '/repos/{owner}/{repo_name}/contents/{file}' \
            .format(owner=user, repo_name=repo_name, file=path)
        headers = {'Accept': 'application/json', 'Authorization': 'token ' + self.get_token()}
        payload = json.dumps({'message': 'Self-replicator initial commit',
                              'content': base64.b64encode(content).decode('utf-8')})
        r = requests.put(url, headers=headers, data=payload)
        if r.status_code == 401:
            return GitHubResultCode(401, "Unauthorized. Probably GitHub access token is expired")
        elif r.status_code != 201:
            return GitHubResultCode(r.status_code, 'File {file} not created: Code - {code}, Message - {message}' \
                                    .format(file=path, code=r.status_code,
                                            message=json.loads(r.text).get('message', None)))
        else:
            return GitHubResultCode(201, 'File created')
