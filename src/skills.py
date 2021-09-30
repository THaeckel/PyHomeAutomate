from threading import Thread, Event
import sys
import traceback
import datetime
import statedb


class Skill(Thread):
    def __init__(self, name, stopEvent, interval=0, errorSilent=False, logSilent=False, logFile=""):
        Thread.__init__(self)
        self.name = name
        self.stopEvent = stopEvent
        self.interval = interval
        self.errorSilent = errorSilent
        self.logSilent = logSilent
        self.logFile = logFile
              
    def printLog(self, text, level="INFO"):
        if len(text) > 0:
            printStr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + " (" + level + ") Skill " + self.name  + ": " + text
            if len(self.logFile) != 0:
                print(printStr, file=open(self.logFile, 'a'))
            else:
                print(printStr)
        sys.stdout.flush()

    def log(self, text):
        if not self.logSilent:
            self.log(text=text+traceback.format_exc, level="INFO")
        
    def error(self, text=""):
        if not self.errorSilent:
            self.log(text=text+traceback.format_exc, level="ERROR")

    # Override the run function of Thread class
    def run(self):
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

    # Override this function to implement the task of your skill
    def task (self):
        self.log("No task implemented for this skill ...stopping")
        self.stopEvent.set()


class SkillWithState(Skill):
    def __init__(self, name, stopEvent, stateDataBase, notifyOnStateChange=False, initialStates=dict(), interval=0, errorSilent=False, logSilent=False, logFile=""):
        Skill.__init__(self, name, stopEvent, interval, errorSilent, logSilent, logFile)
        self.statedb = stateDataBase
        self.initialStates = initialStates
        self.notifyOnChange = notifyOnStateChange
        self.initializeStates()

    def initializeStates(self):
        for key, value in self.initialStates.items():
            self.updateState(key, value)
            if self.notifyOnChange:
                self.observeState(key)

    def stateChangedCallback (self, stateName, stateValue):
        """
        This function is registered as a state changed callback function at the stateDataBase and is called when ever an obeserved state variable is updated. Overide this method and parse the stateName and stateValue accordingly.
        """
        self.log("Received unhandled notification for " + stateName + " with value " + stateValue )

    def observeState(self, stateName):
        if len(stateName) > 0:
            self.statedb.registerCallback(stateName, self.stateChangedCallback)

    def updateState(self, stateName, stateValue):
        """
        Updates the state of variable stateName with value stateValue
        """
        if len(stateName) > 0:
            self.statedb.setState(stateName,stateValue)

    def readState(self, stateName):
        return self.statedb.getState(stateName)
