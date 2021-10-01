"""
Base implementations for home automation skills

Skill class implements a thread with a task executed every interval.
SkillWithState implements a Skill with a connection to the state data base.

Copyright (c) 2021 Timo Haeckel
"""

from threading import Thread, Event
import sys
import traceback
import datetime
import json
import statedb


def findKeyInJson(jsonDict, searchKey):
    """ Search for recursive for a key in a JSON dictionary.

    General purpose function to look for a key in a json file.

    Parameters
    ----------
    jsonDict : dict()
        Dictionary containing a json structure
    searchKey : str
        The key to look for in the settings

    Returns
    -------
    value : jsonObject
        The json object that is found behind the searchKey.
    """
    for key in jsonDict:
        value = jsonDict[key]
        if key == searchKey:
            return value
        elif isinstance(value, dict):
            #launch recursion
            inner = findKeyInJson(value, searchKey)
            if inner is not None:
                return inner
    return None


class Skill(Thread):
    """
    Settings
    --------
    {
        "SKILLNAME" : {
            "setting1" : "value",
            "setting2" : [
                "value",
                "value"
                ]
        }
    }
    """
    def __init__(self,
                 name,
                 interval=0,
                 settingsFile="",
                 errorSilent=False,
                 logSilent=False,
                 logFile=""):
        """ 
        Parameters
        ----------
        name : str
            The name of the skill
        interval : int (Default 0)   
            The time in seconds to wait between each execution of the skill
        settingsFile : str
            Path to the global skill settings file.
        errorSilent : Boolean (Default False)
            True if errors shall not be printed
        logSilent : Boolean (Default False)
            True if log messages shall not be printed
        logFile : str (Default "")
            Path to the log file to be used for errors and log messages
        """
        Thread.__init__(self)
        self.name = name
        self.stopEvent = Event()
        self.interval = interval
        if len(settingsFile) > 0:
            settings = open(settingsFile)
            self.settings = json.load(settings)
        else:
            self.settings = ""

        self.errorSilent = errorSilent
        self.logSilent = logSilent
        self.logFile = logFile

    def findSkillSettingWithKey(self, settingKey):
        """ Searches for the key in the skills json settings.
        
        Parameters
        ----------
        settingKey : str
            The key to look for in the settings

        Returns
        -------
        value : jsonObject
            The json object that is found behind the searchKey.
        """
        if len(self.settings) > 0:
            skillSettings = findKeyInJson(self.settings, self.name)
            return findKeyInJson(skillSettings, settingKey)
        else:
            return None

    def printLog(self, text, level="INFO"):
        """ Prints a log message.

        Prints a log message with the current time, its level and the Skill
        name to a file if self.logFile is set, else the message is printed 
        to the console. 
 
        Parameters
        ----------
        text : str
            The log message to print
        """
        if len(text) > 0:
            printStr = str(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ) + " (" + level + ") Skill " + self.name + ": " + text
            if len(self.logFile) != 0:
                print(printStr, file=open(self.logFile, 'a'))
            else:
                print(printStr)
        sys.stdout.flush()

    def log(self, text):
        """ Prints a log message.

        Prints a log message if logSilent is not set, using the 
        printLog function and attaches the INFO type. 

        Parameters
        ----------
        text : str
            The log message to print
        """
        if not self.logSilent:
            self.printLog(text=text, level="INFO")

    def error(self, text=""):
        """ Prints an error message.

        Prints an error message if errorSilent is not set, using the 
        printLog function and attaches the ERROR type. 

        Parameters
        ----------
        text : str
            The error message to print
        """
        if not self.errorSilent:
            self.printLog(text=text + str(traceback.format_exc), level="ERROR")

    def run(self):
        """ Run function of the Skill !NOT ITS TASK!

        This function runs the Skill task every interval. The run function
        is stopped whend the stopEvent is set. Please override the task() 
        function for your skill implementation not this function.
        """
        self.log("skill launched ")
        while not self.stopEvent.is_set():
            try:
                self.task()
                self.stopEvent.wait(self.interval)
            except KeyboardInterrupt:
                continue
            except Exception:
                self.error("task failed ")
        self.log("skill terminated ")

    def task(self):
        """ The task of the Skill.

        This function shall be overwritten with the implementation of the 
        Skill itself. It is called by the run function of this Skill every
        interval. 
        """
        self.log("No task implemented for this skill ...stopping")
        self.stopEvent.set()


class SkillWithState(Skill, statedb.StateDataBaseObserver):
    """ A Skill with a connection the state data base.

    An abstract implementation extending a basic Skill with 
    a connection to the global state data base instance. 
    Provides functions to updateState, readState, and observeState.
    The function stateChangedCallback() shall be overwritten to
    react on observed state changes.

    Attributes
    ----------
    stateDataBase : statedb.StateDataBase
        Reference to the shared state data base instance used for 
        all skills in the home automation setup
    """
    def __init__(self,
                 name,
                 statedb,
                 interval=0,
                 settingsFile="",
                 errorSilent=False,
                 logSilent=False,
                 logFile=""):
        """ 
        Parameters
        ----------
        name : str
            The name of the skill
        statedb : statedb.StateDataBase
            The shared state data base instance used for all skills in 
            the home automation setup
        interval : int (Default 0)   
            The time to wait between each execution of the skill
        settingsFile : str
            Path to the global skill settings file.
        errorSilent : Boolean (Default False)
            True if errors shall not be printed
        logSilent : Boolean (Default False)
            True if log messages shall not be printed
        logFile : str (Default "")
            Path to the log file to be used for errors and log messages
        """
        Skill.__init__(self,
                       name=name,
                       interval=interval,
                       settingsFile=settingsFile,
                       errorSilent=errorSilent,
                       logSilent=logSilent,
                       logFile=logFile)
        self.statedb = statedb

    def stateChangedCallback(self, stateName, stateValue):
        """ Callback function for changes is the state data baseself.

        This function is registered as a state change callback function 
        at the stateDataBase and is called when ever an obeserved state 
        variable is updated. Overide this method and parse the stateName 
        and stateValue accordingly.   

        Parameters
        ----------
        stateName : str
            The name of the state that is used as a key
        stateValue : complex type
            The value of the state which can be of any complex type    
        """
        self.log("Received unhandled notification for " + stateName +
                 " with value " + stateValue)

    def observeState(self, stateName):
        """ Register for notifications if the given state changes.

        The stateChangedCallback of this skill is registered as an observer
        function to be notified if the given state is updated.

        Parameters
        ----------
        stateName : str
            The name of the state that is used as a key an shall be observed
        """
        if len(stateName) > 0:
            self.statedb.registerCallback(stateName, self.stateChangedCallback)

    def updateState(self, stateName, stateValue):
        """ Updates the given state with the given value.
        
        Updates the state with the key stateName in the state data base 
        with the new value of stateValue.

        Parameters
        ----------
        stateName : str
            The name of the state that is used as a key
        stateValue : complex type
            The value of the state which can be of any complex type
        """
        if len(stateName) > 0:
            self.statedb.setState(stateName, stateValue)

    def readState(self, stateName):
        """ Reads the value of the given state.

        Fetches the state with the key stateName from the state data base 
        and returns its value.

        Parameters
        ----------
        stateName : str
            The name of the state that is used as a key
        
        Returns
        -------
        complex type
            The value of the state which can be of any complex type
            None if the state does not exist
        """
        return self.statedb.getState(stateName)
