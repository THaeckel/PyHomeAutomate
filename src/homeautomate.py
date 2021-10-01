"""

Copyright (c) 2021 Timo Haeckel
"""

import statedb
import traceback
import time
import datetime
from devicedetectionskill import DetectDevicePresenceSkill

skillList = []
statedb = statedb.StateDataBase()
# logFile = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".log"
deviceDetectionAddresses = ["localhost"]


# Initialize your skills in this function!
def createSkills():
    detectSkill = DetectDevicePresenceSkill(
        statedb=statedb, deviceAddresses=deviceDetectionAddresses, interval=10)
    skillList.append(detectSkill)


def startSkills():
    for skill in skillList:
        skill.start()
        time.sleep(10)


def joinSkills():
    for skill in skillList:
        skill.join()


def interruptSkills():
    for skill in skillList:
        skill.stopEvent.set()


if __name__ == "__main__":
    try:
        print("Starting")
        createSkills()
        startSkills()
        joinSkills()
    except KeyboardInterrupt:
        print("terminating...")
        interruptSkills()
    except Exception:
        print("Error... " + str(traceback.format_exc))
    finally:
        joinSkills()
        print("Terminated")
