#
# Copyright (C) 2011 by Tony Young
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

from tornado.options import options

from apollo.server.component import Component
from apollo.server.util.importlib import import_module

class PluginRegistry(Component):
    def __init__(self, core):
        super(PluginRegistry, self).__init__(core)
        self.plugins = {}

    def loadPluginsFromOptions(self):
        for plugin in options.plugins:
            if not self.isPluginLoaded(plugin):
                self.loadPlugin(plugin)
        logging.info("Loaded %d plugins." % len(self.plugins))

    def loadPlugin(self, plugin_name):
        try:
            plugin = import_module(plugin_name)
        except ImportError:
            logging.error("Failed to load plugin: %s" % plugin_name)
            return

        if hasattr(plugin, "depends"):
            for dep in plugin.depends:
                if not self.isPluginLoaded(dep):
                    self.loadPlugin(dep)

        self.plugins[plugin_name] = plugin

        if hasattr(plugin, "setup"):
            plugin.setup(self.core)

    def isPluginLoaded(self, plugin_name):
        return plugin_name in self.plugins
