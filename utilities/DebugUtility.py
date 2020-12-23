"""
    File:
        DebugUtility.py
    Brief:
        Debug utility API
    Author:
        Leon
    History:
        2019/04/25 - Initialization version
        2019/05/27 - Added tracking function
"""
import inspect
import logging

from functools import wraps


# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------
# Default levels and level names
LOG_DEBUG    = logging.DEBUG
LOG_INFO     = logging.INFO
LOG_WARN     = logging.WARN
LOG_ERR      = logging.ERROR
LOG_CRITICAL = logging.CRITICAL


# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
def GetFuncName():
    """

    :return:
    """
    return inspect.stack()[1][3]


def GetClassName(classObject):
    """

    :param classObject:
    :return:
    """
    className = classObject.__class__
    return str(className).split("'")[1].split(".")[2]


def GetMethodName(classObject, fullName=True):
    """

    :param classObject:
    :param fullName:
    :return:
    """
    className = classObject.__class__
    if fullName is not True:
        return str(inspect.stack()[1][3])
    else:
        return str(className).split("'")[1] + "." + str(inspect.stack()[1][3])


def GetMethodDesc(methodObject):
    """

    :param methodObject:
    :return:
    """
    return inspect.getdoc(methodObject)


def GetCallerName():
    """

    :return:
    """
    return inspect.stack()[2][3]


def DumpDictObj(logger, dictName, dictObj, order=None, subOrder=None, offset=""):
    """
    Dump dictionary object

    :param logger:
    :param dictName:
    :param dictObj:
    :param order:
    :param subOrder:
    :param offset:
    :return:
    """
    logger.info("%s<<< %s >>>" % (offset, dictName))

    if order is not None:

        for item in order:

            if item not in dictObj: continue

            if isinstance(dictObj[item], dict):

                for subItem in subOrder:
                    logger.info("\t%16s : %s" % (subItem, dictObj[item][subItem]))
            else:
                logger.info("\t%16s : %s" % (item, dictObj[item]))
    else:

        for item in dictObj:

            if type(dictObj[item]) is dict: DumpDictObj(logger, item, dictObj[item], offset=offset + "\t")
            else: logger.info("%s%s : %s" % (offset + "\t", item, dictObj[item]))


def DumpObj(logger, d, objName=None, i=1):
    """

    :param logger:
    :param d:
    :param objName:
    :param i:
    :return:
    """
    if objName is not None:
        logger.debug("\n")
        logger.debug("-" * 100)
        logger.debug("<<< %s >>>", objName)

    t = "\t" * i
    for p, v in d.items():
        if isinstance(v, dict):
            logger.debug(f"{t}{p}:")
            DumpObj(logger, v, None, i + 1)
        elif isinstance(v, list):
            if len(v) < 1:
                logger.debug(f"{t}{p}: []")
            elif isinstance(v[0], int) or isinstance(v[0], str):
                logger.debug(f"{t}{p}: {v}")
            else:
                logger.debug(f"{t}{p}: [")
                for v2 in v:
                    if isinstance(v2, dict):
                        DumpObj(logger, v2, None, i + 1)
                    else:
                        logger.debug(f"{t}\t{v2}")
                    if len(v) == v.index(v2) + 1:
                        logger.debug(f"{t}]")
        else:
            logger.debug(f"{t}{p}: {v}")
