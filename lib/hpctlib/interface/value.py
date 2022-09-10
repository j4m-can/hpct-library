# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/interface/value.py

"""Supported interface value objects.

Note: Test exposing values rather than codecs. Codecs would be hidden.
"""

import ipaddress

from .base import NoValue, Value
from . import codec


class XValue(Value):
    codec = None
    default = None
    checker = None

    def __init__(self, default=NoValue, checker=None):
        self.default = self.default if default == NoValue else default
        self.checker = self.checker if checker == None else checker
        super().__init__(self.codec, self.default, checker)


class Boolean(XValue):
    codec = codec.Boolean()
    default = False


class Blob(XValue):
    codec = codec.Blob()
    default = None


class Dict(XValue):
    codec = codec.Dict()
    default = None


class Float(XValue):
    codec = codec.Float()
    default = 0.0


class Integer(XValue):
    codec = codec.Integer()
    default = 0


class IPAddress(XValue):
    codec = codec.IPAddress()
    default = ipaddress.IPv4Address("0.0.0.0")


class IPNetwork(XValue):
    codec = codec.IPNetwork()
    default = ipaddress.IPv4Network("0.0.0.0")


class Noop(XValue):
    codec = codec.Noop()
    default = ""


class Ready(Boolean):
    pass


class String(XValue):
    codec = codec.String()
    default = ""
