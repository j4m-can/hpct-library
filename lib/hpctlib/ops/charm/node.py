# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
#
# hpctlib/ops/charm/node.py


"""Provides the Node class (built on ServiceCharm) which acts as a
principal charm for a "node".
"""


import logging
import time

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus, WaitingStatus

from ...misc import get_methodname, get_timestamp, log_enter_exit
from .service import ServiceCharm

logger = logging.getLogger(__name__)


class NodeCharm(ServiceCharm):
    """Provide support for nodes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        # self.framework.observe(self.on.start, self._on_start)
        # self.framework.observe(self.on.stop, self._on_stop)
        self.framework.observe(self.on.update_status, self._on_update_status)

        # self.service_init_sync_status(key, boolean)

        self.required_syncs = []

    #
    # registered handlers
    #
    # Note: These methods should *not* be called directly.
    #

    @log_enter_exit()
    def _on_config_changed(self, event):
        """'on-config-changed' handler.

        Note: Do not override.
        """

        self._service_on_config_changed(event)
        self.service_set_updated("config")
        self.service_update_status()

    @log_enter_exit()
    def _on_start(self, event):
        """'start' handler.

        Note: Do not override.
        """

        self.service_enable(event)
        self.service_start(event)

    @log_enter_exit()
    def _on_stop(self, event):
        """'stop' handler.

        Note: Do not override.
        """

        self.service_stop(event)
        self.service_disable(event)
        self.service_update_status()

    @log_enter_exit()
    def _on_update_status(self, event):
        """'update-status' handler.

        Note: Do not override.
        """
        self.service_update_status()

    #
    # May be overriden
    #
    # Note: These methods should *not* be called directly. Instead,
    #   call the service_* methods.
    #

    @log_enter_exit()
    def _service_start(self, event):
        """Start service.

        Called by service_start().
        """

        pass

    @log_enter_exit()
    def _service_stop(self, event, force):
        """Stop service.

        Called by service_stop().
        """

        pass

    @log_enter_exit()
    def _service_sync(self, event, force=False):
        """Sync all.

        Called by service_sync().
        """

        pass

    @log_enter_exit()
    def service_update_status(self):
        """Update status.

        Note: Do not override.
        """

        state = self.service_get_state()
        if state in ["broken"]:
            cls = BlockedStatus
        elif state in ["idle", "enabled"]:
            cls = MaintenanceStatus
        elif state in ["waiting"]:
            cls = WaitingStatus
        elif state in ["started"]:
            cls = ActiveStatus
        else:
            cls = MaintenanceStatus

        # TODO: allow for tailoring of status message

        if 1:
            status_message = self._service_store.status_message
            syncs = self.service_get_syncs()
            nsynced = len([v for v in syncs.values() if v])
            nsyncs = len(syncs)

            msg = f" ({status_message})" if status_message != None else ""

            self.unit.status = cls(
                f"updated ({tuple(self.service_get_updated())})"
                f"{msg}"
                f" stale ({self.service_get_stale()})"
                f" state ({self.service_get_state()})"
                f" synced ({nsynced}/{nsyncs})"
                f" syncs ({syncs})"
            )

        elif 0:
            self.unit.status = cls(
                f"updated ({self.service_get_updated()})"
                f" ({status_message})"
                f"{msg}"
                f" stale ({self.service_get_stale()})"
                f" state ({self.service_get_state()})"
                f" synced ({self.service_is_synced()})"
                f" syncs ({self.service_get_syncs()})"
            )
