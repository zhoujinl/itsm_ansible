from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible.utils.unicode import to_str


class ITSMAnsibleError(Exception):
    def __init__(self, message=""):
        self.message = '%s' % to_str(message)

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
