import os
import argparse


def set_service_by_env_values():
    name = os.environ.get('SERVICE_NAME')
    mode = os.environ.get('SERVICE_MODE')
    if name == None:
        raise Exception('Environment SERVICE_NAME is not set.')
    read = None
    if mode == 'sim':
        from adapter.petra.TineSimAdapter import TineSimReader
        read = TineSimReader.create_for_petra()
    elif mode == 'prod':
        from adapter.petra.TineAdapter import TineReader
        read = TineReader()
    else:
        raise Exception('Environment SERVICE_MODE have to set to "sim" or "prod".')
    return name, read, mode


def set_adapter_by_arg_parser():
    parser = argparse.ArgumentParser(description='Short sample app')
    parser.add_argument('--mode', help="mode can be 'prod' or 'sim'")
    options = parser.parse_args()
    read = None

    if options.mode == 'sim':
        from adapter.petra.TineSimAdapter import TineSimReader
        read = TineSimReader.create_for_petra()
    elif options.mode == 'prod':
        from adapter.petra.TineAdapter import TineReader
        read = TineReader()
    else:
        raise Exception("Argument --mode isn't set. Possible values are 'prod' for production or 'sim' for simulation")
    return read, options.mode
