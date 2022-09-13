# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/interface/value/__init__.py

"""Base interface value objects.
"""

import ipaddress

from .. import codec as _codec
from ..base import NoValue, Value


class Boolean(Value):
    codec = _codec.Boolean()
    default = False


class Blob(Value):
    codec = _codec.Blob()


class Dict(Value):
    codec = _codec.Dict()


class Float(Value):
    codec = _codec.Float()
    default = 0.0


class Integer(Value):
    codec = _codec.Integer()
    default = 0


class Noop(Value):
    codec = _codec.Noop()


class Ready(Boolean):
    pass


class String(Value):
    codec = _codec.String()
    default = ""
