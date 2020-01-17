#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Data Management

This file contains support functions for data management
"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import pandas as pd
import logging


class DataManagement:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.data = None

    def loadData(self, file=None):
        if file:
            try:
                self.logger.debug('reading data into pandas dataframe: {}'.format(file))
                self.data = pd.read_csv(file)
            except Exception as e:
                self.logger.debug('error while loading file ({}): {}'.format(file, e))
                return 'error: could not load file ({})'.format(file)
            return 0

    def saveData(self, file=None):
        if file:
            try:
                self.logger.debug('saving pandas dataframe to {}.csv'.format(file))
                self.data.to_csv(file)
            except Exception as e:
                self.logger.debug('saving pandas dataframe to {}.csv failed'.format(file))
                return 'error: could not save file: {}.csv'.format(file)
            return 0
