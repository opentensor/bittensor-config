# The MIT License (MIT)
# Copyright © 2021 Yuma Rao
# Copyright © 2022 Opentensor Foundation
# Copyright © 2023 Opentensor Technologies

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

__version__ = "0.0.1"

import os
import sys
import argparse
from typing import List, Optional
from copy import deepcopy

import yaml
from .config_impl import Config as Config, DefaultConfig as DefaultConfig


class InvalidConfigFile(Exception):
    """ In place of YAMLError
    """
    pass

class config:
    """
    Create and init the config class, which manages the config of different bittensor modules.
    """

    def __new__( cls, parser: argparse.ArgumentParser = None, strict: bool = False, args: Optional[List[str]] = None ) -> config_impl.Config:
        r""" Translates the passed parser into a nested Bittensor config.
        Args:
            parser (argparse.ArgumentParser):
                Command line parser object.
            strict (bool):
                If true, the command line arguments are strictly parsed.
            args (list of str):
                Command line arguments.
        Returns:
            config (config_impl.Config):
                Nested config object created from parser arguments.
        """
        if parser == None:
            return config_impl.Config()

        # Optionally add config specific arguments
        try:
            parser.add_argument('--config', type=str, help='If set, defaults are overridden by passed file.')
        except:
            # this can fail if the --config has already been added.
            pass
        try:
            parser.add_argument('--strict',  action='store_true', help='''If flagged, config will check that only exact arguemnts have been set.''', default=False )
        except:
            # this can fail if the --config has already been added.
            pass

        # Get args from argv if not passed in.
        if args == None:
            args = sys.argv[1:]

        # 1.1 Optionally load defaults if the --config is set.
        try:
            config_file_path = str(os.getcwd()) + '/' + vars(parser.parse_known_args(args)[0])['config']
        except Exception as e:
            config_file_path = None
        
        # Parse args not strict
        config_params = cls.__parse_args__(args=args, parser=parser, strict=False)

        # 2. Optionally check for --strict
        ## strict=True when passed in OR when --strict is set
        strict = config_params.strict or strict

        if config_file_path != None:
            config_file_path = os.path.expanduser(config_file_path)
            try:
                with open(config_file_path) as f:
                    params_config = yaml.safe_load(f)
                    print('Loading config defaults from: {}'.format(config_file_path))
                    parser.set_defaults(**params_config)
            except Exception as e:
                print('Error in loading: {} using default parser settings'.format(e))

        # 2. Continue with loading in params.
        params = cls.__parse_args__(args=args, parser=parser, strict=strict)

        _config = config_impl.Config()

        # Splits params and add to config
        cls.__split_params__(params=params, _config=_config)

        # Make the is_set map
        _config['__is_set'] = {}

        ## Reparse args using default of unset
        parser_no_defaults = deepcopy(parser)
        ## Get all args by name
        default_params = parser.parse_args(
                args=[_config.get('command')] # Only command as the arg, else no args
                    if _config.get('command') != None
                    else []
        )
        all_default_args = default_params.__dict__.keys() | []
        ## Make a dict with keys as args and values as argparse.SUPPRESS
        defaults_as_suppress = {
            key: argparse.SUPPRESS for key in all_default_args
        }
        ## Set the defaults to argparse.SUPPRESS, should remove them from the namespace
        parser_no_defaults.set_defaults(**defaults_as_suppress)
        parser_no_defaults._defaults.clear() # Needed for quirk of argparse

        ### Check for subparsers and do the same
        if parser_no_defaults._subparsers != None:
            for action in parser_no_defaults._subparsers._actions:
                # Should only be the "command" subparser action
                if isinstance(action, argparse._SubParsersAction):
                    # Set the defaults to argparse.SUPPRESS, should remove them from the namespace
                    # Each choice is the keyword for a command, we need to set the defaults for each of these
                    ## Note: we also need to clear the _defaults dict for each, this is a quirk of argparse
                    cmd_parser: argparse.ArgumentParser
                    for cmd_parser in action.choices.values():
                        cmd_parser.set_defaults(**defaults_as_suppress)
                        cmd_parser._defaults.clear() # Needed for quirk of argparse
                
        ## Reparse the args, but this time with the defaults as argparse.SUPPRESS
        params_no_defaults = cls.__parse_args__(args=args, parser=parser_no_defaults, strict=strict)

        ## Diff the params and params_no_defaults to get the is_set map
        _config['__is_set'] = {
            arg_key: True 
                for arg_key in [k for k, _ in filter(lambda kv: kv[1] != argparse.SUPPRESS, params_no_defaults.__dict__.items())]
        }

        return _config
    
    @staticmethod
    def __split_params__(params: argparse.Namespace, _config: config_impl.Config):
        # Splits params on dot syntax i.e neuron.axon_port and adds to _config
        for arg_key, arg_val in params.__dict__.items():
            split_keys = arg_key.split('.')
            head = _config
            keys = split_keys
            while len(keys) > 1:
                if hasattr(head, keys[0]) and head[keys[0]] != None: # Needs to be Config
                    head = getattr(head, keys[0])
                    keys = keys[1:]
                else:
                    head[keys[0]] = config_impl.Config()
                    head = head[keys[0]]
                    keys = keys[1:]
            if len(keys) == 1:
                head[keys[0]] = arg_val

    @staticmethod
    def __parse_args__( args: List[str], parser: argparse.ArgumentParser = None, strict: bool = False) -> argparse.Namespace:
        """Parses the passed args use the passed parser.
        Args:
            args (List[str]):
                List of arguments to parse.
            parser (argparse.ArgumentParser):
                Command line parser object.
            strict (bool):
                If true, the command line arguments are strictly parsed.
        Returns:
            Namespace:
                Namespace object created from parser arguments.
        """
        if not strict:
            params = parser.parse_known_args(args=args)[0]
        else:
            params = parser.parse_args(args=args)

        return params
