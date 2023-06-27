"""
Implementation of the config class, which manages the config of different bittensor modules.
"""
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

import yaml
from munch import DefaultMunch
from typing import Dict, Any, Optional, TypeVar, Type
from copy import deepcopy

class Config ( DefaultMunch ):
    """
    Implementation of the config class, which manages the config of different bittensor modules.
    """
    __is_set: Dict[str, bool]

    """
    Args:
        default (Optional[Any]):
            Default value for the Config. Defaults to None.
            This default will be returned for attributes that are undefined.
    """
    def __init__(self, loaded_config = None, default: Optional[Any] = None ):
        super().__init__(default)
        if loaded_config:
            raise NotImplementedError('Function load_from_relative_path is not fully implemented.')
        
        self['__is_set'] = {}

    def __deepcopy__(self, memo) -> 'Config':
        _default = self.__default__
        
        config_state = self.__getstate__()
        config_copy = Config()
        memo[id(self)] = config_copy

        config_copy.__setstate__(config_state)
        config_copy.__default__ = _default
    
        config_copy['__is_set'] = deepcopy(self['__is_set'], memo)
        
        return config_copy
        
    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        config_dict = self.toDict()
        config_dict.pop("__is_set")
        return "\n" + yaml.dump(config_dict)

    def to_string(self, items) -> str:
        """ Get string from items
        """
        return "\n" + yaml.dump(items.toDict())

    def update_with_kwargs( self, kwargs ):
        """ Add config to self
        """
        for key,val in kwargs.items():
            self[key] = val

    @classmethod
    def _merge( cls, a, b ):
        """Merge two configurations recursively.
        If there is a conflict, the value from the second configuration will take precedence.
        """
        for key in b:
            if key in a:
                if isinstance( a[key], dict ) and isinstance( b[key], dict ):
                    a[key] = cls._merge( a[key], b[key] )
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a

    def merge(self, b):
        """ Merge two configs
        """
        self = self._merge( self, b )

    def is_set(self, param_name: str) -> bool:
        """
        Returns a boolean indicating whether the parameter has been set or is still the default.
        """
        if param_name not in self.get('__is_set'):
            return False
        else:
            return self.get('__is_set')[param_name]


T = TypeVar('T', bound='DefaultConfig')

class DefaultConfig( Config ):
    """
    A Config with a set of default values.
    """
    
    @classmethod
    def default(cls: Type[T]) -> T:
        """
        Get default config.
        """
        raise NotImplementedError('Function default is not implemented.')