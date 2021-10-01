"""

Copyright (c) 2021 Timo Haeckel
"""

import statedb
import traceback
import time
import datetime
from devicedetectionskill import DetectDevicePresenceSkill
from wheatherskill import WeatherSkill
from raumfeldskill import RaumfeldTVWakeup

# logFile = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".log"
jsonSettingsFile = "my_skills_config.json"
statedb = statedb.StateDataBase()
skillList = [
    DetectDevicePresenceSkill(statedb=statedb,
                              interval=30,
                              settingsFile=jsonSettingsFile),
    WeatherSkill(statedb=statedb, interval=300, settingsFile=jsonSettingsFile),
    RaumfeldTVWakeup(statedb=statedb,
                     interval=30,
                     settingsFile=jsonSettingsFile)
]


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
