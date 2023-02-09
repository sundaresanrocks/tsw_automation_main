__author__ = 'M'
import os
import sys
import unittest
import importlib


class TestConfigUtilsGetEnvVars(unittest.TestCase):
    """Config Utils related unit tests"""

    def setUp(self):
        """Reset environment vars and unload framework.config_utils"""
        if 'framework.config_utils' in sys.modules:
            del sys.modules['framework.config_utils']
        os.environ['__INTERNAL_CONFIG_UTILS_LOADED'] = ''

    def test_import(self):
        """Load the module"""
        import framework.config_utils

    def test_reload(self):
        """Realoding the module must throw ImportError"""
        #time.sleep(1)
        import framework.config_utils
        try:
            importlib.reload(framework.config_utils)
        except ImportError as err:
            if 'This module, config_utils can be loaded only once!' not in str(err):
                raise

    def test_prop_file_not_found(self):
        """Check error message for non existing properties file"""
        os.environ['USE_PROPERTIES_FILE_AS_ENV_VAR'] = ''
        import framework.config_utils
        framework.config_utils.PROPERTIES_FILE = 'res/non-existing-file.properties'
        with self.assertRaises(IOError):
            framework.config_utils.get_required_environment_vars()

    def test_env_vars_correct_value(self):
        """Write test here"""
        os.environ['ARBITRARY_REQ_VAR'] = 'ARBITRARY VALUE'
        os.environ['USE_PROPERTIES_FILE_AS_ENV_VAR'] = 'FALSE'

        import framework.config_utils
        #print (framework.config_utils.USE_PROP_FILE)
        framework.config_utils.REQUIRED_ENV_VARS = ['ARBITRARY_REQ_VAR']

        env_dict = framework.config_utils.get_required_environment_vars()
        if 'ARBITRARY_REQ_VAR' not in env_dict:
            raise EnvironmentError('Unable to read ARBITRARY_REQ_VAR from settings file ')
        self.assertEquals(env_dict['ARBITRARY_REQ_VAR'], 'ARBITRARY VALUE', 'Value Mismatch')

    def test_env_vars_missing_key(self):
        """Write test here"""
        os.environ['ARBITRARY_REQ_VAR'] = 'ARBITRARY VALUE'
        os.environ['USE_PROPERTIES_FILE_AS_ENV_VAR'] = 'FALSE'

        import framework.config_utils
        #print (framework.config_utils.USE_PROP_FILE)
        framework.config_utils.REQUIRED_ENV_VARS = ['ARBITRARY_REQ_VAR', 'ARBITRARY_NOT_FOUND_VAR']
        with self.assertRaisesRegex(EnvironmentError, 'Unable to read environment variables - ARBITRARY_NOT_FOUND_VAR'):
            framework.config_utils.get_required_environment_vars()

    def test_env_from_file(self):
        """Load environment from file - correct value"""
        os.environ['USE_PROPERTIES_FILE_AS_ENV_VAR'] = 'True'
        import framework.config_utils
        framework.config_utils.PROPERTIES_FILE = 'res/arbitary-req-var.properties'
        framework.config_utils.REQUIRED_ENV_VARS = ['ARBITRARY_REQ_VAR']

        env_dict = framework.config_utils.get_required_environment_vars()
        if 'ARBITRARY_REQ_VAR' not in env_dict:
            raise EnvironmentError('Unable to read ARBITRARY_REQ_VAR from settings file ')
        self.assertEquals(env_dict['ARBITRARY_REQ_VAR'], 'ARBITRARY VALUE', 'Value Mismatch')

    def test_env_from_file_missing_key(self):
        """Missing required value from file"""
        os.environ['USE_PROPERTIES_FILE_AS_ENV_VAR'] = 'True'
        os.environ['ARBITRARY_REQ_VAR'] = 'ARBITRARY_VALUE'
        import framework.config_utils
        framework.config_utils.PROPERTIES_FILE = 'res/arbitary-req-var.properties'
        framework.config_utils.REQUIRED_ENV_VARS = ['ARBITRARY_REQ_VAR', 'ARBITRARY_NOT_FOUND_VAR']
        with self.assertRaisesRegex(EnvironmentError, 'Missing environment variables'):
            framework.config_utils.get_required_environment_vars()


if __name__ == '__main__':
    unittest.main()