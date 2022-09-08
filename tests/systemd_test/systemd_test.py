#! /usr/bin/env python3
#
# systemd_test.py

import json
import os.path
import pprint
import sys

sys.path.insert(0, os.path.realpath("../../lib"))

from hpctlib.editors.os.systemd import SystemdConfFileEditor


if __name__ == "__main__":
    sep = "----------"

    e = SystemdConfFileEditor()
    # e.load("resolved.conf")
    e.load("pipewire-session-manager.service")

    print(e.render())

    print(sep)
    print(json.dumps(e.render_json(), indent=2, sort_keys=True))

    print(sep)
    # e.remove_group("b")
    print(e.get_section_names())
    print(e.get_settings("Install"))
    # print(e.render())

    print(sep)
    # print(e.get_groups())
