# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/interface/base.py


"""Base implementation of Interface, Value, SuperInterface.
"""


import json
import logging
from typing import Any


logger = logging.getLogger(__name__)


class AccessError(Exception):
    pass


class NoValue:
    def __str__(self):
        return "no value"

    def __repr__(self):
        return "no value"


NoValue = NoValue()


class Value:
    """Base descriptor for use with interfaces. The interface provides
    storage via its get() and set().

    The checker validates the value encoded and decoded.

    The codec encodes (to string) and decodes (from string).

    The default is return when there is no value set.

    The access is zero or combined "r"ead and "w"rite.
    """

    checker = None
    codec = None
    default = NoValue

    def __init__(self, default=NoValue, checker=None, codec=None, **kwargs):
        self.checker = self.checker if checker == None else checker
        self.codec = self.codec if codec == None else codec
        self.default = self.default if default == NoValue else default
        self.access = kwargs.get("access", "rw")

    def __get__(self, owner, objtype=None):
        """Return value (from owner)."""
        if owner == None:
            return self

        if "r" not in self.access:
            raise AccessError("value not readable")

        value = owner._get(self.name, NoValue)
        if value == NoValue:
            value = self.default
        else:
            value = self.codec.decode(value)

        # only check for non-NoValue values
        if value != NoValue and self.checker:
            self.checker.check(value)

        return value

    def __set__(self, owner, value):
        """Set value (in owner)."""

        if value == NoValue:
            return

        if "w" not in self.access:
            raise AccessError("value not writable")

        if self.checker:
            self.checker.check(value)

        value = self.codec.encode(value)
        owner._set(self.name, value)

    def __set_name__(self, owner, name):
        """Set name (mangle to put in owner)."""
        self.name = name


class Interface:
    """Base interface class providing standard functionality.

    A minimum number of methods, with specific names, are provided to
    avoid polluting the namespace. This allows clean integration with
    descriptors (from Value).
    """

    def __init__(self, *args, **kwargs):
        self._basecls = (Value, Interface)
        self._prefix = None
        self._store = {}

        # patch in "_store" for sub Interface
        for k in dir(self):
            iface = getattr(self, k)
            if isinstance(iface, Interface):
                self._patch_subinterface(k, iface)

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__} keys ({self.get_keys()})>"

    def __contains__(self, key):
        """Support for "has"."""

        return issubclass(getattr(self.__class__, key), self._basecls)

    def _get(self, key, default=None):
        """Accessor for the interface store."""

        return self._store.get(self.get_fqkey(key), default)

    def _patch_subinterface(self, k, iface):
        iface._prefix = k
        iface._store = self._store

    def _set(self, key, value):
        """Accessor for the interface store."""

        self._store[self.get_fqkey(key)] = value

    def clear(self, key=None):
        """Clear one or all interface keys from storage."""

        keys = [key] if key != None else self.get_keys()
        for key in keys:
            del self._store[self.get_fqkey(key)]

    def get_doc(self, show_values=False):
        """Return json object about interface."""

        try:
            values = {}
            doc = (self.__class__.__doc__ or "").strip()
            j = {
                "interface": self.__class__.__name__,
                "module": self.__module__,
                "description": doc.strip(),
                "values": values,
            }

            for k in self.get_keys():
                # TODO: call Value.get_doc()
                v = getattr(self.__class__, k)

                if isinstance(v, Interface):
                    values[k] = v.get_doc()
                else:
                    doc = (v.__doc__ or "").strip()
                    codec_doc = v.codec.get_doc() if v and v.codec else None
                    checker_doc = v.checker.get_doc() if v and v.checker else None
                    values[k] = {
                        "type": v.__class__.__name__,
                        "module": v.__module__,
                        "codec": codec_doc,
                        "checker": checker_doc,
                        "description": doc.strip(),
                    }

                    if show_values:
                        values[k]["value"] = getattr(self, k)
        except Exception as e:
            raise

        return j

    def get_fqkey(self, key):
        """Return fully qualified key. Support for sub-Interface dotted notation."""

        return key if not self._prefix else f"{self._prefix}.{key}"

    def get_keys(self):
        """Get keys of all descriptors for this interface."""

        prefix = f"{self._prefix}."
        prefixlen = len(prefix)
        keys = []
        for k in dir(self):
            if (
                hasattr(self.__class__, k)
                and isinstance(getattr(self.__class__, k), self._basecls)
                and k.startswith(prefix)
            ):
                if "." not in k:
                    keys.append(k[prefixlen:])
        return keys

    def get_all_keys(self):
        """Get all keys."""

        keys = []
        for k in dir(self):
            if hasattr(self.__class__, k) and isinstance(
                getattr(self.__class__, k), self._basecls
            ):
                keys.append(k)
        return keys

    def get_items(self):
        """Get descriptor items."""

        return [(k, getattr(self, k)) for k in self.get_keys()]

    def is_ready(self):
        """Return if the interface is ready."""

        return False

    def mount(self, key, subiface, force=False):
        """Dynamically mount/attach a sub-interface at an anchor.

        Note: Added as an instance member *not* a class member.

        Q. Should this be added as a class member?"""

        if not hasattr(self, key) or force:
            if not isinstance(subiface, (Interface,)):
                raise Exception("interface must be a Interface")
            self._patch_subinterface(key, subiface)
            setattr(self, key, subiface)

    def print_doc(self, indent=2):
        """Basic pretty print of object document."""

        json.dumps(self.get_doc(), indent)

    def set_item(self, key, value):
        """Update a single item by key."""

        setattr(self, key, value)

    def update(self, d):
        """Update multiple items from a dict."""

        for k, v in d.items():
            self.set_item(k, v)


class ProxyInterface(Interface):
    """Interface which uses the backing Interface._store and key
    prefix support.
    """

    pass


class StructInterface(ProxyInterface):
    """Alias for ProxyInterface to clearly indicate Struct-style
    usage.
    """

    pass


class SuperInterface:
    """Base class to manage multiple interfaces."""

    def __init__(self):
        pass


def test(interface: Interface, name: str, value: Any):
    """Generic interface test function.

    Prints out test info. On error, any exceptions are caught and
    reported as messages. This function does not fail.

    Args:
        interface: Interface object.
        name: Identifier for value.
        value: Value to test interface.
    """

    try:
        print(f"interface ({interface})")
        print(f"codec ({getattr(interface.__class__, name).codec})")
        print(f"checker ({getattr(interface.__class__, name).checker})")
        print(f"name ({name})")

        # assign (would normally be <interface>.<name> = <value>)
        print(f"value ({value})")
        setattr(interface, name, value)

        # interface store
        encoded = interface._get(name)
        print(f"encoded type ({type(encoded)}) value ({encoded})")

        decoded = getattr(interface, name)
        print(f"decoded type ({type(decoded)}) value ({decoded})")

        print(f"match? ({decoded == value})")
    except Exception as e:
        print(f"exception e ({e})")

    print("-----")
