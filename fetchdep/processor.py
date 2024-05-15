# -*- coding: utf-8 -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright fetchdep

from fetchdep.config import find_configuration
from fetchdep.fetch import FetchOptions
from fetchdep.util.io import redirect_output
from fetchdep.util.log import fetchdep_log_configuration
from fetchdep.util.log import log
from multiprocessing import Event
from multiprocessing import Lock
from multiprocessing import Queue
from multiprocessing import Value
import os
import signal
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class ProcessState:
    def __init__(self):
        self.detected = Queue()
        self.failure = Value('b', False)  # noqa: FBT003
        self.log_debug = False
        self.log_nocolor = False
        self.log_verbose = False
        self.stderr = None
        self.stdout = None
        self.msgs = Queue()
        self.mtx = Lock()
        self.pending = Value('i', 0)
        self.signal = Event()

    def queued(self):
        with self.mtx:
            self.pending.value += 1

    def complete(self, result):
        with self.mtx:
            # share information back to parent (if any)
            self.detected.put(result)
            self.pending.value -= 1

        # notify that a specific dependency has completed its work
        self.signal.set()

    def msg(self, message):
        self.msgs.put(message)

    def failed(self):
        with self.mtx:
            # indicate we have had an issue
            self.failure.value = True
            self.pending.value -= 1

        # notify that a specific dependency has completed its work
        self.signal.set()

    def wait(self):
        while True:
            # wait for a dependency to be processed
            self.signal.wait()

            # dump any messages generates from the process
            while not self.msgs.empty():
                print(self.msgs.get_nowait())

            with self.mtx:
                # return a new dependency (if any)
                while not self.detected.empty():
                    new_dep = self.detected.get_nowait()
                    if new_dep:
                        return new_dep

                # if no more dependencies to be fetched or a failure has been
                # detected, we are done waiting
                if self.pending.value <= 0 or self.failure.value:
                    return None


def process_initialization(state):
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    global process_state
    process_state = state

    fetchdep_log_configuration(
        state.log_debug, state.log_nocolor, state.log_verbose)


def process(req, opts):
    fetch_opts = FetchOptions()
    fetch_opts.name = req.dep.name
    fetch_opts.site = req.dep.site
    fetch_opts.target_dir = req.target_dir

    new_target = StringIO()
    try:
        # if we are unit testing, capture all multiprocessing output into
        # a buffer to be relayed back to the root tool; this is a crude way
        # to avoid prints during unit testing -- most likely should have a
        # proper multi-processing log management, but for now, normal use
        # just "competes" on stderr/stdout
        if os.getenv('TOX_INI_DIR') and not os.getenv('FETCHDEP_NO_TCACHE'):
            sys.stderr = new_target
            sys.stdout = new_target

        if opts.dry_run:
            log('[dry-run] perform fetch of site ({}: {}): {}',
                req.dep.name, req.dep.vcs, req.dep.site)
            fetched = True
        elif opts.parallel > 1:
            with process_state.mtx:
                log('[parallel] started: {}', req.dep.name)

            with redirect_output() as stream:
                fetched = req.fetcher(fetch_opts)

            with process_state.mtx:
                log('[parallel] output: {}', req.dep.name)
                log(stream.getvalue())
        else:
            fetched = req.fetcher(fetch_opts)

        if fetched:
            cfg = None
            if opts.recursive and req.dep.recursive:
                cfg = find_configuration(req.target_dir)

            process_state.complete(cfg)
        else:
            process_state.failed()
    finally:
        messages = new_target.getvalue()
        if messages:
            process_state.msg(messages)
