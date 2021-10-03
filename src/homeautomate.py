"""

Copyright (c) 2021 Timo Haeckel
"""

import statedb
import traceback
import time
import datetime
from devicedetectionskill import DetectDevicePresenceSkill
from wheatherskill import WeatherSkill
from daytimeskill import DaytimeSkill
from raumfeldskill import RaumfeldTVWakeup
from hueskill import HueDaytimeAndWeatherSkill

# logFile = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + ".log"
jsonSettingsFile = "my_skills_config.json"
statedb = statedb.StateDataBase()
skillList = [
    DetectDevicePresenceSkill(statedb=statedb, settingsFile=jsonSettingsFile),
    WeatherSkill(statedb=statedb, settingsFile=jsonSettingsFile),
    DaytimeSkill(statedb=statedb, settingsFile=jsonSettingsFile),
    RaumfeldTVWakeup(statedb=statedb, settingsFile=jsonSettingsFile),
    HueDaytimeAndWeatherSkill(statedb=statedb, settingsFile=jsonSettingsFile)
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
