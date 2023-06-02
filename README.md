# Eikon Backend Engineering Take-Home Challenge

### Assumptions
The submitted code makes the following assumptions -

1. The app would run in an env with docker installed, stable internet connection and have sufficient disk space to build the images (~1.5 GB)
2. The input data files will retain a similar structure to produce consistent processed output.
3. The features are computed for each user.
4. The "Average experiments amount per user" feature refers to the `experiment_run_time` field in user_experiments.csv file. The feature is calculated by grouping on user_id and taking the average of run_time across experiments.
5. Port 5000 is available in the env, that's where the flask app will listen.

### Quick overview of code and directory structure
- All the input csv files are in data folder and the scripts to facilitate execution are in the scripts folder.
- `app.py` contains all API and ETL logic.
- When /etl endpoint is evoked the `etl()` method is called internally which reads the csv files and performs some processing on it.
- Next the data is loaded into Pandas Dataframes and is transformed to extract the features.
- Finally the resultant DataFrame is persisted to the postgres DB. 

### Instructions to run
The application can be easily brought up and interacted with through the provided bash scripts in the scripts folder.
Make sure scripts are executable, if not run `chmod +x <script_name>.sh`.

**Note - All scripts must be triggered from inside the scripts folder to support relative paths** 

- `setup.sh`: This script pulls the postgres image, builds the python app image, create a docker network and then spins up the flask-app and mypostgres containers with the docker network so they can communicate.
- `trigger_etl.sh`: Runs the curl command to hit the etl endpoint. The API returns after the etl process is completed.
- `check_db.sh`: This script pings the postgres container and prints the features table.
- `cleanup.sh`: This script cleans all the artifacts created by `setup.sh` allowing easy re-runs. 

1. It might complain but it's a good idea to run cleanup.sh to make sure there are no collisions during setup. 
2. Navigate to scripts folder and run the setup.sh script. It might take a few minutes.
3. Run the trigger_etl script, you should see a success message.
4. Run check_db script which should print the features table.
5. Cleanup artifacts with the cleanup script.

### Improvements & design choices
1. Since here are ETL process is fairly simple, I didn't see the need to user a workflow orchestrator like AirFlow.
2. Right now, the `/etl` API is synchronous. This works fine because the ETL task is fairly simple and there isn't a lot of data. But for more complicated tasks it'd be a good idea to make the API asynchronous.
3. Since there weren't specific instructions on where the DB would run. I have opted to create a postgres DB in a container and connect it to the application over a Docker network. This does have the downside of the data not being retained after the container dies.
4. Finally, the DB creds are for now present in plain text in the `setup.sh` script and the `app.py` file. In a prod setup, where are container are managed by an orchestrator like Kubernetes we would probably store them as a secret and mount and access as env variables.