from odoo import http
from .ApiException import ApiException
import re
from datetime import datetime


class Params(object):

    @staticmethod
    def verify(verify_params: list = [], data_params: dict = None):
        """
        Hàm kiểm tra tham số theo quy tắc

        Quy tắc của tham số được sử dụng trong verify_params ví dụ như sau:

        ['user_id|int|require:partner_id',
        'partner_id|int',
        'duration|float~int|nullable',
        'birthday'|date:%Y-%m-%d|require',
        'start_time|datetime:%Y-%m-%d %H:%M:%S',
        'email|str:[\w\.]{3,}@[a-zA-Z]+([.a-z]{2,6}){1,4}|require',
        'user_ids|list',
        'partner_ids|tuple',
        'products|dict']

        Diễn giải:
            Tham số         |       Kiểu dữ liệu        |       Định dạng       |          Bắt buộc     |       Cho phép null       |       Ghi chú

            user_id             int                                                 yes                                                 Bắt buộc nếu có partner_id
            partner_id          int
            duration            float,int                                                                    yes
            birthday            date                        %Y-%m-%d                yes
            start_time          datetime                    %Y-%m-%d %H:%M:%S
            email               str                         [\w\.]{3,}@[a-...       yes
            user_ids            list
            partner_ids         tuple
            products            dict

        Các quy tắc như sau:
            * Kiểu dữ liệu: int, str, bool, list, dict, float, date, datetime
            * Bắt buộc: require
            * Cho phép null: nullable

        @param verify_params: Danh sách tham số và quy tắc áp dụng
        @param data_params: Danh sách tham số cần áp dụng quy tắc
        @return: Trả về True nếu tất cả tham số được áp dụng quy tắc đều hợp lệ,
                 Trả về ApiException nếu 1 trong các tham số không đúng quy tắc
        """

        __DATA_TYPE = ['int', 'float', 'long', 'list', 'dict', 'bool']
        __DATA_TYPE_FORMAT = ['str']
        __DATA_TYPE_DATETIME = ['date', 'datetime']

        if not data_params:
            data_params = http.request.jsonrequest

        for item in verify_params:
            split_data = item.split('|')
            field = split_data[0].split(':')
            field_name = field[-1]
            rules = split_data[1:]

            for rule in rules:
                if re.search(r'(require)(\:\w+)*', rule):
                    Params.__require(field, rule, data_params)
                    continue

                if field[0] not in data_params:
                    continue

                # Sử lý trường hợp rule hỗn hợp
                # VD: duration|float,int
                _rules = rule.split('~')
                if len(_rules) > 1:
                    is_correct_type = False
                    data_types = []
                    for _rule in _rules:
                        try:
                            if _rule.split(':')[0] in __DATA_TYPE:
                                Params.__validate_data_type(field_name, _rule, data_params.get(field[0]),
                                                            'nullable' in rules)
                                is_correct_type = True
                                break

                            if _rule.split(':')[0] in __DATA_TYPE_FORMAT:
                                Params.__validate_data_type_format(field_name, _rule, data_params.get(field[0]),
                                                                   'nullable' in rules)
                                is_correct_type = True
                                break

                            if _rule.split(':')[0] in __DATA_TYPE_DATETIME:
                                Params.__validate_data_type_datetime(field_name, _rule, data_params.get(field[0]),
                                                                     'nullable' in rules)
                                is_correct_type = True
                                break

                        except ApiException as e:
                            data_types.append(_rule.split(':')[0])

                    if not is_correct_type:
                        raise ApiException('Trường %s có kiểu dữ liệu thuộc %s không phải %s'
                                           % (field_name, str(data_types), type(data_params.get(field[0])).__name__),
                                           ApiException.INVALID_DATA_TYPE)
                    continue

                # Sử lý trường hợp rule đơn lẻ
                # Ví: rule: duration|int
                if rule.split(':')[0] in __DATA_TYPE:
                    Params.__validate_data_type(field_name, rule, data_params.get(field[0]), 'nullable' in rules)
                    continue

                if rule.split(':')[0] in __DATA_TYPE_FORMAT:
                    Params.__validate_data_type_format(field_name, rule, data_params.get(field[0]), 'nullable' in rules)
                    continue

                if rule.split(':')[0] in __DATA_TYPE_DATETIME:
                    Params.__validate_data_type_datetime(field_name, rule, data_params.get(field[0]),
                                                         'nullable' in rules)
                    continue

    @staticmethod
    def __require(field: str, rule: str, params: dict = None, rules: str = ''):
        file_name = field[-1]
        split_rule = rule.split(':')
        relation_rule = split_rule[1] if len(split_rule) == 2 else ''

        data_pos = relation_rule.find('{')
        relation = relation_rule
        relation_data = []
        if data_pos >= 0:
            relation = relation_rule[0:data_pos]
            relation_data = relation_rule[data_pos:]

        if isinstance(field[0], list) and any([x in params for x in field[0]]):
            if not relation:
                return
        if len(relation_data) < 1:
            if isinstance(field[0], str) and relation and not params.get(relation, False):
                return
            if isinstance(field[0], str) and field[0] in params:
                if not relation or relation in params:
                    if re.search(r'(nullable)(\:\w+)*', rules):
                        return
                    if not str(params.get(field[0])).strip():
                        raise ApiException("Trường %s không được để trống !" % file_name,
                                           ApiException.INVALID_DATA_TYPE)
                    return
            raise ApiException("Trường %s đang bị thiếu" % file_name, ApiException.PARAM_NOT_PROVIDE)
        else:
            if params.get(relation, '') not in relation_data:
                return
            else:
                if params.get(field[0]) == '':
                    raise ApiException("Trường %s không được để trống !" % file_name, ApiException.INVALID_DATA_TYPE)
                if not params.get(field[0]):
                    raise ApiException("Trường %s đang bị thiếu" % file_name, ApiException.PARAM_NOT_PROVIDE)

    @staticmethod
    def __validate_data_type(field, rule, value, nullable=False):
        if nullable and not value:
            return
        try:
            data_type = eval(rule)
        except Exception as e:
            raise ApiException(str(e), ApiException.UNKNOWN_ERROR)

        if not isinstance(value, data_type):
            raise ApiException('Trường %s có kiểu dữ liệu là %s không phải %s'
                               % (field, data_type.__name__, type(value).__name__), ApiException.INVALID_DATA_TYPE)

    @staticmethod
    def __validate_data_type_format(field, rule, value, nullable=False):
        if nullable and not value:
            return
        split_rule = rule.split(':')
        Params.__validate_data_type(field, split_rule[0], value, nullable)
        if len(split_rule) == 1:
            return
        pattern = re.compile(split_rule[1])
        if split_rule[0] == 'str' and not pattern.fullmatch(value):
            raise ApiException('%s không đúng định dạng.' % field, ApiException.INVALID_DATA_FORMAT)
        return

    @staticmethod
    def __validate_data_type_datetime(field, rule, value, nullable=False):
        if nullable and not value:
            return
        split_rule = rule.split(':')
        data_type = split_rule[0]
        pattern = '%Y-%m-%d'
        if data_type == 'datetime':
            pattern += ' %H:%M:%S'
        if split_rule == 2:
            pattern = split_rule[1]
        try:
            datetime.strptime(value, pattern)
            return
        except Exception as e:
            raise ApiException('Trường %s không đúng định dạng %s' % (field, pattern), ApiException.INVALID_DATA_TYPE)
