# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])
PKG_name = PKG.title().replace("_", " ")

# Plugin offers services that are executed on publishing to this topic
ELECTRODES_STATE_CHANGE = 'dropbot/requests/electrodes_state_change'