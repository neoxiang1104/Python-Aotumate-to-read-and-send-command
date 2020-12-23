"""
    File:
        TFTPServer.py
    Brief:
        Setup TFTP Server side for deploy file transfer
    Author:
        Neo
    History:
        2020/12/08 - Initialization version

"""
import time
import sys
import os
import tftpy
import time
import minimumTFTP

sys.path.append('platforms/')
sys.path.append('utilities/')
sys.path.append('configuration/')

from datetime import datetime
from configuration import Config
from utilities import LoggerEx
from time import sleep


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
class TFTP_Server:
    """

        :return:
        """

    def __init__(self):
        """
        """
        self.testStartTime = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H-%M')
        self.testEndingTime = ""

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
        self.config = Config.XmlLib(self.logger, ROOT_PATH + os.sep + "configuration")

def TFTPServerSide():

    TFTPServer = TFTP_Server()

    # Obtain parameter variable
    TFTPip = TFTPServer.config.CONFIG_SET['MAIN_BOARD']['TFTP_SERVER_IP']

    # Start up TFTP Server
    filePath = ROOT_PATH + os.sep + "Image"
    TFTPServer.logger.info("Deploy file folder path : %s\n" % filePath)
    TFTPServer.logger.info("TFTP Server IP Address : %s " % TFTPip)

    server = tftpy.TftpServer(filePath)
    server.listen((('%s') % TFTPip), 69) # listen

    sleep(5)
    server.stop(True) # Close TFTP


def minimumTFTPServer():

    TFTPServer = TFTP_Server()

    # Obtain parameter variable
    TFTPip = TFTPServer.config.CONFIG_SET['MAIN_BOARD']['TFTP_SERVER_IP']

    # Start up TFTP Server
    filePath = ROOT_PATH + os.sep + "Image"
    TFTPServer.logger.info("Deploy file folder path : %s\n" % filePath)
    TFTPServer.logger.info("TFTP Server IP Address : %s " % TFTPip)

    server = minimumTFTP.Server(filePath)
    server.run() # listen


# Only for debugging
def Debugging():
    """

    :return:
    """
    pass

# Main Test Function
if __name__ == "__main__":
    sys.exit(minimumTFTPServer())
    #sys.exit(Debugging())