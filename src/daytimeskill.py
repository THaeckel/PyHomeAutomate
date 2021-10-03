"""
Skill that evaluates the current day time

DaytimeState is a state data object providing information about current daytime
DaytimeSkill is a Skill to detect the current daytime

Copyright (c) 2021 Timo Haeckel
"""

from skills import SkillWithState
import time
import datetime


class DaytimeState():
    """ State data object for the DetectDevicePresenceSkill.

    Attributes
    ----------
    bedtime : bool
        True if it is currently bed time
    daytime : str
        one of:
        DAY_STR = "Daytime"
        SUNRISE_STR = "Sunrise"
        SUNSET_STR = "Sunset"
        NIGHT_STR = "Nighttime"
    options : list(str)
        contains all valid options for daytime
    """
    DAY_STR = "Day"
    SUNRISE_STR = "Sunrise"
    SUNSET_STR = "Sunset"
    NIGHT_STR = "Night"
    options = [DAY_STR, SUNRISE_STR, SUNSET_STR, NIGHT_STR]

    def __init__(self, daytime=DAY_STR):
        self.setDayTime(daytime)
        self.bedTime = False

    def setDayTime(self, daytime):
        if daytime in self.options:
            self.daytime = daytime

    def isDayTime(self):
        return self.daytime == self.DAY_STR

    def isSunriseTime(self):
        return self.daytime == self.SUNRISE_STR

    def isSunsetTime(self):
        return self.daytime == self.SUNSET_STR

    def isNightTime(self):
        return self.daytime == self.NIGHT_STR

    def isBedTime(self):
        return self.bedTime


class DaytimeSkill(SkillWithState):
    """ Skill to detect the current daytime

    This skill detects whether it is day time, sunset, oder night time based 
    on the weather information from the WeatherSkill. The bed time is detected 
    based on the settings for each day (example below). 
    I had difficutlies finding a good format so I did the format I found most 
    sensible: The time is in 24h:60M and counted from midday to next midday 
    the day the night has started on, e.g. "friday": "03:00-08:00" is actually 
    saturday 3am to 8am but still counts as friday night. The border is mid 
    day so you must not sleep till 1pm :-P 
    If no bedTime is wanted ever or on a certain day just not set it in the JSON settings file.

    Settings
    --------
    {
        "statePrefix" : "DayTime",
        "bedTime" : {
            "monday" : "23:00-07:00",            
            "tuesday" : "23:00-07:00",
            "wednesday" : "23:00-07:00",
            "thirsday" : "23:00-07:00",
            "friday" : "03:00-08:00",
            "saturday" : "03:00-08:00",
            "sunday" : "23:00-07:00"
        }
    }

    Attributes
    ----------
    bedTime : dict(str, str)
        The bedtime as described in the settings
    STATE_PREFIX : str
        A prefix used to form the state key in the state data base
    """
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
                                name="Daytime",
                                statedb=statedb,
                                settingsFile=settingsFile)
        self.STATE_PREFIX = self.findSkillSettingWithKeyOrDefault(
            "statePrefix", "Daytime")
        bedTime = self.findSkillSettingWithKeyOrDefault("bedTime", dict())
        if len(bedTime) > 0:
            for day, timeInterval in bedTime.items():
                self.bedTime[day] = self.parseTimeInterval(day, timeInterval)

    def checkBedTime(self):
        """ 
        Checks weather current time is in the bedTime list.

        Returns
        -------
        Bool : True if it there is a bedTime entry for now
        """
        #helper variables
        currentDatetime = datetime.datetime.now()
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        # check if currently before midday and alter lookupday if necessary
        lookupday = currentDatetime.strftime("%A").lower()
        beforeMidday = False
        if currentDatetime < datetime.datetime.combine(
                today, datetime.time(12, 0, 0)):
            beforeMidday = True
            lookupday = yesterday.strftime("%A").lower()
        # find todays entry from list with 12 to 12 wrap
        if len(self.bedTime) > 0 and lookupday in self.bedTime:
            # there is an entry for today!
            # prepare the settings data
            interval = self.bedTime[lookupday].split('-')
            startSplit = interval[0].split(':')
            endSplit = interval[1].split(':')
            startTime = datetime.time(int(startSplit[0]), int(startSplit[1]))
            endTime = datetime.time(int(endSplit[0]), int(endSplit[1]))
            # find out for which day start and end time are ment?!
            if beforeMidday:
                endTime = datetime.datetime.combine(today, endTime)
                if startTime > datetime.time(12, 0, 0):
                    startTime = datetime.datetime.combine(yesterday, startTime)
                else:
                    startTime = datetime.datetime.combine(today, startTime)
            else:
                endTime = datetime.datetime.combine(tomorrow, endTime)
                if startTime > datetime.time(12, 0, 0):
                    startTime = datetime.datetime.combine(today, startTime)
                else:
                    startTime = datetime.datetime.combine(tomorrow, startTime)
            # finally compare the times
            if currentDatetime >= startTime and currentDatetime < endTime:
                # we should be sleeping!
                return True
        # no bed time entry for the current time
        return False

    def getDayTime(self):
        pass

    def task(self):
        """ Detects the current daytime

        This skill detects whether it is day time, sunset, oder night time 
        based on the weather information from the WeatherSkill. The bed time 
        is detected based on the settings for each day. 
        The DaytimeState data object with the key STATE_PREFIX will be updated.
        """
        daytimeState = self.readState(self.STATE_PREFIX)
        if daytimeState is None:
            daytimeState = DaytimeState()
        bedTime = self.checkBedTime()
        daytimeState.bedTime = bedTime
        dayTime = self.getDayTime()
        daytimeState.setDayTime(dayTime)

        if bedTime:
            self.log("It is " + dayTime + " and you should be sleeping!")
        else:
            self.log("It is " + dayTime + " and you should not be sleeping!")
