from threading import Thread, Timer
import logging


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._ret = None

    def run(self):
        ret = self._target()
        if ret is not None:
            self._ret = ret

    def join(self):
        Thread.join(self)
        return self._ret


class RepeatedTimer(object):

    def __init__(self, interval, fun, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = fun
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
