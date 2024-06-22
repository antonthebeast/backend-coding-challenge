"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request
import re


app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username: str):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'.format(username=username)
    response = requests.get(gists_url)
    return response.json()


def get_gist_by_id(gist_id: str):
    gist_url = 'https://api.github.com/gists/{gist_id}'.format(gist_id=gist_id)
    response = requests.get(gist_url)
    return response.json()


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """

    result = {
        "matches": [],
        "status": "error"  # bad status until the very end
    }

    try:
        post_data = request.get_json()
    except Exception as e:
        result["reason"] = e.__str__()
        return jsonify(result), 400

    try:
        username = post_data['username']
    except KeyError:
        result["reason"] = "Missing 'username' key in JSON data"
        return jsonify(result), 400
    
    try:
        pattern = post_data['pattern']
    except KeyError:
        result["reason"] = "Missing 'pattern' key in JSON data"
        return jsonify(result), 400
    
    result["username"] = username
    result["pattern"] = pattern

    try:
        gists = gists_for_user(username)
    except Exception as e:
        result["reason"] = e.__str__()
        return jsonify(result), 400

    if "status" in gists:
        result["status"] = 'error'
        result["reason"] = "User's gists not found (incorrent user name?)"
        return jsonify(result), 404

    try:
        re_pattern = re.compile(pattern)
    except re.error as e:
        result["reason"] = "Error compiling regular expression: {e}".format(e=e)
        return jsonify(result), 400

    try:
        for gist in gists:
            gist_obj = get_gist_by_id(gist["id"])

            for filename, file_data in gist_obj["files"].items():
                if re.search(re_pattern, file_data["content"]):
                    result["matches"].append(gist_obj)
                    break

        result["status"] = "success"  # good status only here
    except Exception as e:
        result["reason"] = e.__str__()
        return jsonify(result), 400

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
