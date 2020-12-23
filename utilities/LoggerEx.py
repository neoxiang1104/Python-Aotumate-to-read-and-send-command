"""
    File:
        LoggerEx.py
    Brief:
        Python logging module enhanced version
    Author:
        Neo
    History:
        2020/12/03 - Initialization version
"""
import logging
import colorama

# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
class LoggerEx(logging.Logger):
    """
    Inherit from logging.Logger class
    """
    def __init__(self, name, level=logging.DEBUG):
        """
        Initialize the logger with a name and an optional level.

        :param name:
        :param level:
        """
        logging.Filterer.__init__(self)
        self.name      = name
        self.level     = logging._checkLevel(level)
        self.parent    = None
        self.propagate = 1
        self.handlers  = []
        self.disabled  = 0
        self._cache    = {}
        colorama.init(autoreset=True)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, colorama.Fore.LIGHTGREEN_EX + msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, colorama.Fore.LIGHTWHITE_EX + msg, args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARN'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warn("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.isEnabledFor(logging.WARN):
            self._log(logging.WARN, colorama.Fore.LIGHTCYAN_EX + msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, colorama.Fore.LIGHTRED_EX + msg, args, **kwargs)


def GetLoggerEx(name=None):
    """
    Return a LoggerEx with the specified name

    :param name:
    :return:
    """
    return LoggerEx(name)


def ConfigLoggerEx(moduleName, logLevel, logFileName=None, fileFormatter=None, consoleFormatter=None):
    """
    Set the logging level and output format of this loggerEx

    :param moduleName:
    :param logLevel:
    :param logFileName:
    :param fileFormatter:
    :param consoleFormatter:
    :return:
    """
    loggerEx = GetLoggerEx(moduleName)
    loggerEx.setLevel(logLevel)

    # Create file handler which logs even debug messages
    if logFileName is not None:
        fileHandler = logging.FileHandler(logFileName)
        fileHandler.setLevel(logLevel)
        # Create formatter and add it to the handlers
        if fileFormatter is None:
            fileHandler.setFormatter(logging.Formatter('%(message)s'))
        else:
            fileHandler.setFormatter(logging.Formatter(fileFormatter))
        # Add the handlers to the logger
        loggerEx.addHandler(fileHandler)

    # Create console handler with a higher log level
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logLevel)

    # Create formatter and add it to the handlers
    if consoleFormatter is None:
        consoleHandler.setFormatter(logging.Formatter('%(message)s'))
    else:
        consoleHandler.setFormatter(logging.Formatter(consoleFormatter))
    # Add the handlers to the logger
    loggerEx.addHandler(consoleHandler)

    return loggerEx
