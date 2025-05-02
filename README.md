# CITS3403-Project

An application to track your media consumption habits.

The idea is, at the end of the day, the user can log (approximately) the time spend on certain media **titles** (i.e. we are not tracking your youtube consumption or how long you spent watching the news).

To log an activity, click on the **new activity** button on the dashboard and select a **media type**, an optional **media subtype**, and input a **media name**. The activity will now appear on the dashboard. To log time spent on that title, simply input a duration and click **add**. 

To run the web application, navigate to the project root and install the required dependencies:
```
pip install -r requirements.txt
```

To avoid conflicts with your existing python environment, you may create a virtual environment before installing dependencies:
```
python -m venv <virtual-environment-path>
source <virtual-environment-path>/bin/activate
```

This application requires sqlite3 to run. If you do not have sqlite3 installed, you can install via:
```
sudo apt update
sudo apt install sqlite3
```
