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

"""
Supervisor for the renderer processes.
"""

import logging

from tornado.options import options

from apollo.server.component import Component
from apollo.server.render.renderer import Renderer

from multiprocessing import Pool, Process

workerData = {}
"""
Worker data dictionary. Because ``multiprocessing.pool`` does not have a more
sensible place to store data, we can just throw it here.
"""

class RendererSupervisor(object):
    def go(self):
        self.pool = Pool(
            processes=options.render_process_num,
            initializer=self.initializeRenderer
        )
        logging.info("Started renderer supervisor with %d processes" % options.render_process_num)

    def initializeRenderer(self):
        """
        Initialize the renderer for a process.
        """
        workerData["renderer"] = Renderer()

    def renderChunk(self, chunk_id, callback=None):
        callback = callback or (lambda: None)
        self.pool.apply_async(self._renderChunk, callback=callback)

    def _renderChunk(self, chunk_id):
        workerData["renderer"].render(chunk_id)
