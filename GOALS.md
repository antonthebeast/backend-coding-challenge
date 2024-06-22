## Implement a few tests (using a testing framework of your choice)

Initially started to write tests in Postman, then moved to pytest

## In all places where it makes sense, implement data validation, error handling, pagination

All the code is covered with try..except

## Migrate from `requirements.txt` to `pyproject.toml` (e.g. using [poetry](https://python-poetry.org/))

First install poetry with

```bash
pip install poetry
```

Then I will move requirements with

```bash
poetry add $(cat requirements.txt)
```

Another way is to manually move requirements:

```toml
[project]
name = "backend-coding-challenge"
version = "0.1.0"
description = "locoia Python project"
authors = [
    { name="Anton Kononov", email="korselmain@gmail.com" }
]

dependencies = [
    "Flask==2.2.2",
    "requests=2.28.1",
    "Werkzeug=2.2.2"
]
```

## Implement a simple Dockerfile

I would start with something like this:

```Dockerfile
# Use the official base image of Python
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry for managing dependencies
RUN pip install poetry

# Install project dependencies
RUN poetry install --no-root

# Copy the project contents to the container
COPY . /app

# Expose the port on which Flask will run
EXPOSE 9876

# Define the command to start the application
CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--port=9876"]

```

Then build and run:

```bash
docker build -t my-flask-app .
docker run -p 9876:9876 my-flask-app
```

## Implement handling of huge gists

Huge gists should be loaded in chunks or in async. I would take chunks for this small project. Something like that:

```py
url = "https://api.github.com/gists/{gist_id}".format(gist_id=gist_id)
regex = re.compile(pattern)
response = requests.get(url, stream=True)

# Initialize a variable to store any partial matches
partial_match = ""

# Iterate over the response data in chunks
for chunk in response.iter_content(chunk_size=1024):
    # Concatenate the partial match and the current chunk
    data = partial_match + chunk.decode("utf-8")

    # Search for the pattern in the data
    match = regex.search(data)

    # If a match is found, add gist to `result[matches]`
    if match:
        # ...

    # Update the partial match with any remaining data
    partial_match = data[match.end():] if match else data
```

So we could stop loading gist if our pattern already found.

## Set up the necessary tools to ensure code quality (feel free to pick up a set of tools you personally prefer)

I like code review as one of the best "tools" for code quality.

Also some linting could help (for example `pylint`).

## Document how to start the application, how to build the docker image, how to run tests, and (optionally) how to run code quality checkers

For debugging I used this to start app:

```bash
python gistapi/gistapi.py
```

and this to test:

```bash
pytest
```

## Can we use a database? What for? SQL or NoSQL?

Database can be used to cache foreign api (for example calls to Githup api). We can cache gist list for the user, the list has `updated_at` field, so we can use cached value rather that reading real gist.

Maybe NoSQL is better (if gists are big), but SQL database also can be used.

## How can we protect the api from abusing it?

Some standard methods:
* Limit the number of requests from one user (total or in period of time)
* Use Auth so that only registered users can access
* Use cache
* CORS
* Limit user's IP (white/black)
* Logging, monitoring
* Some anti-bot methods: captcha, data rate limit

## How can we deploy the application in a cloud environment?

* Dockerize the app
* Push image to container registry
* Deploy to cloud

## How can we be sure the application is alive and works as expected when deployed into a cloud environment?

Sending a `/ping` requests is the easiest way.

Also cloud systems have their own methods to monitor activity.

Logging all important function calls can also help.
