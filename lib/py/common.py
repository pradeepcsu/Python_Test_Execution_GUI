import tkMessageBox
import sys
import os
import random
import string
import datetime
try:
    from robot.testdoc import TestSuiteFactory
except ImportError as e:
    tkMessageBox.showerror('Error', 'Robot Framework is not installed!')
    sys.exit(1)


regions = ['QAT', 'UAT2', 'DEV2']


def get_auts():
    root = TestSuiteFactory(os.path.join(os.getcwd(), 'test'))
    return [aut.name for aut in root.suites]


def strip_currency(curr):
    if not curr:
        return
    if curr[0] == '(' and curr[-1] == ')':
        curr = '-' + curr[1:-1]
    return curr.replace('$', '').replace(',', '').strip()


def get_timestamp():
    return datetime.datetime.now()


def get_random_string(length):
    return ''.join(random.choice(string.lowercase) for i in range(int(length)))


def get_random_number_string(length):
    return ''.join(random.choice(string.digits) for i in range(int(length)))


def get_random_alphanumeric_string(length):
    return ''.join(random.choice(string.lowercase + string.digits) for i in range(int(length)))


def get_random_ssn():
    """
    Avoid 000, 666, and 900-999 in first part
    Pick any in next three since first part is guranteed from last
    Avoid 00 and 0000 in second and third parts
    Pick any for last three
    """
    ssn = random.sample(set('1234578'), 1)
    ssn += ''.join(random.choice(string.digits) for i in range(3))
    ssn += random.sample(set('123456789'), 2)
    ssn += ''.join(random.choice(string.digits) for i in range(3))
    return ''.join(ssn)