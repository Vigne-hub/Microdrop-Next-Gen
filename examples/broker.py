from dramatiq import get_broker

BROKER = get_broker()

# remove prometheus metrics for now
for el in BROKER.middleware:
    if el.__module__ == "dramatiq.middleware.prometheus":
        BROKER.middleware.remove(el)