"""
    File:
        Debug.py
    Brief:
        For new code trail and executed
    Author:
        Neo
    History:
        2020/12/10 - Initialization version

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


def Tftpy64():

    TFTPtransfer = Tester()

    # Start up TFTP Server
    filePath = ROOT_PATH
    TFTPtransfer.logger.debug("Deploy file folder path : %s \n" % filePath)

    programPath = ROOT_PATH + os.sep + "tftpd64.exe"
    TFTPtransfer.logger.debug("Tftp64 program open path : %s \n" % programPath)

    TFTP64 = subprocess.Popen(programPath)
    sleep(5)
    TFTP64.terminate()

def ImageupgradeTrail():

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
        NORimage      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['NOR_IMAGE']
        BOOTfile      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['BOOT_FILE']
        ROOTfile      = Upgrade.config.CONFIG_SET['MAIN_BOARD']['ROOT_FILE']
        FirmwareImage = Upgrade.config.CONFIG_SET['MAIN_BOARD']['FIRMWARE_IMAGE']
        dlpEth        = Upgrade.config.CONFIG_SET['MAIN_BOARD']['DLP_ETH']

        # Check File
        FileSearch.SearchFile(Upgrade)

        # Start up TFTP Server ------------------
        programPath = ROOT_PATH + os.sep + "TFTP" + os.sep + "tftpd64.exe"
        Upgrade.logger.info("Tftp64 program open path : %s \n" % programPath)

        TFTP64 = Tftp64.Tftpd64_Open() # Start up Tftpd64.exe

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

        try:
            while True:

                while ser.inWaiting():

                    response = ser.readline().decode('utf-8', 'ignore')
                    Upgrade.logger.info(response)

                    # Login Normal Linux ----
                    if ("localhost login:") in response != -1:
                        Upgrade.logger.info(ser.send_and_read("root\n", "Password:")) # User Name
                        Upgrade.logger.info(ser.send_and_read("root\n", "root@localhost:~#")) # Password
                    # Login Tiny Linux ----
                    if ("TinyLinux login:") in response != -1:
                        Upgrade.logger.info(ser.send_and_read("root\n", "root@localhost:~#")) # User Name
                        Upgrade.logger.info(ser.send_and_read("reboot\n", "Hit any key to stop autoboot:")) # User Name

                    # Re-Start ----
                    if ("root@TinyLinux:~#") in response != -1:
                        Upgrade.logger.info(ser.send_and_read("reboot\n", "Hit any key to stop autoboot:"))
                    if ("root@localhost:~#") in response != -1:
                        Upgrade.logger.info(ser.send_and_read("reboot\n", "Hit any key to stop autoboot:")) # Reboot

                    # Used for debug ------------------------------------------
                    # Re-start from U-Boot mode ----
                    # if ("=>") in response != -1:
                    #     Upgrade.logger.info(ser.send_and_read("boot\n", "localhost login:"))
                    #
                    # if ("Hit any key to stop autoboot:") in response != -1:
                    #     Upgrade.logger.info(ser.send_and_read("\n", "=>"))
                    #     Upgrade.logger.info(ser.send_and_read("boot", "localhost login:"))
                    # --------------------------------------------------------

                    # Enter into U-Boot mode and setup TFTP connection ----
                    if ("Hit any key to stop autoboot:") in response != -1:
                        Upgrade.logger.info(ser.send_and_read("\n", "=>"))
                        Upgrade.logger.info(ser.send_and_read((("setenv ipaddr %s\n") % DUTip), "=>"))
                        Upgrade.logger.info(ser.send_and_read((("setenv serverip %s\n") % TFTPip), "=>"))
                        Upgrade.logger.info(ser.send_and_read("setenv ethact DPMAC5@xgmii\n", "=>"))
                        Upgrade.logger.info(ser.send_and_read((("tftp 0x80001000 %s\n") % dlpEth), "=>"))
                        Upgrade.logger.info(ser.send_and_read("fsl_mc lazyapply dpl 0x80001000\n", "=>"))
                        sleep(1)

                        # Check Connection ------------------------------------------------------
                        Upgrade.logger.info(ser.send_and_read((("ping %s\n") % TFTPip), "is alive"))
                        sleep(1)

                        if ser.wait_for("is alive") != -1:
                            Upgrade.logger.info(ser.send_and_read("\n", "=>"))
                            Upgrade.logger.info("------ Connect with TFTP Server Success ------ \n")

                        else:
                            Upgrade.logger.info("******** Image Upgrade Failed ********\n")
                            Upgrade.logger.info("******** Please check Server connection ******** \n")

                            return response
                        # ------------------------------------------------------------------------

                        # Login Tiny Linux -----
                        Upgrade.logger.info(ser.send_and_read("run xspi_bootcmd\n", "TinyLinux login:"))
                        Upgrade.logger.info(ser.send_and_read("root\n", "root@TinyLinux:~#"))
                        sleep(1)

                        # Create Ethernet interface in Tiny Linux ---
                        Upgrade.logger.info(ser.send_and_read("ls-addni dpmac.5\n", "root@TinyLinux:~#"))
                        Upgrade.logger.info(ser.send_and_read("ifconfig eth2 up\n", "root@TinyLinux:~#"))
                        Upgrade.logger.info(ser.send_and_read((("ifconfig eth2 %s\n") % DUTip), "root@TinyLinux:~#"))
                        sleep(1)

                        # Load image via tftp and use flex-installer script to deploy image ----
                        Upgrade.logger.info(ser.send_and_read((("tftp -gr %s %s\n") % (BOOTfile, TFTPip)),
                                                              "root@TinyLinux:~#"))
                        sleep(1)
                        Upgrade.logger.info(ser.send_and_read((("tftp -gr %s %s\n") % (ROOTfile, TFTPip)),
                                                              "root@TinyLinux:~#"))
                        sleep(1)
                        Upgrade.logger.info(ser.send_and_read((("tftp -gr %s %s\n") % (FirmwareImage, TFTPip)),
                                                              "root@TinyLinux:~#"))
                        sleep(1)
                        Upgrade.logger.info(ser.send_and_read((("tftp -gr flex-installer %s\n") % TFTPip),
                                                              "root@TinyLinux:~#"))
                        sleep(1)
                        Upgrade.logger.info(ser.send_and_read(("chmod +x flex-installer\n"), "root@TinyLinux:~#"))

                        # Deploy Image -----
                        Upgrade.logger.info(ser.send_and_read(("./flex-installer -b %s -r %s -f %s -d /dev/mmcblk1\n") %
                                                              (BOOTfile, ROOTfile, FirmwareImage),"Installation completed successfully"))
                        if ser.wait_for("Installation completed successfully") != -1:
                            Upgrade.logger.info("----- Installation completed -----\n")
                            sleep(1)
                        else:
                            Upgrade.logger.info("----- Installation Image Failed -----\n")
                            Upgrade.logger.info("Please try again for Image upgrade process \n")
                            Upgrade.logger.info("or \n")
                            Upgrade.logger.info("Check up issue \n")

                            return response

                        # Finished upgrade process ----
                        Upgrade.logger.info(ser.send_and_read("reboot\n", "localhost login:"))
                        if ser.wait_for("localhost login:") != -1:
                            Upgrade.logger.info("\n")
                            Upgrade.logger.info("----- Closed DUT board serial port -----\n")
                            Upgrade.logger.info("------- Finished Image Upgrade -------\n")
                            Upgrade.logger.info("Done !!\n")

                            return response

                        else:
                            Upgrade.logger.info("\n")
                            Upgrade.logger.info("######## Image Upgrade Failed ########\n")
                            Upgrade.logger.info("Please try again for Image upgrade process \n")
                            Upgrade.logger.info("or \n")
                            Upgrade.logger.info("Check up issue \n")

                            return response

                    # if Upgrade.logger.info(("mmc1: Tuning timeout, falling back to fixed sampling clock")) in response != -1:
                    #     Upgrade.logger.info("\n")
                    #     Upgrade.logger.info("######## Image Upgrade Failed ########\n")
                    #     Upgrade.logger.info("######## MMC1 Failed ########\n")
                    #
                    #     return response

                    ser.write('\n'.encode('utf-8', 'ignore'))

        except KeyboardInterrupt:
            ser.close()
            Upgrade.logger.info('Image Upgrade Process End ******\n')
            TFTP64.terminate()  # Close Tftpd64.exe

#############################################################################################################

# Only for debugging
def Debugging():
    """

    :return:
    """
    pass

# Main Test Function
if __name__ == "__main__":
    sys.exit(ImageupgradeTrail())
    #sys.exit(Debugging())