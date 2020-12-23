"""
    File:
        FileSearch.py
    Brief:
        Check up deploy
    Author:
        Neo
    History:
        2020/12/08 - Initialization version

"""
import os

# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------
ROOT_PATH     = os.path.abspath('.')

# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------

def SearchFile(Upgrade, NORimage, BOOTfile, ROOTfile, EMMCImage, dlpEth):
    # File Search
    # Import deployed files

    mypath = ROOT_PATH + os.sep + "Image"

    Upgrade.logger.info("File Path : %s\n" % mypath)
    Upgrade.logger.info("\nImport deployed files:")
    NORimageCheck = mypath + os.sep + NORimage
    BOOTfileCheck  = mypath + os.sep + BOOTfile
    ROOTfileCheck = mypath + os.sep + ROOTfile
    EMMCImageCheck = mypath + os.sep + EMMCImage
    dlpEthCheck    = mypath + os.sep + dlpEth

    Upgrade.logger.info("Check NOR image file '%s' : %s" % (NORimageCheck, os.path.isfile(NORimageCheck)))
    if os.path.isfile(NORimageCheck) == -1:
        Upgrade.logger.info("NOR image File '%s' does not exit in the 'Image' folder\n" % NORimage)
    Upgrade.logger.info("Check Boot partition file '%s' : %s"% (BOOTfileCheck, os.path.isfile(BOOTfileCheck)))
    if os.path.isfile(BOOTfileCheck) == -1:
        Upgrade.logger.info("Boot File '%s' does not exit in the 'Image' folder\n" % BOOTfile)
    Upgrade.logger.info("Check Root file system '%s' : %s"% (ROOTfileCheck, os.path.isfile(ROOTfileCheck)))
    if os.path.isfile(ROOTfileCheck) == -1:
        Upgrade.logger.info("Root File '%s' does not exit in the 'Image' folder\n" % ROOTfile)
    Upgrade.logger.info("Check EMMC image file '%s' : %s"% (EMMCImageCheck, os.path.isfile(EMMCImageCheck)))
    if os.path.isfile(EMMCImageCheck) == -1:
        Upgrade.logger.info("EMMC image File '%s' does not exit in the 'Image' folder\n" % EMMCImage)
    Upgrade.logger.info("Check DLP_ETH file '%s' : %s"% (dlpEthCheck, os.path.isfile(dlpEthCheck)))
    if os.path.isfile(dlpEthCheck) == -1:
        Upgrade.logger.info("Dlp_eth File '%s' does not exit in the 'Image' folder\n" % dlpEth)

    filesList = []

    for root, d_names, f_names in os.walk(mypath):
        for filename in f_names:
            filesList.append(os.path.join(root, filename))

            if filename == None:
                Upgrade.logger.info("Cannot find any of the files in the 'Image' folder\n")
                Upgrade.logger.info("Please check up 'Image' folder\n")