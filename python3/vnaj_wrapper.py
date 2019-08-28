#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Wrapper for vnaJ-hl

This class runs the vnaJ-hl.jar java program and saves the results of the measurement in csv format for further
processing. For this to work vnaJ requires the proper setup scripts set up in advance and placed in the vnaJ
working directory

"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import logging
import subprocess

logger = logging.getLogger(__name__)


class vnajWrapper():

    java_loc = None
    vnaj_loc = None
    home_loc = None
    export_loc = None
    PORT = None
    data = None
    calibration = None
    driverid = 20

    def __init__(self, java_loc='/home/battosai/vnaJ/oracle_java/jre1.8.0_221/bin/java',
                 vnaJ_loc='../vnaJ/vnaJ-hl.3.2.10.jar',
                 home='../vnaJ',
                 export_loc='../vnaJ/export',
                 PORT=None,
                 data='scan_data',
                 cal_file='../vnaJ/TRAN_miniVNA.cal'):

        self.java_loc = java_loc
        self.vnaj_loc = vnaJ_loc
        self.home_loc = home
        self.export_loc = export_loc
        self.PORT = PORT
        self.data = data
        self.calibration = cal_file


    def run_vnaJ(self, lang='en', region='US', fstart=None, fstop=None, fsteps=822, average=1,
                 scanmode='TRAN', exports='csv'):

        # run vnaJ-hl using the setup previously done
        try:
            logging.info('running measurements ...')
            tmp = subprocess.check_output([self.java_loc,
                                           '-Dfstart={}'.format(fstart),
                                           '-Dfstop={}'.format(fstop),
                                           '-Dfsteps={}'.format(fsteps),
                                           '-Dcalfile={}'.format(self.calibration),
                                           '-DdriverPort={}'.format(self.PORT),
                                           '-Daverage={}'.format(average),
                                           '-DexportDirectory={}'.format(self.export_loc),
                                           '-DexportFilename={}'.format(self.data),
                                           '-Dscanmode={}'.format(scanmode),
                                           '-Dexports={}'.format(exports),
                                           '-DdriverId={}'.format(self.driverid),
                                           '-Duser.home={}'.format(self.home_loc),
                                           '-Duser.language={}'.format(lang),
                                           '-Duser.region={}'.format(region),
                                           '-jar', self.vnaj_loc])
            logging.info('measurements successful')
            logging.debug(tmp)
        except subprocess.CalledProcessError as e:
            logging.debug('Could not run vnaj-hl! error: {}'.format(e))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    zoom = [25994500, 26004290]
    full = [25990000, 26049719]
    fstart = zoom[0]
    fstop = zoom[1]
    PORT = 'ttyUSB0'
    average = 5

    minivna = vnajWrapper(PORT=PORT)
    minivna.run_vnaJ(fstart=fstart, fstop=fstop, average=average)

    # /home/battosai/vnaJ/oracle_java/jre1.8.0_221/bin/java -Dfstart=100000000 -Dfstop=500000000 -Dfsteps=822 -Dcalfile=../vnaJ/calibration/TRAN_miniVNA.cal -DdriverPort=ttyUSB0 -Daverage=1 -DexportDirectory=../vnaJ/export -DexportFilename=scan_data.csv -Dscanmode=TRAN -Dexports=csv -DdriverId=20 -Duser.home=../vnaJ -jar ../vnaJ/vnaJ-hl.3.2.10.jar

