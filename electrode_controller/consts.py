# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

# Plugin offers services that are executed on publishing to this topic
ELECTRODE_STATE_CHANGE = "dropbot/requests/start_device_monitoring"