# Integration Engineering Team Leader Quiz

## FastAPI nano
Originally, this repo was created from the boilerplate [fastapi-nano](https://github.com/rednafi/fastapi-nano)
but I made a lot of changes to it for my personal needs and preferences.

## How to add new dependency
First of all, this project will follow [PEP 505](https://peps.python.org/pep-0508/)
please refer to the link, and we will use Poetry to manage our packaging versioning (You can think it will like Pip with lock version of Nodejs).

Set to install:
1. Install "Poetry" in your local development please follow the guide here [Poetry](https://python-poetry.org/docs/)
2. To add new dependency please add in the [pyproject.toml](./pyproject.toml) file 
   - 2.1.1) If that dependency is essential in the production env please add that in the [tool.poetry.dependencies] section
or you can run the command:
    ```bash
        poetry add black
    ```
   - 2.1.2) If that dependency is only need for development env please add it
in the production env please add that in the [tool.poetry.group.dev.dependencies] section or you can run the command:
    ```bash
        poetry add black -D
    ```
   - NOTE!!: Eveytime         
 you make the update to the dependency pyproject.toml file
please also update the poetry.lock as well (if it not updates yet) by running
    ```bash
   poetry lock --no-update
    ```
ref: https://stackoverflow.com/questions/58961497/how-to-update-poetrys-lock-file-without-upgrading-dependencies

3. Next step

    For the installation in local you can do the following </br>
    Set up a venv in your local like this for example
    ```bash
        python3.11 -m venv .venv
    ```
    and then run
    ```bash
        poetry config virtualenvs.in-project true --local
    ```
       to install core dependencies you run:
    ```shell
    poetry install --no-root 
    ```
    or run this if you don't want the dev dependencies
    ```shell
    poetry install --no-root --no-dev
    ```
    to run the application, test, or make lint you you can do like this
    ```shell
    poetry run pytest
    ```
    ```shell
    poetry run make lint-check
    ```
    ```shell
    poetry run uvicorn app.main:app --port 5000 --reload
    ```

## Dependency injection and inversion of control
If you still not familiar with this concept please do some research,
here is some good resources: https://python-dependency-injector.ets-labs.org/introduction/di_in_python.html, https://www.youtube.com/watch?v=J1f5b4vcxCQ&ab_channel=CodeAesthetic

In this project I try to adapt the python-dependency-injector with our FastAPI to implement DI.
Please refer to their documentation and some tutorial, it is very helpful.
https://python-dependency-injector.ets-labs.org/providers/index.html
https://python-dependency-injector.ets-labs.org/examples/index.html

## Testing

We will mostly use mock to test our code, please see some example code in the repo.
the point of test is to test "our code" - meaning the code we wrote, including unittest (function, class,..) 
to integration level test (put some part of code together).

So please do test on the code you wrote, integration test is a must for delivering an API.
For other part external part of the system like Auth0, DB, AWS,... you don't have to test that.

## DB Change Management 

Currently, sqlalchemy doesn't support update when model changing (it can only create new table).
The solution is to use Alembic to do that.
Please refer here on some tutorial: [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

So if you have some updates to the db models, please help update Alembic folder as well,
Here are some steps to follow when update db:
1. Config DB credentials:
```bash
   export DB_URL <something>
```
Alternative way is changing sqlalchemy.url the [alembic.ini](./alembic.ini) 
but please do it only in localhost, don't commit that

2. Create a Migration Script:
```bash
   alembic revision -m "create account table"
```
this command will create a file in alembic/development, if you want to use production env:
```bash
   alembic --name production revision -m "create account table"
```

3. Update your Migration Script
4. Run to apply changes:
```bash
   alembic upgrade head
```
or
```bash
   alembic --name production upgrade head
```



## Configuration

We will use  [config.yml](./config.yml) to set some of the configuration variable for our project.
Some important note!!: 
- For some config like this ${AWS_ACCESS_KEY_ID}, ${ENV_NAME},... meaning they are the 
environment variable in your local machine, or they can be set in the run time of the application,...
please refer to this to update on those setting on MacOS, Window, Ubuntu..
- ${ENV_NAME:"local"} meaning it will look for your env if not it get default as "local" 
- For ${AWS_SECRET_ACCESS_KEY} please read this https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html
- Some section in the yaml file have the structure like this:
```yaml
    s3_image_bucket:
      production: "sensayai-images"
      development: "sensayai-images-dev"
      local: "sensayai-images-local"
```
meaning they can switch-variant base on the ENV_NAME you currently running, 
so if you want you can update those section to update the variable for 
the environment you want to run the application on
- reference: https://python-dependency-injector.ets-labs.org/providers/configuration.html

## Architecture - Project Structure
| Layer Name       | Description                                                                                                                                                                                                   | Dependencies |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|
| Models           | This define domain models. The business logic should be implemented in this package, some example to put in models are: db entity/object, some modeling of the application, api input/output schema object... | No           |
| Infrastructures  | This handles the external interaction like DB, GoogleSheet, Auth0, and etc. Within this project, library exposing data structure should be converted into the domain models                                   | Yes          |
| Services         | This should implement use cases using infrastructures & domain-models.                                                                                                                                        | Yes          |
| Routes -Endpoint | This should include the code run an application and application specific logic like HTTP Endpoint or background workers                                                                                       | Yes          |
| Container        | This will include the Dependency Injector Container to provide and wire up the dependency for the application                                                                                                 | ---          |
| Other tooling    | Other tool like Docker, Script, GithubAction, Alchemic, Poetry ... will set up along with this service as well to help set up the project and deployment                                                      | ---          |


The image bellow show the overview of this architecture

![img.png](ProjectArchitecture&Structure.png)
(The arrow meaning: Service <--- Model mean that Service layer will have the dependency from Model layer)
