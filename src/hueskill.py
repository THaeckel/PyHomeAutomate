"""
Skills to control hue smart lights

HueDaytimeAndWeatherSkill is a Skill that adapts hue lights to daytime and weather.

Copyright (c) 2021 Timo Haeckel
"""

from skills import SkillWithState
import colorsys
import datetime
from phue import Bridge


class HueDaytimeAndWeatherSkill(SkillWithState):
    """ Skill adapt hue lights to daytime and weather
    
    This skill adapts the hue lighting to the daytime and weather state provided by the WeatherSkill and DaytimeSkill.

    Settings
    --------
    {
        "daytimeStatePrefix" : "Daytime",
        "weatherStatePrefix" : "Weather",
        "hueBridgeIp" : "192.168.178.42",
        "lightsToAutomate" : ["Desklamp", "Kitchen Mainlight"],
        "sceneNightMode" : "Gedimmt",
        "sceneDayModeLight" : "Energie tanken",
        "sceneDayModeDark" : "Hell",
        "maxCloudsClear" : 80,
        "minCloudsCloudy" : 90,
        "sceneTransitionTime" : 300 #= 30 sec
    }

    Attributes
    ----------
    DAYTIME_STATE_PREFIX : str
        A prefix used to access the daytime state
    WEATHER_STATE_PREFIX : str
        A prefix used to access the weather state
    hue : Bridge()
        The hue bridge access
    sceneNightMode : str
        Name of the scene that shall be activated during the night
    sceneDayModeLight : str
        Name of the scene that shall be activated during dark days
    sceneDayModeDark : str
        Name of the scene that shall be activated during light days
    lightsToAutomate : list(str)
        Lights that shall be controlled with this skill
    maxCloudsClear : int
        Maximum cloud level that will be regarded as a clear sky
    minCloudsCloudy : int
        Minimum cloud level that will be regardes as cloudy 
    sceneTransitionTime : int
        Time for transition between scenes in .1 seconds (e.g., 300 = 30sec)
    lastModeSet : str
        on of the static modes below
    """
    MODE_SLEEP = "SLEEP"
    MODE_DAY_CLEAR = "DAY_CLEAR"
    MODE_DAY_DARK = "DAY_DARK"
    MODE_DAY_MODERATE = "DAY_MODERATE"
    MODE_SUNRISE = "SUNRISE"
    MODE_SUNSET = "SUNSET"
    MODE_NIGHT = "NIGHT"

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
                                name="HueDaytimeAndWeather",
                                statedb=statedb,
                                settingsFile=settingsFile)
        self.DAYTIME_STATE_PREFIX = self.findSkillSettingWithKeyOrDefault(
            "daytimeStatePrefix", "Weather")
        self.WEATHER_STATE_PREFIX = self.findSkillSettingWithKeyOrDefault(
            "weatherStatePrefix", "Daytime")
        self.hue = Bridge(self.findSkillSettingWithKey("hueBridgeIp"))
        self.lightsToAutomate = self.findSkillSettingWithKeyOrDefault(
            "lightsToAutomate", [])
        self.sceneNightMode = self.findSkillSettingWithKeyOrDefault(
            "sceneNightMode", "Gedimmt")
        self.sceneDayModeLight = self.findSkillSettingWithKeyOrDefault(
            "sceneDayModeLight", "Energie tanken")
        self.sceneDayModeDark = self.findSkillSettingWithKeyOrDefault(
            "sceneDayModeDark", "Hell")
        self.maxCloudsClear = self.findSkillSettingWithKeyOrDefault(
            "maxCloudsClear", 80)
        self.minCloudsCloudy = self.findSkillSettingWithKeyOrDefault(
            "minCloudsCloudy", 90)
        self.sceneTransitionTime = self.findSkillSettingWithKeyOrDefault(
            "sceneTransitionTime", 300)
        self.lastModeSet = ""

    def convert_rgb_to_hue(rgbcolor):
        hsvcolor = colorsys.rgb_to_hsv(rgbcolor[0], rgbcolor[1], rgbcolor[2])
        huecolor = (int(hsvcolor[0] * 65535), int(hsvcolor[1] * 255),
                    int(hsvcolor[2]))
        return huecolor

    def turnLightsOff(self):
        """ Turns all lightsToAutomate off

        Sets the state of all lights in lightsToAutomate to off
        """
        if len(self.lightsToAutomate) > 0:
            for light in self.lightsToAutomate:
                if not self.hue.get_light(light)["state"]["reachable"]:
                    self.log("Light " + light + " unreachable ")
                else:
                    self.hue.set_light(light, "on", False)
                    self.log("Turned light " + light + " off")

    def getRoomForLightName(self, light):
        """ Get a room from the light name

        Looks for the light name in all rooms and returns the name of the first room containing the light.

        Parameters
        ----------
        light : str
            The name of the light to look for

        Returns
        -------
        str : the name of the room the light belongs to, None if no room is found 
        """
        lightId = self.hue.get_light_id_by_name(light)
        for info in self.hue.get_group().values():
            if lightId in info['lights']:
                return info['name']
        return None

    def setScene(self, scene):
        """ Sets a scene for all rooms containing one of lightsToAutomate
        
        Looks for all rooms containing lightsToAutomate and sets the given scene with the transition time in self.sceneTransitionTime.

        Parameters
        ----------
        scene : str
            The name of the hue scene to be set
        """
        if len(self.lightsToAutomate) > 0:
            for light in self.lightsToAutomate:
                if not self.hue.get_light(light)["state"]["reachable"]:
                    self.log("Light " + light + " unreachable ")
                else:
                    self.hue.run_scene(
                        self.getRoomForLightName(light),
                        scene,
                        transition_time=self.sceneTransitionTime)
                    self.log("Activated scene " + scene + " for light " +
                             light)

    def activateSleepMode(self):
        """ Activates the sleep mode for all lightsToAutomate

        To be implemented
        """
        # self.turnLightsOff()
        self.log("Sleep mode not implemented yet")

    def activateSunriseMode(self):
        """ Activates the sunrise mode for all lightsToAutomate

        To be implemented
        """
        self.log("Sunrise mode not implemented yet")

    def activateSunsetMode(self):
        """ Activates the sunset mode for all lightsToAutomate

        To be implemented
        """
        self.log("Sunset mode not implemented yet")

    def task(self):
        """ Adapts hue lights to changes in daytime and weather

        This function will adapt the light to changes in the daytime and weather data.
        """
        weather = self.readState(self.WEATHER_STATE_PREFIX)
        daytime = self.readState(self.DAYTIME_STATE_PREFIX)
        if daytime is None:
            self.log("DaytimeState not avialable ")
            return
        if weather is None:
            self.log("WeatherState not avialable ")
            return

        if daytime.isBedTime():
            if not self.lastModeSet == self.MODE_SLEEP:
                self.log("Setting bedtime sleep mode...")
                self.activateSleepMode()
                self.lastModeSet = self.MODE_SLEEP
        else:
            if daytime.isDayTime():
                if weather.getClouds() < self.maxCloudsClear:
                    if not self.lastModeSet == self.MODE_DAY_CLEAR:
                        self.log("Setting clear day mode...")
                        self.turnLightsOff()
                        self.lastModeSet = self.MODE_DAY_CLEAR
                elif weather.getClouds(
                ) > self.minCloudsCloudy or weather.isRaining():
                    if not self.lastModeSet == self.MODE_DAY_DARK:
                        self.log("Setting dark day mode...")
                        self.setScene(self.sceneDayModeDark)
                        self.lastModeSet = self.MODE_DAY_DARK
                else:
                    if not self.lastModeSet == self.MODE_DAY_MODERATE:
                        self.log("Setting light day mode...")
                        self.setScene(self.sceneDayModeLight)
                        self.lastModeSet = self.MODE_DAY_MODERATE
            elif daytime.isSunriseTime():
                if not self.lastModeSet == self.MODE_SUNRISE:
                    self.log("Setting sunrise mode...")
                    self.activateSunriseMode()
                    self.lastModeSet = self.MODE_SUNRISE
            elif daytime.isSunsetTime():
                if not self.lastModeSet == self.MODE_SUNSET:
                    self.log("Setting sunset mode...")
                    self.activateSunsetMode()
                    self.lastModeSet = self.MODE_SUNSET
            elif daytime.isNightTime():
                if not self.lastModeSet == self.MODE_NIGHT:
                    self.log("Setting night mode...")
                    self.setScene(self.sceneNightMode)
                    self.lastModeSet = self.MODE_NIGHT
