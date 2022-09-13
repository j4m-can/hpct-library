# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/interface/value/network.py

"""Interface network value objects.
"""

import ipaddress

from .. import codec, checker
from ..base import NoValue
from . import XValue, Integer


class IPAddress(XValue):
    codec = codec.IPAddress()
    default = ipaddress.IPv4Address("0.0.0.0")


class IPNetwork(XValue):
    codec = codec.IPNetwork()
    default = ipaddress.IPv4Network("0.0.0.0")


class Port(Integer):
    codec = codec.Integer()
    default = 0
    checker = checker.IntegerRange(0, 65535)


class PrivilegedPort(Port):
    checker = checker.IntegerRange(0, 1023)


class UnprivilegedPort(Port):
    default = 1024
    checker = checker.IntegerRange(1024, 65535)


class URL(XValue):
    codec = codec.String()
    default = ""
    checker = checker.URL()
