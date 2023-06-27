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

import pytest
import unittest

import argparse

from bittensor_config import Config, config

class TestConfig(unittest.TestCase):

    def test_loaded_config(self):
        # This is not implemented, so should raise an exception
        with pytest.raises(NotImplementedError):
            Config(loaded_config=True)

    def test_strict(self):
        # Create dummy parser
        parser = argparse.ArgumentParser()

        # Positional/mandatory arguments don't play nice with multiprocessing.
        # When the CLI is used, the argument is just the 0th element or the filepath.
        # However with multiprocessing this function call actually comes from a subprocess, and so there
        # is no positional argument and this raises an exception when we try to parse the args later.
        # parser.add_argument("arg", help="Dummy Args")
        parser.add_argument("--cov", help="Dummy Args")
        parser.add_argument("--cov-append", action='store_true', help="Dummy Args")
        parser.add_argument("--cov-config",  help="Dummy Args")

        correct_args = ["--cov", "test", "--cov-append", "--cov-config", "test"]
        incorrect_args = ["--cov", "test", "--this-arg-does-not-exist", "test"]

        # Correct args should not raise an exception with strict as True or False
        config( parser, strict=False, args=correct_args )
        config( parser, strict=True, args=correct_args )
        # Should also be strict if we use --strict flag, with or without strict=True
        config( parser, strict=False, args=correct_args + ["--strict"] )

        # Incorrect args should raise an exception with strict=True, but not strict=False
        config( parser, strict=False, args=incorrect_args )

        ## Should exit with SystemExit because of incorrect args
        with pytest.raises(SystemExit, match="2"):
            config( parser, strict=True, args=incorrect_args )

        ## Try using --strict flag, should still raise an exception
        with pytest.raises(SystemExit):
            config( parser, strict=False, args=incorrect_args + ["--strict"] )

        with pytest.raises(SystemExit):
            config( parser, strict=True, args=incorrect_args + ["--strict"] )

        
if __name__ == "__main__":
    unittest.main()
