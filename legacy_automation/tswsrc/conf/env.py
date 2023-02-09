"""
Environment Vars
****************
"""

__author__ = 'manoj'
import platform
import os

class ENV:
    env = {}
    # list of environment prefixes that will be exported
    _env_wildcard = ['SFDB', 'TSA', 'BUILD_', 'WORKSPACE']

    @classmethod
    def _create_shell_env(cls, wildcard=False):
        """return env vars of current shell"""

        new_env = os.environ.copy()
        new_env.update(cls.env)
        if wildcard:
            env_selected = {}
            for key, value in new_env.items():
                for item in cls._env_wildcard:
                    if key.startswith(item):
                        env_selected[key] = value
            return env_selected
        else:
            return new_env

    @classmethod
    def get_env_for_ssh_cmd(cls, wildcard=False):
        """Returns env vars in for bash"""
        string = ''
        env = cls._create_shell_env(wildcard=wildcard)
        for key, value in env.items():
            string += 'export %s="%s"; ' % (key, value)
        return string

    @classmethod
    def get_env_for_sub_process(cls, wildcard=False):
        """Returns env vars based on platform"""
        string = ''
        env = cls._create_shell_env(wildcard=wildcard)
        for key, value in env.items():
            if platform.system() == 'Windows':
                string += 'set %s="%s"; ' % (key, value)
            else:
                string += 'export %s="%s"; ' % (key, value)
        return string
