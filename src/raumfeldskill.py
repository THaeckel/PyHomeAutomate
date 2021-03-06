"""
Skills to control teufel raumfeld streaming devices

RaumfeldTVWakeup is a Skill that wakes up a speaker when the TV is turned on.

Copyright (c) 2021 Timo Haeckel
"""

from skills import SkillWithState
import raumfeld

RAUMFELD_URI_PLACEHOLDER = "dlna-playcontainer://uuid%3Abd4f7f00-aa40-4e4a-a54e-ec64e9944e23?sid=urn%3Aupnp-org%3AserviceId%3AContentDirectory&amp;cid=0%2FTidal%2FDirectAccess%2FArtist%2F8372%2FTopTracks&amp;fid=0&amp;fii=0"


class RaumfeldTVWakeup(SkillWithState):
    """ Skill to wakeup a raumfeld speaker connected to a smart tv.

    This skill wakes up the raumfeld speaker connected to the smart tv when it
    is turned on.

    Settings
    --------
    {
        "statePrefix" : "DevicePresence:",
        "tvAddress" : "192.168.178.42",
        "tvSpeakerRoomName" : "TV Speaker"
    }

    Attributes
    ----------
    tvAddress : str
        The TVs IPv4 address to be detected in the local network.
    STATE_PREFIX : str
        The prefix from the DeviceDetectionSkill used to form the state key in 
        the state data base for the tv host with STATE_PREFIX + Address  
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
                                name="RaumfeldTVWakeup",
                                statedb=statedb,
                                settingsFile=settingsFile)
        raumfeld.init()
        self.alreadyAwake = False
        self.speaker = self.findSkillSettingWithKey("tvSpeakerRoomName")
        self.tvAddress = self.findSkillSettingWithKey("tvAddress")
        self.STATE_PREFIX = self.findSkillSettingWithKey("statePrefix")

    def wakeup(self, speaker):
        rooms = raumfeld.getRoomsByName(speaker)
        rooms[0].play(RAUMFELD_URI_PLACEHOLDER)
        rooms[0].pause()

    def task(self):
        """ Wakeup TV speakers task

        This function will wakeup the TV speakers if the TV device is turned on
        """
        tvState = self.readState(self.STATE_PREFIX + self.tvAddress)
        if tvState is not None:
            if tvState.currentlyPresent:
                #tv is turned on!
                if not self.alreadyAwake:
                    self.wakeup(self.speaker)
                    self.alreadyAwake = True
                    self.log("TV Speaker woken up")
            elif self.alreadyAwake:
                #tv turned off!
                self.alreadyAwake = False
                self.log("TV turned off sleep allowed")
