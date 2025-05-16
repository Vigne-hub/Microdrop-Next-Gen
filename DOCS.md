# Application Components

### Message Router

The Message Router (found in message_router), Plugin A and B are all Envisage plugins.

When MessageRouterPlugin is loaded, it creates a new  MessageRouterActor (found in microdrop_utils/dramatiq_pub_sub_helpers), which creates a MessageRouterData with a static random queue number (since its not referenced anywhere else im

It then listens on that queue and for every (message, topic) pair it receives and propagates the messages to every subscriber to the topic. The idea is to hack dramatiq into a full pub/sub system, which does not support broadcast messages otherwise.

MessageRouterData keeps track of all of the pub/sub info, and provides the relavent methods to publish/listen

An example of how it works can be found in /examples/tests/tests_with_redis_server_need/test_message_router.py

# Files/Folders

## /microdrop

Deprecated/Not Needed, accorinding to Vignesh

## /examples

Lots of run scripts for various components of the application.

### /examples/run_demo_dramatiq_pluggable.py

A simple demo that demonstrates Envisage services (using toy examples in /examples/toy_plugins) and dramatiq task dispatch/receiving. Useful for a full example of all imports/setup required.

### /examples/dropbot_device_monitering_aps_dramatiq_scheduled.py

Imports functions from /microdrop_utils/broker_server_helpers.py that no longer exist. Is not imported anywhere so can safely be ignored.

### /examples/run_device_viewer_pluggable_dropbot_service_demo.py

Requires dropbot to be plugged in to operate.

## /examples/run_device_viewer_pluggable_backend.py



# Plugins

## /dropbot_controller

## /dropbot_status

## /dropbot_status_plot

## /dropbot_tools_menu

## /electrode_controller

## /manual_controls

## /device_viewer

## /BlankMicrodropCanvas

# Tests

Most tests can be found in /examples/tests/. There are additional tests scattered around:
- /electrode_controller/tests

# Conda

### To create environment

```
conda env create -f environment.yml
```
### To delete environment

```
conda env remove -n microdrop --all
```