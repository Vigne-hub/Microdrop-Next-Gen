Plugins do not communicate with each other, all updates are dispatched by the message broker, so we only need to list the interactions between each component and the broker, namely what they send and what they receive.

Messages are sent via publish_message() from microdrop_utils/dramatiq_pub_sub_helpers.py.

They are received/handled using the format indicated by 

### manual_controls

Sending:
- SET_VOLTAGE
- SET_FREQUENCY

### electrode_controller

Receiving:
- SHORTS_DETECTED
- CAPACITANCE_UPDATED
- DISCONNECTED
- CHIP_NOT_INSERTED
- CHIP_INSERTED
- SHOW_WARNING
- NO_POWER

Sending:
- The plugin seems actually actuation via the proxy object instead of sending a message (see services/electrode_state_change_service.py)

### device_viewer

Receiving:
- SETUP_SUCCESS

Sending:
- ELECTRODES_STATE_CHANGE
- START_DEVICE_MONITORING

### dropbot_controller

Receiving:
- 
