"""
    File:
        Build.py
    Brief:
        Responsible for software package distribution
    Author:
        Neo
    History
        2020/12/04 - Initialization version
        2020/12/09 - Support to build TFTP sever program
"""
import os
import sys
import stat
import shutil

sys.path.append('configuration/')

from cx_Freeze import setup, Executable
from ImageUpgrade import Tester as ImageUpgrade


# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
SRC_PATH     = CURRENT_PATH + "\\release"
DEST_PATH    = CURRENT_PATH + "\\build\\exe.win32-3.7"


# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------
MAKE_ARCH_DICT = {
    'configuration' : {
        'SRC_PATH'  : '%s\\configuration' % CURRENT_PATH,
        'DEST_PATH' : '%s\\configuration' % DEST_PATH,
        'FILES'     : ['CONFIG_SET.xml']
    },
    'Image' : {
        'SRC_PATH'  : '%s\\Image' % CURRENT_PATH,
        'DEST_PATH' : '%s\\Image' % DEST_PATH,
        'FILES'     : ['firmware_lx2160ardb_rev2_uboot_xspiboot.img',
                       'bootpartition_LS_arm64_lts_4.19_202012021002.tgz',
                       'rootfs_lsdk2004_ubuntu_main_arm64_202012021106.tgz',
                       'firmware_lx2160ardb_rev2_uboot_emmcboot.img',
                       'dpl-eth.19.dtb',
                       'flex-installer']
    },
    'TFTP' : {
        'SRC_PATH'  : '%s\\TFTP' % CURRENT_PATH,
        'DEST_PATH' : '%s\\TFTP' % DEST_PATH,
        'FILES'     : ['tftpd32.chm',
                       'tftpd32.ini',
                       'tftpd64.exe']
    },

    'result' : {
        'SRC_PATH'  : '%s\\result' % CURRENT_PATH,
        'DEST_PATH' : '%s\\result' % DEST_PATH,
        'FILES'     : ''
    },
}

RESERVED_ITEM = [
    'configuration',
    'library',
    'utilities',
    'library.zip',      # Startup module created by cx_Freeze
]


RELEASE_TYPE = "FM"

# Create tester instance
ImageUpgrade = ImageUpgrade()

FM_VERSION = "V%s.%s.S%s" % (ImageUpgrade.config.CONFIG_SET['VERSION']['PROG_VERSIN'],
                             ImageUpgrade.config.CONFIG_SET['VERSION']['PROG_SUB_VERSIN'],
                             ImageUpgrade.config.CONFIG_SET['VERSION']['SVN_REVERSIN'])

TFTP_VERSION = "V%s.%s" % (ImageUpgrade.config.CONFIG_SET['TFTP_VERSION']['PROG_VERSIN'],
                           ImageUpgrade.config.CONFIG_SET['TFTP_VERSION']['PROG_SUB_VERSIN'])

# -----------------------------------------------------------------------------
#    Internal Function declaration
# -----------------------------------------------------------------------------
def CreateFolder(directory):
    """

    :param directory:
    :return:
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, mode=0o777)
    except OSError:
        print("Error: Creating directory %s " % directory)


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
def Build(type, version):
    """

    :return:
    """
    if type == "FM":
        setup(name        = "ImageUpgrade",
              version     = version,
              description = "Responsible for executing image upgrade automated system",
              #options     = {'build_exe': {'init_script':'Console'}},
              executables = [Executable(".\\ImageUpgrade.py",
                                        icon=".\\document\\testing_icon-48.ico")])

    elif type == "TFTP":
        setup(name        = "TFTPServer",
              version     = version,
              description = "Responsible for executing TFTP server build system",
              #options     = {'build_exe': {'init_script':'Console'}},
              executables = [Executable(".\\TFTPServer.py",
                                        icon=".\\document\\testing_icon-48.ico")])

    else:
        pass


def Make(type, version):
    """

    :return:
    """
    for folder in MAKE_ARCH_DICT:

        CreateFolder(MAKE_ARCH_DICT[folder]['DEST_PATH'])

        for file in MAKE_ARCH_DICT[folder]['FILES']:
            shutil.copyfile(MAKE_ARCH_DICT[folder]['SRC_PATH'] + "\\" + file,
                            MAKE_ARCH_DICT[folder]['DEST_PATH'] + "\\" + file)

    # Rename output folder
    if type == "FM":
        os.renames('.\\build\\exe.win32-3.7', ".\\release\\ImageUpgrade_%s" % version)
        shutil.copyfile(".\\document\\IM_README", ".\\release\\ImageUpgrade_%s\\IM_README" % version)
        shutil.copyfile(".\\document\\Image_Upgrade_Automation_SOP.pptx",".\\release\\ImageUpgrade_%s\\AutomationTest_SW_SOP_Final.pptx" % version)

    elif type == "TFTP":
        os.renames('.\\build\\exe.win32-3.7', ".\\release\\TFTPServer_%s" % version)
        # shutil.copyfile(".\\document\\FM_README", ".\\release\\ImageUpgrade_5GNR_%s\\README" % version)
        # shutil.copyfile(".\\document\\Image_Upgrade_Automation_SOP.pptx",".\\release\\FMUpgrader_%s\\AutomationTest_SW SOP_Final.pptx" % version)

    else:
        pass


if __name__ == "__main__":
    if RELEASE_TYPE == "FM":
        Build("FM", FM_VERSION)
        Make("FM", FM_VERSION)

    elif RELEASE_TYPE == "TFTP":
        Build("TFTP", TFTP_VERSION)
        Make("TFTP", TFTP_VERSION)

