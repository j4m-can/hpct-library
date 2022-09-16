# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/interface/value/network.py

"""Interface network value objects.
"""

import ipaddress

from .. import codec as _codec
from ..code import network as _network_codec
from .. import checker
from ..base import NoValue, Value
from . import Integer


class IPAddress(Value):
    codec = _network_codec.IPAddress()
    default = ipaddress.IPv4Address("0.0.0.0")


class IPNetwork(Value):
    codec = _network_codec.IPNetwork()
    default = ipaddress.IPv4Network("0.0.0.0")


class Port(Integer):
    codec = _codec.Integer()
    default = 0
    checker = checker.IntegerRange(0, 65535)


class PrivilegedPort(Port):
    checker = checker.IntegerRange(0, 1023)


class UnprivilegedPort(Port):
    default = 1024
    checker = checker.IntegerRange(1024, 65535)


class URL(Value):
    codec = _codec.String()
    checker = checker.URL()
