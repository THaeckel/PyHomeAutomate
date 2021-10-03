from skills import SkillWithState
import colorsys
import datetime
from phue import Bridge

MSH_SUNSET_PHASE_SECONDS = 60 * 45 # 45min
MSH_SKY_IS_CLOUDY = 90 # %
MSH_SKY_IS_CLEAR = 80 # %


class HueDaytimeAndWeatherSkill(SkillWithState):
    def __init__(self, statedb, settingsFile=""):
        SkillWithState.__init__(name="HueDaytimeAndWeather",
                                statedb=statedb,
                                settingsFile=settingsFile)

        self.sceneNightMode = self.findSkillSettingWithKeyOrDefault(
            "sceneNightMode", "Gedimmt")
        self.sceneDayMode = self.findSkillSettingWithKeyOrDefault(
            "sceneDayMode", "Hell")

    def convert_rgb_to_hue(rgbcolor):
        hsvcolor = colorsys.rgb_to_hsv(rgbcolor[0],rgbcolor[1],rgbcolor[2])
        huecolor = (int(hsvcolor[0] * 65535), int(hsvcolor[1] * 255), int(hsvcolor[2]))
        return huecolor

    def task(self):
        