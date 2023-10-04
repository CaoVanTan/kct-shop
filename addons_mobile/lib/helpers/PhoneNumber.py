# -*- coding: utf-8 -*-

import re


class PhoneNumber(object):
    @staticmethod
    def validate(phone_number, error_message=''):
        if not phone_number or phone_number == '':
            return True
        phone_number = phone_number.strip()
        pattern = r'0{1}[0-9]{9}'
        if not re.search(pattern, phone_number):
            raise Exception(error_message or 'Phone number must be start with "0" and it\'s length must be 10')
        return True
