#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

import json

__metaclass__ = type

import traceback

from itsm_ansible.cli import CLI
from ansible.errors import AnsibleError
from itsm_ansible.executor.playbook_executor import PlaybookExecutor
from itsm_ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play_context import PlayContext
from ansible.utils.vars import load_extra_vars
from ansible.vars import VariableManager
from itsm_ansible.error import ITSMAnsibleError

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display

    display = Display()


# ---------------------------------------------------------------------------------------------------

class PlaybookCLI(CLI):
    ''' code behind ansible playbook cli'''

    def parse(self):

        # create parser for CLI options
        parser = CLI.base_parser(
            usage="%prog playbook.yml",
            connect_opts=True,
            meta_opts=True,
            runas_opts=True,
            subset_opts=True,
            check_opts=True,
            inventory_opts=True,
            runtask_opts=True,
            vault_opts=True,
            fork_opts=True,
            module_opts=True,
        )

        self.options, self.args = parser.parse_args(self.args[1:])

        self.parser = parser

        display.verbosity = self.options.verbosity
        self.validate_conflicts(runas_opts=True, vault_opts=True, fork_opts=True)

    def run(self):

        super(PlaybookCLI, self).run()

        # Note: slightly wrong, this is written so that implicit localhost
        # Manage passwords
        sshpass = None
        becomepass = None
        vault_pass = None
        passwords = {}

        loader = DataLoader()

        variable_manager = VariableManager()
        variable_manager.extra_vars = load_extra_vars(loader=loader, options=self.options)

        # create the inventory, and filter it based on the subset specified (if any)
        hostlist = self.translate_inventory_itsm_to_ansible(self.options.inventory)
        pt = self.creaate_palybook_target(self.options.inventory)
        task_id = self.get_task_id(self.options.inventory)
        playbook_location = json.loads(self.options.inventory)["playbook"]
        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=hostlist)
        variable_manager.set_inventory(inventory)

        no_hosts = False
        if len(inventory.list_hosts()) == 0:
            # Empty inventory
            display.warning("provided hosts list is empty, only localhost is available")
            no_hosts = True
        if len(inventory.list_hosts()) == 0 and no_hosts is False:
            # Invalid limit
            raise AnsibleError("Specified --limit does not match any hosts")

        # create the playbook executor, which manages running the plays via a task queue manager
        pbex = PlaybookExecutor(playbooks=[playbook_location], inventory=inventory, variable_manager=variable_manager,
                                loader=loader, options=self.options, passwords=passwords, pt=pt, task_id=task_id)

        results = pbex.run()

        if isinstance(results, list):
            for p in results:

                display.display('\nplaybook: %s' % p['playbook'])
                for idx, play in enumerate(p['plays']):
                    msg = "\n  play #%d (%s): %s" % (idx + 1, ','.join(play.hosts), play.name)
                    mytags = set(play.tags)
                    msg += '\tTAGS: [%s]' % (','.join(mytags))

                    if self.options.listhosts:
                        playhosts = set(inventory.get_hosts(play.hosts))
                        msg += "\n    pattern: %s\n    hosts (%d):" % (play.hosts, len(playhosts))
                        for host in playhosts:
                            msg += "\n      %s" % host

                    display.display(msg)

                    all_tags = set()
                    if self.options.listtags or self.options.listtasks:
                        taskmsg = ''
                        if self.options.listtasks:
                            taskmsg = '    tasks:\n'

                        all_vars = variable_manager.get_vars(loader=loader, play=play)
                        play_context = PlayContext(play=play, options=self.options)
                        for block in play.compile():
                            block = block.filter_tagged_tasks(play_context, all_vars)
                            if not block.has_tasks():
                                continue

                            for task in block.block:
                                if task.action == 'meta':
                                    continue

                                all_tags.update(task.tags)
                                if self.options.listtasks:
                                    cur_tags = list(mytags.union(set(task.tags)))
                                    cur_tags.sort()
                                    if task.name:
                                        taskmsg += "      %s" % task.get_name()
                                    else:
                                        taskmsg += "      %s" % task.action
                                    taskmsg += "\tTAGS: [%s]\n" % ', '.join(cur_tags)

                        if self.options.listtags:
                            cur_tags = list(mytags.union(all_tags))
                            cur_tags.sort()
                            taskmsg += "      TASK TAGS: [%s]\n" % ', '.join(cur_tags)

                        display.display(taskmsg)

            return 0
        else:
            return results

    def translate_inventory_itsm_to_ansible(self, hosts):
        inv = {
            # "all": {
            #     "hosts": [],
            #     "vars": {
            #
            #     }
            # },
            "_meta": {
                "hostvars": {

                }
            }
        }
        try:
            hosts = json.loads(hosts)
            for host in hosts["hosts"]:

                # 构建host
                n_h = {
                        "ansible_user": host["user"],
                        "ansible_ssh_pass": host["password"],
                        "ansible_port": host["port"],
                        "ansible_host": host["ip"],
                        "ansible_become_pass": host["password"],
                        #"ansible_become": host["user"],
                        #"roles": host["roles"],

                }
                # 如果没有groups字段或者group字段为空或者group字段不是一个list,都放到all组
                if (not host.has_key("groups")) or (len(host["groups"]) == 0 or (not isinstance(host["groups"], list))):
                    host["groups"] = ["all"]

                for g in host["groups"]:
                    if not inv.has_key(g):
                        inv[g] = {"hosts": [], "vars": {}}
                    inv[g]["hosts"].append(host["hostname"])

                # 判断是否有host_vars
                if host.has_key("host_vars"):
                    inv["_meta"]["hostvars"][host["hostname"]] = dict(n_h, **host["host_vars"])
                else:
                    inv["_meta"]["hostvars"][host["hostname"]] = n_h

            if hosts.has_key("group_vars"):
                for k, v in hosts["group_vars"].iteritems():
                    if not inv.has_key(k):
                        inv[k] = {"hosts": [], "vars": {}}
                    inv[k]["vars"] = v
            return inv
        except:
            traceback.print_exc()
            raise ITSMAnsibleError("解析主机列表出错")

    def creaate_palybook_target(self, hosts):
        pt = [{
            "hosts": "all",
            "tasks": []
        }]
        try:
            hosts = json.loads(hosts)
            for h in hosts["host_roles"]:
                #{\"hosts\":\"all\",\"roles\":[{\"role\": \"common\", \"vars\": {}}]},
                host = {
                    "hosts": h["hosts"]
                }
                roles = []
                for r in h["roles"]:
                    role = dict({"role": r["role"]}, **r["vars"])
                    roles.append(role)
                host["roles"] = roles
                pt.append(host)
            return pt
        except:
            print(traceback.format_exc())
            raise ITSMAnsibleError("解析主机列表出错")

    def get_task_id(self, hosts):
        try:
            hosts = json.loads(hosts)
            return hosts["task_id"]
        except:
            print(traceback.format_exc())
            raise ITSMAnsibleError("解析主机列表出错")
