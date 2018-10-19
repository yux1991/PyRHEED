import configparser

class Configuration():
    def __init__(self):
        self.saveDefaults()

    def saveDefaults():
        config = configparser.ConfigParser()
        config['windowDefault'] = {\
                                    'HS' : 0,\
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
                                    'tiltAngleSliderScale' : 10\
                                    }

        config['propertiesDefault'] = {\
                                    'sensitivity': 361.13,\
                                    'electronEnergy': 20,\
                                    'azimuth': 0,\
                                    'scaleBarLength': 5,\
                                    'brightness': 30,\
                                    'brightnessMinimum': 0,\
                                    'brightnessMaximum': 100,\
                                    'blackLevel': 50,\
                                    'blackLevelMinimum': 0,\
                                    'blackLevelMaximum': 500,\
                                    'integralHalfWidth': 0.4,\
                                    'widthMinimum': 0,\
                                    'widthMaximum': 1,\
                                    'widthSliderScale': 100,\
                                    'chiRange': 0,\
                                    'chiRangeMinimum': 0,\
                                    'chiRangeMaximum': 60,\
                                    'radius': 20,\
                                    'radiusMinimum': 0,\
                                    'radiusMaximum': 100,\
                                    'radiusSliderScale': 10,\
                                    'tiltAngle': 0,\
                                    'tiltAngleMinimum': 0,\
                                    'tiltAngleMaximum': 15,\
                                    'tiltAngleSliderScale': 10\
                                    }

        config['canvasDefault'] = {\
                                    'widthInAngstrom' : 0.4,\
                                    'radiusMaximum' : 20,\
                                    'span' : 60,\
                                    'tilt' : 0,\
                                    'max_zoom_factor' : 21\
                                    }

        with open('./configuration.ini','w') as configfile:
            config.write(configfile)
