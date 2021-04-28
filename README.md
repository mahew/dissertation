# Software User Documentation
## Setup and Requirements
### Requirements
- Windows 10 or Linux (Ubuntu Preferred)
- Python 3.6 & Pip
- MongoDB Atlas Database Access String
### Setup
#### Database Setup
- Create or use an exisiting MongoDB cluster, including the free tier from [MongoDB Atlas Get Started](https://docs.atlas.mongodb.com/getting-started/)
- Set the POETRY_CONN_STRING environment variable according to your operating system to your MongoDB connection string, for example in Linux
```
export POETRY_CONN_STRING="mongodb+srv://USERNAME:PASSWORD@iot-see.rcen0.mongodb.net/"
```
#### Software Setup
In a shell or console, install poetry using 
```
pip install poetry
```
Change into the projects main directory 
```
cd iot-see
```
Now install the Python requirements with 
```
poetry install
```
Once the requirements are installed, create a virtual environment shell using 
```
poetry shell
```

## Running the Project
Using the virtual environment, run 
```
python main.py
```

If you are running the project for the first time, you will have to set up the device in the console,
this is used to correlate the vehicle detections to the device and session. You should be promoted to name the device and its location, this will then be saved to the provided database in the devices collection.

Once the device is saved, the software should be running using the default settings and included traffic video
you should see the tracking results in a window called "Frame" as shown below.

![Example Frame](https://cdn.discordapp.com/attachments/761551359706791957/836960696927387749/GUI.png)

You can exit the program at any time by pressing "Q" on your keyboard, closing the frame will just re open it.

### Changing the default tracking settings
You can view help for changing the default tracking settings using
```
python main.py --help
```
this will display the following options
```
usage: main.py [-h] [--input INPUT] [--roi ROI] [--skip SKIP] [--maxw MAXW]
               [--verbose VERBOSE] [--testing TESTING]

Tracking Settings for Matthew Ball's tracking project

optional arguments:
  -h, --help         show this help message and exit
  --input INPUT      The input video or stream of traffic images
  --roi ROI          Region of Interest Value (Y Cut Off)
  --skip SKIP        Number of skip frames
  --maxw MAXW        Max Width Value used to resize input frame
  --verbose VERBOSE  Verbose option, used to show the input frame, will
                     increase performance when disabled
  --testing TESTING  Manual Testing Option, only works with default input
                     video, enables Verbose mode
```
you can change any of these options as you would like, but there are default values for all arguments if you would prefer to use these.

the tracked vehicles should be logged into your MongoDB database with current timestamps, directions and labels