## Steps to Run the IoT Service
This document describes the steps to run the IoT service on your local machine.

### IoT-Libs
To run the IoT service, you need to install the [iot-libs](https://gitlab.com/groups/mse-jbi/project_work/-/packages) package.
Refer to the [GitLab documentation](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token) 
for instructions on creating a personal access token.
Set the `PIP_EXTRA_INDEX_URL` environment variable to point to the GitLab package registry by running the following command:

On Windows:
```bash
setx PIP_EXTRA_INDEX_URL "https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/61911828/packages/pypi/simple"
```
On Linux
```bash
export PIP_EXTRA_INDEX_URL="https://__token__:<your_personal_token>@gitlab.com/api/v4/projects/61911828/packages/pypi/simple"
```
You can check if the environment variable is set by running the following command:
```bash
pip config list
```
Expected output:
```bash
:env:.extra-index-url='https://__token__:******@gitlab.com/api/v4/projects/61911828/packages/pypi/simple' 
```

## Virtual Environment
After setting the pip index URL you can create a virtual environment for each of the services by running this command from the **repository root path**
with the corresponding authorizations (permissions to create directories).
```bash
/utils/update_packages.bat
```
Now in each of the service directories, there should be a `venv` directory with the necessary packages installed.

## Run and Setup the Database
In order to run the database, you need to have [Docker](https://www.docker.com) installed on your machine.
To run the [TimescaleDB container](https://hub.docker.com/r/timescale/timescaledb-ha) you can run the following command from the **repository root path**:
```bash
docker compose up -d
```
You can check if the container is running by running the following command:
```bash
docker ps
```
Expected output:
```bash
CONTAINER ID   IMAGE                           COMMAND                  CREATED         STATUS         PORTS                                         NAMES
033672b3bc67   timescale/timescaledb-ha:pg16   "/docker-entrypoint.…"   8 seconds ago   Up 2 seconds   8008/tcp, 8081/tcp, 0.0.0.0:50000->5432/tcp   timescaledb
```
To setup the database, you can run the following command from the **src_db_manager** path:
```bash
venv/Scripts/activate
```
Start the database manager script by running the following command:
```bash
python db_manager/main.py
```
You can connect to the database using [pgAdmin](https://www.pgadmin.org/) or any other database management tool by using the following credentials:
Username: `postgres` <br>
Password: `1`
The database should have a `tenant_100000` with `device`, `metrics`, and `numeric_scalar_values` tables (see [Appendix A](#appendix-a-pgadmin-example)).

## Run the IoT Service
To run the IoT service you can run each service (edge_device, device_mgmt, hub) in vscode  using the launch.json file in the `.vscode` directory (see [Appendix B](#appendix-b-start-iot-service-in-vscode)). <br> 
Or you can run the following command from the **repository root path**:
```bash
/utils/start_services.bat
```

## Interact with the Service
You can use [Postman](https://www.postman.com/) to interact with the IoT service or over a browser [Device Managment API](http://127.0.0.1:8000/docs). In order to use Postman,
you can use the Postman [collection](data/postman/IoT.postman_collection.json). 

## Video Examples
[Service Example](/videos/wiki/iot_service_example_v1.0.0.mp4) <br>
[Database Example](/videos/wiki/database_example_v1.0.0.mp4)

# Appendix

## Appendix A: pgAdmin Example
![pgadmin](/images/wiki/pgadmin.png)

## Appendix B: Start IoT service in VSCode
![start iot service](/images/wiki/vscode_start_iot_platform.png)