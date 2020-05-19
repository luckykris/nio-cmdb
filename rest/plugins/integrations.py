#from django.conf import settings
settings = {'PLUGIN_DIR': '/Users/googlegu/codes/nio-cmdb/rest/plugin_dir'}
import importlib
import os
import sys


class ProxyPlugin:
    def __init__(self):
        self.plugin_path = settings.get('PLUGIN_DIR', '')

    def get_plugin(self, plugin_name):
        path = os.path.join(self.plugin_path)
        sys.path.append(path)
        m = importlib.import_module(plugin_name)
        return m


if __name__ == '__main__':
    a = ProxyPlugin()
    v = a.get_plugin('clickhouse')
