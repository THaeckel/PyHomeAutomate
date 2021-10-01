"""
Skill to fetch weather state

WeatherState is a state data object for the WeatherSkill.
WeatherSkill is a Skill to fetch current weather information.

Copyright (c) 2021 Timo Haeckel
"""

from skills import SkillWithState
import requests
import json


class WeatherSkill(SkillWithState):
    """ Skill to detect devices present in the network.

    This skill sends ping probes to the device addresses to detect their 
    presence. Remember that a host may not respond to a ping (ICMP) request
    even if the host name is valid.
    The DevicePresenceState() with the key STATE_PREFIX+ADDRESS will be
    constantly updated.

    Settings
    --------
    {
        "statePrefix" : "Weather",
        "weatherRequestURL" : "http://weather.com/..."
    }

    Attributes
    ----------
    addresses : list(str)
        The device IPv4 addresses to be detected in the local network.
    STATE_PREFIX : str
        A prefix used to form the state key in the state data base with 
        STATE_PREFIX + Address  
    """
    STATE_PREFIX = "Weather"

    def __init__(self, statedb, settingsFile=""):
        """ 
        Parameters
        ----------
        statedb : statedb.StateDataBase
            The shared state data base instance used for all skills in 
            the home automation setup
        settingsFile : str
            Path to the global skill settings file
        """
        SkillWithState.__init__(self,
                                name="Weather",
                                statedb=statedb,
                                settingsFile=settingsFile)
        self.requestURL = self.findSkillSettingWithKey("weatherRequestURL")
        prefix = self.findSkillSettingWithKey("statePrefix")
        if prefix is not None:
            self.STATE_PREFIX = prefix

    def task(self):
        """ Refreshes the weather information

        This function will refresh the weather information for a request url.
        The weather json data with the key STATE_PREFIX will be updated.
        """
        weather = requests.get(self.requestURL).json()
        self.log("current weather:\n" + json.dumps(weather, indent=4))
        self.updateState(self.STATE_PREFIX, weather)
