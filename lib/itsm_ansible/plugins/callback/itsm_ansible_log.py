# (C) 2012, Michael DeHaan, <michael.dehaan@gmail.com>

# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import time
import json

from ansible.utils.unicode import to_bytes
from ansible.plugins.callback import CallbackBase
from ansible.executor.task_result import TaskResult


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'log_plays'
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(category)s - %(data)s\n\n"

    def __init__(self, task_id):

        super(CallbackModule, self).__init__()
        self.task_id = task_id
        if not os.path.exists("/tmp/ansible/task"):
            os.makedirs("/tmp/ansible/task")

        path = os.path.join("/tmp/ansible/task", self.task_id + ".log")
        if os.path.exists(path):
            os.remove(path)

    def log(self, category, data):
        log={}
        if type(data) == TaskResult:
            log["results"]= data._result
            log["host"]=data._host.get_name()
            log["task"]=data._task
        if type(data) == dict:
            log = data.copy()
            # if invocation is not None:
            #     log = json.dumps(invocation) + " => %s " % data

        path = os.path.join("/tmp/ansible/task", self.task_id + ".log")
        now = time.strftime(self.TIME_FORMAT, time.localtime())

        msg = to_bytes(self.MSG_FORMAT % dict(now=now, category=category, data=log))
        with open(path, "ab") as fd:
            fd.write(msg)

    def runner_on_failed(self, host, res, ignore_errors=False):
        res["host"] = host
        self.log(host, 'FAILED', res)

    def runner_on_ok(self, host, res):
        res["host"] = host
        self.log(host, 'OK', res)

    def runner_on_skipped(self, host, item=None):
        self.log(host, 'SKIPPED', '...')

    def runner_on_unreachable(self, host, res):
        self.log(host, 'UNREACHABLE', res)

    def runner_on_async_failed(self, host, res, jid):
        self.log(host, 'ASYNC_FAILED', res)

    def playbook_on_import_for_host(self, host, imported_file):
        self.log(host, 'IMPORTED', imported_file)

    def playbook_on_not_import_for_host(self, host, missing_file):
        self.log(host, 'NOTIMPORTED', missing_file)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.log('FAILED', result)

    def v2_runner_on_ok(self, result):
        self.log('OK', result)

    def v2_runner_on_skipped(self, result):
        self.log('SKIPPED', result)

    def v2_runner_on_unreachable(self, result):
        self.log('UNREACHABLE', result)

    def v2_playbook_on_no_hosts_matched(self):
        self.log('NO HOSTS MATCHED', "....")

    def v2_playbook_on_no_hosts_remaining(self):
        self.log('NO HOSTS REMAINING', "....")

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.log('TASK_START', {"name": task.get_name().strip()})

    def v2_playbook_on_cleanup_task_start(self, task):
        self.log("CLEANUP TASK", {"name": task.get_name().strip()})

    def v2_playbook_on_handler_task_start(self, task):
        self.log("RUNNING HANDLER",  {"name": task.get_name().strip()})

    def v2_playbook_on_play_start(self, play):
        pass
        # name = play.get_name().strip()
        # if not name:
        #     name = ""
        # self.log("PLAY", name)

    def v2_on_file_diff(self, result):
        self.log("FILE DIFFERENT", result)

    def v2_playbook_item_on_ok(self, result):

        delegated_vars = result._result.get('_ansible_delegated_vars', None)
        if result._task.action == 'include':
            return
        elif result._result.get('changed', False):
            if delegated_vars:
                msg = "changed: [%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "changed: [%s]" % result._host.get_name()
            color = 'yellow'
        else:
            if delegated_vars:
                msg = "ok: [%s -> %s]" % (result._host.get_name(), delegated_vars['ansible_host'])
            else:
                msg = "ok: [%s]" % result._host.get_name()
            color = 'green'

        msg += " => (item=%s)" % (result._result['item'],)

        if (
                        self._display.verbosity > 0 or '_ansible_verbose_always' in result._result) and not '_ansible_verbose_override' in result._result:
            msg += " => %s" % self._dump_results(result._result)
        self.log("ITEM OK", msg)

    def v2_playbook_item_on_failed(self, result):
        self.log("ITEM FAIL", result)

    def v2_playbook_item_on_skipped(self, result):
        self.log("ITEM SKIPPED", result)

    def v2_playbook_on_include(self, included_file):
        msg = 'included: %s for %s' % (included_file._filename, ", ".join([h.name for h in included_file._hosts]))
        self.log("INCLUDE FILE", msg)

    def v2_playbook_on_start(self, playbook):
        self.log("PLAYBOOK START", {"name": playbook._file_name})

    def v2_playbook_on_finish(self, playbook):
        self.log("PLAYBOOK FINISH", {"name": playbook._file_name})
