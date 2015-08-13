import inspect
from ulmo import services


def list_providers():
    modules = inspect.getmembers(services, inspect.ismodule)
    return [name for name, _ in modules]


def list_services(provider, **kwargs):
    pass
    

def get_provider_metadata(provider):
    pass


def load_service(provider, service, **kwargs):
    provider = getattr(__import__('ulmo.services', globals(), locals(), [provider], -1), provider)
    return 