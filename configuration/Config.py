"""
    File:
        Config.py
    Brief:
        Provide configuration XML parser function
    Author:
        Neo
    History:
        2020/12/03 - Initialization version
"""
import os
import sys
import csv
import traceback
import functools
import xmltodict
import collections

sys.path.append('utilities/')

from utilities import DebugUtility as DBG


# -----------------------------------------------------------------------------
#    Constant
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Variables & Type declaration
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
#    Function declaration
# -----------------------------------------------------------------------------
def ExceptionHandler(func):
    """

    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(self, *a, **kw):
        try:
            return func(self, *a, **kw)
        except Exception as e:
            print("\n")
            print("-" * 100, "\n[ERROR]:", e, "\n")
            print("\n[TRACE]:")
            print(traceback.format_exc())
            print("\n[RAISE]:")
            raise
    return wrapper


class ConfigException(Exception):
    pass


class XmlLib:

    def __init__(self,
                 logger,
                 path,
                 CONFIG_SET_XML=None,):
        """

        :param logger:
        :param path:
        :param CONFIG_SET_XML
        """
        self.logger     = logger
        self.path       = path
        self.CONFIG_SET = None

        self.logger.debug("Path: {}".format(self.path))

        # Try to get env config file name from env vars
        try:
            config_set_xml = os.environ["TEST_CONFIG"] if CONFIG_SET_XML is None else CONFIG_SET_XML
        except KeyError:
            config_set_xml = "CONFIG_SET"

        # Config_Test
        self.config_set_xml_path = self.path + os.sep + "{}.xml".format(config_set_xml)
        if not os.path.exists(self.config_set_xml_path):
            raise ConfigException("Given Serial Port Config xml doesn't exist.\n"
                                  "Serial Port config setting xml path: {}\n".format(self.config_set_xml_path))

        self.logger.debug("config_set_xml_path: {}".format(self.config_set_xml_path))
        self.CONFIG_SET = self.ParseXml(self.config_set_xml_path, "CONFIG_SET")


    @staticmethod
    @ExceptionHandler
    def ParseXml(xml_file, xml_element, xml_root_element=None):
        """

        :param xml_file:
        :param xml_element:
        :param xml_root_element:
        :return:
        """
        with open(xml_file) as xml_f:
            xml_str = xml_f.read()
            xml_str = xml_str.replace("ï»¿", "")

        xml_dict = xmltodict.parse(xml_str, encoding="utf-8")
        if xml_dict.get(xml_element):
            parameters = xml_dict[xml_element]
        elif xml_root_element is not None:
            parameters = xml_dict[list(xml_dict.keys())[0]][xml_root_element][xml_element]
        else:
            parameters = xml_dict[list(xml_dict.keys())[0]][xml_element]

        retVal = {}
        for parameter in parameters:
            try:
                value = parameters[parameter]
            except KeyError:
                value = ''
            value = XmlLib.ParseParameterValues(value, parameter)
            retVal.update({parameter: value})
        return retVal

    @staticmethod
    @ExceptionHandler
    def ParseParameterValues(value, parameter):
        """

        :param value:
        :param parameter:
        :return:
        """

        def to_list(_val, _par, _a):
            """

            :param _val:
            :param _par:
            :param _a:
            :return:
            """
            v_list = _val.get(_par, [])
            if not isinstance(v_list, list):
                if _a:
                    _val[_par] = [v_list]
                    return _val
                else:
                    return [v_list]
            else:
                if _a:
                    _val[_par] = v_list
                    return _val
                else:
                    return v_list

        try:
            if value is not None:
                value = int(value)
        except (ValueError, TypeError):
            if isinstance(value, collections.OrderedDict) or isinstance(value, dict):
                new_value = dict()
                for i in value:
                    new_value.update({i.strip("@"): XmlLib.ParseParameterValues(value[i], i)})
                value = new_value
            elif isinstance(value, list):
                for i, val in enumerate(value):
                    value[i] = XmlLib.ParseParameterValues(val, parameter)
            elif value.startswith('['):
                for item in ['[', ']', ' ']:
                    if item in value:
                        value = value.replace(item, '')
                value = list(map(lambda r: XmlLib.Convert(r), value.split(',')))
            elif value.startswith('0x'):  # str to hex
                value = int(str(value), 16)
            elif value.startswith('-') and len(str(value)) > 1:  # negative str to float
                value = float(value)
            elif value.lower() == 'true':  # str to boolean TRUE
                value = bool(value)
            elif value.lower() == 'false':  # str to boolena FALSE
                value = bool()
            elif value.lower() == 'none':  # str to boolena FALSE
                value = None
        return value

    @staticmethod
    @ExceptionHandler
    def Convert(val):
        """

        :param val:
        :return:
        """
        try:
            r_val = int(val)
        except ValueError:
            r_val = val if isinstance(val, str) else val.decode("utf-8")
        return r_val

    def GetInstance(self):
        """

        :return:
        """
        return self


def SELF_TEST_FUNC(logger):
    """
    Self test function

    :return:
    """
    config = XmlLib(logger,
                    path=os.path.abspath('.'),
                    CONFIG_SET_XML=None)

    #logger.debug("\n{}".format(config.NR5G_FREQ_BAND))

    logger.debug("\n{}".format(config.CONFIG_SET))
    DBG.DumpObj(logger, config.CONFIG_SET['LOGGER_INFO'], 'LOGGER_INFO')

    logger.debug("\n{}".format(config.CONFIG_SET))
    #logger.debug("\n{}".format(config.HDVT_TC_EXT_CONFIG))
    #logger.debug("\n{}".format(config.UNIT_SUPPORT_LIST))

    return config
