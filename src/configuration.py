import configparser
import os

class Configuration():
    DefaultDic = {'windowDefault':{'HS' : 0,\
                                    'VS' : 0,\
                                    'energy' : 20,\
                                    'azimuth' : 0,\
                                    'scaleBarLength' : 5,\
                                    'chiRange' : 60,\
                                    'width' : 0.4,\
                                    'widthSliderScale' : 100,\
                                    'radius' : 5,\
                                    'radiusMaximum' : 20,\
                                    'radiusSliderScale' : 10,\
                                    'tiltAngle' : 0,\
                                    'tiltAngleSliderScale' : 10},\
            'propertiesDefault':{'sensitivity': 361.13,\
                                    'electronEnergy': 20,\
                                    'azimuth': 0,\
                                    'scaleBarLength': 5,\
                                    'brightness': 20,\
                                    'brightnessMinimum': 0,\
                                    'brightnessMaximum': 100,\
                                    'blackLevel': 50,\
                                    'blackLevelMinimum': 0,\
                                    'blackLevelMaximum': 500,\
                                    'integralHalfWidth': 0.4,\
                                    'widthMinimum': 0,\
                                    'widthMaximum': 1,\
                                    'widthSliderScale': 100,\
                                    'chiRange': 60,\
                                    'chiRangeMinimum': 0,\
                                    'chiRangeMaximum': 180,\
                                    'radius': 5,\
                                    'radiusMinimum': 0,\
                                    'radiusMaximum': 20,\
                                    'radiusSliderScale': 10,\
                                    'tiltAngle': 0,\
                                    'tiltAngleMinimum': -15,\
                                    'tiltAngleMaximum': 15,\
                                    'tiltAngleSliderScale': 10},\
            'canvasDefault':{'widthInAngstrom' : 0.4,\
                                    'radiusMaximum' : 20,\
                                    'span' : 60,\
                                    'tilt' : 0,\
                                    'max_zoom_factor' : 21},\
            'chartDefault':{'theme':1}}

    def save_defaults(self,Dic = DefaultDic):
        config = configparser.ConfigParser()
        config.read_dict(Dic)
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname,'configuration.ini'),'w') as configfile:
            config.write(configfile)
