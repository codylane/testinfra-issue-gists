# coding: utf-8
# flake8: noqa

from __future__ import absolute_import
from __future__ import unicode_literals
from testinfra.utils.ansible_runner import AnsibleRunner
try:
    from ansible.cli.playbook import PlaybookCLI
    from ansible.cli import CLI
    from ansible.playbook import Playbook
    import ansible
except ImportError:
    raise RuntimeError("You must install ansible")

import json
import os


PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

INVENTORY_FILE = os.path.join(PROJECT_ROOT_DIR, 'inventory')

RUNNER = AnsibleRunner(INVENTORY_FILE)

testinfra_hosts = RUNNER.get_hosts('all')

def read_playbook(*args):
    args_list = list(args)
    cli = PlaybookCLI(args_list)
    parser = cli.base_parser(
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
    cli.options, cli.args = parser.parse_args(args_list)
    cli.normalize_become_options()
    cli.options.connection = 'smart'
    cli.options.inventory = 'inventory'

    loader, inventory, variable_manager = cli._play_prereqs(cli.options)

    pb = Playbook.load(cli.args[0], variable_manager, loader)

    for play in pb.get_plays():
        yield variable_manager.get_vars(play)


# testinfra_hosts = (
#     'ansible://foo-centos7?ansible_inventory=' + INVENTORY_FILE,
#     'ansible://foo-ubuntu1404?ansible_inventory=' + INVENTORY_FILE,
# )

def test_hostvars(host):
    for vars in read_playbook('playbook.yml'):
        err_msg =  json.dumps(vars, indent=2, ensure_ascii=False, sort_keys=True)
        assert vars['pyenv_install_these_pythons'] == ['2.7.15'], err_msg
        assert vars['pyenv_user'] == 'vagrant', err_msg
        assert vars['pyenv_group'] == 'vagrant', err_msg
        assert vars['pyenv_root'] == '/home/vagrant/.pyenv', err_msg
