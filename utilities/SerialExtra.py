"""
    File:
        SerialExtra.py
    Brief:
        Extension serial library
    Author:
        Neo
    History:
        2020/12/03 - Initialization version
"""

import sys
import serial
import re
import ctypes

sys.path.append('library/')

from time import sleep
from library import serial
from utilities import ErrorCodeDef as ErrCode

class SerialExtra(serial.Serial):
    """
    Inherit from Serial class
    """

    def send_and_result(self, develop, write, read_until, error_check):
        """

        :param write:
        :param read_until:
        :return:
        """

        self.flushInput()
        self.write(write.encode('utf-8', 'ignore'))
        develop.logger.info(write)

        response = ""
        if type(read_until) == type(str()):
            token_list = (read_until)
        else:
            token_list = tuple(read_until)

        while not response.endswith(token_list):
            character = self.read().decode('utf-8', 'ignore')
            sys.stdout.write(character)
            sys.stdout.flush()

            if not character: return response

            response = response + character

        develop.logger.info(response)

        if response.find(error_check) != -1:
            return token_list
        else:
            return -1

    def send_and_read(self, Upgrade, write, read_until):
        """

        :param write:
        :param read_until:
        :return:
        """
        self.flushInput()
        self.write(write.encode('utf-8', 'ignore'))
        return self.wait_for(Upgrade, read_until)

    def wait_for(self, Upgrade, token):
        """

        :param token:
        :return:
        """
        # wait for some text to appear
        response = ""
        if type(token) == type(str()):
            token_list = (token)
        else:
            token_list = tuple(token)

        while not response.endswith(token_list):
            character = self.read().decode('utf-8', 'ignore')
            sys.stdout.write(character)
            sys.stdout.flush()

            response = response + character

        return response


    def sender(self, command, returnType = True, waitingTime = 2):
        """

        :param command:
        :param returnType:
        :param waitingTime:
        :return:
        """
        self.flushInput()
        self.write(command)

        if returnType == True:
            sleep(waitingTime)
            bytesToRead = self.inWaiting()
            if bytesToRead == ErrCode.IS_EMPTY: return ErrCode.FAIL
            return self.read(bytesToRead)