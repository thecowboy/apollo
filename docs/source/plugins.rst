Plugins
=======

Apollo has an extensible plugin framework, with a set of basic plugins that
facilitate writing more complex plugins (such as
``apollo.server.plugins.hooks``).

A plugin operating at a low level uses monkey-patching to hook into Apollo's
methods. This is what the ``apollo.server.plugins.hooks`` plugin achieves. A
utility class, ``apollo.server.plugins.PluginMonkey``, allows for rollbackable
monkey patching.
