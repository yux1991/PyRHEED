import configparser

class Configuration():
    def saveDefaults(self):
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
                                    'tiltAngleSliderScale': 10\
                                    }

        config['canvasDefault'] = {\
                                    'widthInAngstrom' : 0.4,\
                                    'radiusMaximum' : 20,\
                                    'span' : 60,\
                                    'tilt' : 0,\
                                    'max_zoom_factor' : 21\
                                    }

        #0: ChartThemeLight
        #1: ChartThemeBlueCerulean
        #2: ChartThemeDark
        #3: ChartThemeBrownSand
        #4: ChartThemeBlueNcs
        #5: ChartThemeHighContrast
        #6: ChartThemeBlueIcey
        #7: ChartThemeQt
        config['chartDefault'] = {\
                            'theme':'1'\
                                }

        with open('./configuration.ini','w') as configfile:
            config.write(configfile)
