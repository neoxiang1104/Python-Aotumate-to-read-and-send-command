"""
    File:
        SD_Emmc_upgrade.py
    Brief:
        Image upgrade for SD and EMMC
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


# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
def UpgradeSdEmmc(Upgrade, ser, DUTip, TFTPip, dlpEth, NORimage, BOOTfile, ROOTfile, emmcImage, sdImage):
    ser.write('\n'.encode('utf-8', 'ignore'))
    sleep(2)

    try:
        while True:

            while ser.inWaiting():

                response = ser.readline().decode('utf-8', 'ignore')
                Upgrade.logger.info(response)

                # Login Normal Linux ----
                if ("localhost login:") in response != -1:
                    ser.send_and_result(ser, "root\n", "Password:", "Password:")  # User Name
                    ser.send_and_result(ser, "root\n", "root@localhost:~#", "root@localhost:~#")  # Password
                # Login Tiny Linux ----
                if ("TinyLinux login:") in response != -1:
                    ser.send_and_result(ser, "root\n", "root@localhost:~#", "root@localhost:~#")  # User Name
                    ser.send_and_result(ser, "reboot\n", "Hit any key to stop autoboot:",
                                        "Hit any key to stop autoboot:")  # User Name

                # Re-Start ----
                if ("root@TinyLinux:~#") in response != -1:
                    ser.send_and_result(ser, "reboot\n", "Hit any key to stop autoboot:",
                                        "Hit any key to stop autoboot:") # tiny linux reboot
                if ("root@localhost:~#") in response != -1:
                    ser.send_and_result(ser, "reboot\n", "Hit any key to stop autoboot:",
                                        "Hit any key to stop autoboot:")  # root linux reboot

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
                    ser.send_and_result(ser, "\n", "=>", "=>")
                    ser.send_and_result(ser, (("setenv ipaddr %s\n") % DUTip), "=>", "=>")
                    ser.send_and_result(ser, (("setenv serverip %s\n") % TFTPip), "=>", "=>")
                    ser.send_and_result(ser, "setenv ethact DPMAC5@xgmii\n", "=>", "=>")

                    # TFTP server start up
                    Upgrade.logger.info("Startup TFTP Server ---\n")
                    proc = subprocess.run(['python', 'TFTPServer.py'],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=True)

                    # Deploy firmware to XSPI NOR Flash ".90" ----
                    ser.send_and_result(ser, (("tftp $load_addr %s\n") % NORimage), "=>", "=>")  # ".90"
                    ser.send_and_result(ser, "sf probe 0:0\n", "=>", "=>")
                    ser.send_and_result(ser, "sf erase 0 +$filesize && sf write $load_addr 0 $filesize\n", "=>", "=>")
                    ser.send_and_result(ser, "qixis_reset altbank\n", "=>", "=>")
                    ser.send_and_result(ser, "run xspi_bootcmd\n", "TinyLinux login:", "TinyLinux login:")
                    ser.send_and_result(ser, "root\n", "root@TinyLinux:~#", "root@TinyLinux:~#")

                    # Re-start system and setup connection again ---
                    ser.send_and_result(ser, "reboot\n", "Hit any key to stop autoboot:",
                                        "Hit any key to stop autoboot:")
                    ser.send_and_result(ser, "\n", "=>", "=>")
                    ser.send_and_result(ser, (("setenv ipaddr %s\n") % DUTip), "=>", "=>")
                    ser.send_and_result(ser, (("setenv serverip %s\n") % TFTPip), "=>", "=>")
                    ser.send_and_result(ser, "setenv ethact DPMAC5@xgmii\n", "=>", "=>")

                    # TFTP server start up
                    Upgrade.logger.info("Startup TFTP Server ---\n")
                    proc = subprocess.run(['python', 'TFTPServer.py'],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=True)

                    ser.send_and_result(ser, (("tftp 0x80001000 %s\n") % dlpEth), "=>", "=>")
                    ser.send_and_result(ser, "fsl_mc lazyapply dpl 0x80001000\n", "=>", "=>")

                    # Check Connection ------------------------------------------------------
                    if ser.send_and_result(ser, (("ping %s\n") % TFTPip), "=>", "is alive") != -1:
                        ser.send_and_result(ser, "\n", "=>", "=>")
                        Upgrade.logger.info("------ Connect with TFTP Server Success ------ \n")

                    else:
                        Upgrade.logger.info("******** Image Upgrade Failed ********\n")
                        Upgrade.logger.info("******** Please check Server connection ******** \n")

                        return response
                    # ------------------------------------------------------------------------

                    # Login Tiny Linux -----
                    ser.send_and_result(ser, "run xspi_bootcmd\n", "TinyLinux login:", "TinyLinux login:")
                    ser.send_and_result(ser, "root\n", "root@TinyLinux:~#", "root@TinyLinux:~#")

                    # Create Ethernet interface in Tiny Linux ---
                    ser.send_and_result(ser, "ls-addni dpmac.5\n", "root@TinyLinux:~#", "root@TinyLinux:~#")
                    ser.send_and_result(ser, "ifconfig eth2 up\n", "root@TinyLinux:~#", "root@TinyLinux:~#")
                    ser.send_and_result(ser, (("ifconfig eth2 %s\n") % DUTip), "root@TinyLinux:~#", "root@TinyLinux:~#")
                    sleep(1)

                    # Load EMMC image via tftp and use flex-installer script to deploy image ----
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (BOOTfile, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (ROOTfile, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (emmcImage, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr flex-installer %s\n") % TFTPip), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, ("chmod +x flex-installer\n"), "root@TinyLinux:~#", "root@TinyLinux:~#")

                    # Deploy EMMC Image -----
                    if ser.send_and_result(ser, ("./flex-installer -b %s -r %s -f %s -d /dev/mmcblk1\n") %
                                                (BOOTfile, ROOTfile, emmcImage), "root@TinyLinux:~#",
                                           "Installation completed successfully") != -1:
                        Upgrade.logger.info("----- Installation completed -----\n")
                        sleep(1)
                    else:
                        Upgrade.logger.info("----- Installation EMMC Image Failed -----\n")
                        Upgrade.logger.info("Please try again for EMMC Image upgrade process \n")
                        Upgrade.logger.info("or \n")
                        Upgrade.logger.info("Check up issue \n")

                        return response

                    # Load SD image via tftp and use flex-installer script to deploy image ----
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (BOOTfile, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (ROOTfile, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr %s %s\n") % (sdImage, TFTPip)), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, (("tftp -gr flex-installer %s\n") % TFTPip), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")
                    sleep(1)
                    ser.send_and_result(ser, ("chmod +x flex-installer\n"), "root@TinyLinux:~#",
                                        "root@TinyLinux:~#")

                    # Deploy SD Image -----
                    if ser.send_and_result(ser, ("./flex-installer -b %s -r %s -f %s -d /dev/mmcblk1\n") %
                                                (BOOTfile, ROOTfile, sdImage), "root@TinyLinux:~#",
                                           "Installation completed successfully") != -1:
                        Upgrade.logger.info("----- Installation completed -----\n")
                        sleep(1)
                    else:
                        Upgrade.logger.info("----- Installation Image Failed -----\n")
                        Upgrade.logger.info("Please try again for SD Image upgrade process \n")
                        Upgrade.logger.info("or \n")
                        Upgrade.logger.info("Check up issue \n")

                        return response

                    # Finished upgrade process ----
                    if ser.send_and_result(ser, "reboot\n", "localhost login:", "localhost login:") != -1:
                        Upgrade.logger.info("\n")
                        Upgrade.logger.info("----- Closed DUT board serial port -----\n")
                        Upgrade.logger.info("------- Finished EMMC and SD Image Upgrade -------\n")
                        Upgrade.logger.info("Done !!\n")

                        return response

                    else:
                        Upgrade.logger.info("\n")
                        Upgrade.logger.info("######## EMMC/SD Image Upgrade Failed ########\n")
                        Upgrade.logger.info("Please try again for EMMC/SD Image upgrade process \n")
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
