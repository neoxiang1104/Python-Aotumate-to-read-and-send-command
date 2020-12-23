"""
    File:
        ImageUpgrade_Dev.py
    Brief:
        Deployment for image upgrade and design code flow structure
    Author:
        Neo
    History:
        2020/12/11 - Initialization version

"""
import time
import sys
import os
import datetime
import subprocess

sys.path.append('platforms/')
sys.path.append('utilities/')
sys.path.append('Image/')
sys.path.append('configuration/')

from datetime import datetime
from configuration import Config
from utilities import LoggerEx
from utilities import FileSearch
from TFTP import Tftp64
from utilities.SerialExtra import SerialExtra
from time import sleep

from platforms import Emmc_Upgrade
from platforms import SD_Emmc_Both
from platforms import SD_Upgrade


# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------
timeStamp     = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')
ROOT_PATH     = os.path.abspath('.')
LOG_FILE_NAME = ROOT_PATH + os.sep + "result" + os.sep + "ImageUpgrade_LogFile_%s.log" % (timeStamp)

# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
class Tester:
    """

    :return:
    """

    def __init__(self):
        """
        """
        self.testStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')
        self.testEndingTime = ""

        # Create tester instance
        parameters = Config.XmlLib.ParseXml(ROOT_PATH + os.sep +
                                            "configuration" + os.sep +
                                            "{}.xml".format("CONFIG_SET"),
                                            "MAIN_BOARD")

        # Config logger level for system module
        loggerInfo = Config.XmlLib.ParseXml(ROOT_PATH + os.sep + "configuration" +
                                            os.sep + "{}.xml".format("CONFIG_SET"),
                                            "LOGGER_INFO")

        self.logger = LoggerEx.ConfigLoggerEx('CTRL',
                                         loggerInfo['MOD_LOG_LEVEL']['CTRL'],
                                         LOG_FILE_NAME,
                                         loggerInfo['FORMAT']['FILE'],
                                         loggerInfo['FORMAT']['CONSOLE'])

        # Import configuration from XML file
        self.logger.info("\nImport configuration from XML file:")
        self.config = Config.XmlLib(self.logger, ROOT_PATH + os.sep + "configuration")
        self.logger.info("")


def Main():

    # Create tester instance
    Upgrade = Tester()

    # Obtain parameter variable
    MainBoardTest = Upgrade.config.CONFIG_SET['MAIN_BOARD']['TEST']

    # Main Board Fiber Port Test --
    if MainBoardTest is True:

        # Obtain parameter variable
        comportNum    = Upgrade.config.CONFIG_SET['MAIN_BOARD']['SerialNumber']
        comportBaud   = Upgrade.config.CONFIG_SET['MAIN_BOARD']['SerialBaud']
        DUTip         = Upgrade.config.CONFIG_SET['MAIN_BOARD']['DUT_IP']
        TFTPip        = Upgrade.config.CONFIG_SET['MAIN_BOARD']['TFTP_SERVER_IP']
        dlpEth        = Upgrade.config.CONFIG_SET['MAIN_BOARD']['DLP_ETH']
        NORimage      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['NOR_IMAGE']
        BOOTfile      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['BOOT_FILE']
        ROOTfile      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['ROOT_FILE']
        emmcImage     = Upgrade.config.CONFIG_SET['MAIN_BOARD']['EMMC_IMAGE']
        sdImage       = Upgrade.config.CONFIG_SET['MAIN_BOARD']['SD_IMAGE']
        # Select for deploy method
        emmcUpgrade   = Upgrade.config.CONFIG_SET['MAIN_BOARD']['EMMC_UPGRADE']
        sdUpgrade     = Upgrade.config.CONFIG_SET['MAIN_BOARD']['SD_UPGRADE']
        bothUpgrade   = Upgrade.config.CONFIG_SET['MAIN_BOARD']['BOTH']

        # Check File
        FileSearch.SearchFile(Upgrade, NORimage, BOOTfile, ROOTfile, emmcImage, dlpEth)

        # Start Image Upgrade ------------------
        # Process Start
        Upgrade.logger.info("\n")
        Upgrade.logger.info("============================================================================")
        Upgrade.logger.info("=== Start Image Upgrade ===")
        Upgrade.logger.info("============================================================================")

        Upgrade.logger.info("Comport Number : %s \n" % comportNum)
        Upgrade.logger.info("Serial Baud : %d \n" % comportBaud)

        # Serial Port Connect
        # ser = serial.serial(comportNum, baudrate=comportBaud, bytesize=8, parity='N', stopbits=1)
        ser = SerialExtra(comportNum, comportBaud, bytesize=8, parity='N', stopbits=1)
        ser.flushInput()
        ser.flushOutput()
        Upgrade.logger.info("----- Opened DUT board serial port -----")

#############################################################################################################

        ser.write('\n'.encode('utf-8', 'ignore'))
        sleep(2)

        # EMMC upgrade Function
        if emmcUpgrade is True:
            Upgrade.logger.info("**************************************************************************")
            Upgrade.logger.info("** Image upgrade for EMMC only **")
            Upgrade.logger.info("**************************************************************************")

            Emmc_Upgrade.UpgradeEmmc(Upgrade, ser, DUTip,
                                     TFTPip, dlpEth, NORimage,
                                     BOOTfile, ROOTfile, emmcImage)

        # SD upgrade Function
        if sdUpgrade is True:
            Upgrade.logger.info("**************************************************************************")
            Upgrade.logger.info("** Image upgrade for SD only **")
            Upgrade.logger.info("**************************************************************************")

            SD_Upgrade.UpgradeSD(Upgrade, ser, DUTip,
                                 TFTPip, dlpEth, NORimage,
                                 BOOTfile, ROOTfile, sdImage)

        # SD and EMMC upgrade Function
        if bothUpgrade is True:
            Upgrade.logger.info("**************************************************************************")
            Upgrade.logger.info("** Image upgrade for SD and EMMC **")
            Upgrade.logger.info("**************************************************************************")

            SD_Emmc_Both.UpgradeSdEmmc(Upgrade, ser, DUTip,
                                       TFTPip, dlpEth, NORimage,
                                       BOOTfile, ROOTfile, emmcImage, sdImage)


#############################################################################################################

# Only for debugging
def Debugging():
    """

    :return:
    """
    pass

# Main Test Function
if __name__ == "__main__":
    sys.exit(Main())
    #sys.exit(Debugging())