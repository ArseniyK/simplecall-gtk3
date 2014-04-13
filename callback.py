import pjsua
from gi.repository import GObject

class AccountCallback(pjsua.AccountCallback, GObject.GObject):
    __gsignals__ = {
        'register': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        'incoming': (GObject.SIGNAL_RUN_FIRST, None, (object,))
    }

    def __init__(self, account=None):
        GObject.GObject.__init__(self)
        pjsua.AccountCallback.__init__(self, account)

    def on_reg_state(self):
        self.emit('register', self.account.info().reg_status)

    def on_incoming_call(self, call):
        print type(call)
        self.emit('incoming', call)


class CallCallback(pjsua.CallCallback, GObject.GObject):
    __gsignals__ = {
        'state': (GObject.SIGNAL_RUN_FIRST, None, (int,))
    }

    def __init__(self, call=None):
        GObject.GObject.__init__(self)
        pjsua.CallCallback.__init__(self, call)

    def on_state(self):
        self.emit('state', self.call.info().state)

