"""
Skill to detect active devices

DevicePresenceState is a state data object for the DetectDevicePresenceSkill.
DetectDevicePresenceSkill is a Skill to detect devices present in the network.

Copyright (c) 2021 Timo Haeckel
"""

from skills import SkillWithState
import platform
import subprocess
import datetime


class DevicePresenceState():
    """ State data object for the DetectDevicePresenceSkill.

    Attributes
    ----------
    address : str
        The device IPv4 address.
    currentlyPresent : Boolean
        The current detection state
    lastDetectedAt : datetime
        The time the device was last detected
    """
    def __init__(self, address, currentlyPresent=False):
        """ 
        lastDetectedAt will be automatically initialized with none if 
        currentlyPresent is false, else to the current datetime
        Parameters
        ----------
        address : str (mandatory)
            The device IPv4 address.
        currentlyPresent : Boolean (Default False)
            The current detection state
        """
        self.lastDetectedAt = None
        self.address = address
        self.setPresence(currentlyPresent)

    def setPresence(self, currentlyPresent):
        """ Set the current device state to the given value.

        lastDetectedAt will be automatically updated with the current datetime
        if currentlyPresent is set to true. 
        
        Parameters
        ----------
        currentlyPresent : Boolean
            The current detection state
        """
        self.currentlyPresent = currentlyPresent
        if currentlyPresent:
            self.lastDetectedAt = datetime.datetime.now()


class DetectDevicePresenceSkill(SkillWithState):
    """ Skill to detect devices present in the network.

    This skill sends ping probes to the device addresses to detect their 
    presence. Remember that a host may not respond to a ping (ICMP) request
    even if the host name is valid.
    The DevicePresenceState() with the key STATE_PREFIX+ADDRESS will be
    constantly updated.

    Settings
    --------
    {
        "statePrefix" : "DevicePresence:",
        "deviceAddresses" : [
            "localhost",
            "192.168.178.12"
        ]
    }

    Attributes
    ----------
    addresses : list(str)
        The device IPv4 addresses to be detected in the local network.
    STATE_PREFIX : str
        A prefix used to form the state key in the state data base with 
        STATE_PREFIX + Address  
    """
    STATE_PREFIX = "DevicePresence:"

    def __init__(self,
                 statedb,
                 interval=60,
                 errorSilent=False,
                 logSilent=False,
                 logFile=""):
        """ 
        Parameters
        ----------
        statedb : statedb.StateDataBase
            The shared state data base instance used for all skills in 
            the home automation setup
        interval : int (Default 60)   
            The detection interval to look for hosts in seconds
        errorSilent : Boolean (Default False)
            True if errors shall not be printed
        logSilent : Boolean (Default False)
            True if log messages shall not be printed
        logFile : str (Default "")
            Path to the log file to be used for errors and log messages
        """
        SkillWithState.__init__(self,
                                name="DetectDevicePresence",
                                statedb=statedb,
                                interval=interval,
                                errorSilent=errorSilent,
                                logSilent=logSilent,
                                logFile=logFile)
        self.addresses = self.findSkillSettingWithKey("deviceAddresses")
        prefix = self.findSkillSettingWithKey("statePrefix")
        if prefix is not None:
            self.STATE_PREFIX = prefix

    def task(self):
        """ Device presence detection task.

        This function will send ping probes to the device addresses to detect 
        their presence. Remember that a host may not respond to a ping (ICMP) 
        request even if the host name is valid.
        The DevicePresenceState data object with the key STATE_PREFIX+ADDRESS 
        will be updated.
        """
        for host in self.addresses:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', host, '-4']
            result = subprocess.call(command,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL) == 0
            deviceState = self.readState(self.STATE_PREFIX + host)
            if deviceState is None:
                deviceState = DevicePresenceState(host, result)
            else:
                deviceState.setPresence(result)
            self.updateState(self.STATE_PREFIX + host, deviceState)
            if result == True:
                self.log("Device " + host + " is reachable")
            else:
                self.log("Device " + host + " is unreachable")
