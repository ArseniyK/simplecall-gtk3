import json
from gi.repository import Gtk

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

class Settings(Gtk.Dialog):

    def __init__(self, enum_snd_dev):
        Gtk.Dialog.__init__(self, "Settings", None, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.connect('delete-event', lambda w, e: self.retrieve_settings())

        self.config = {}
        self.changed = False
        self.set_size_request(200, 100)
        self.set_border_width(10)
        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        label = Gtk.Label('Server')
        self.server = Gtk.Entry()
        grid.attach(label, 0, 0, 1, 1)
        grid.attach_next_to(self.server, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label('Port')
        self.port = Gtk.Entry()
        grid.attach_next_to(label, self.server, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.port, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label('Login')
        self.login = Gtk.Entry()
        grid.attach(label, 0, 1, 1, 1)
        grid.attach_next_to(self.login, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label('Password')
        self.password = Gtk.Entry()
        self.password.set_visibility(False)
        grid.attach_next_to(label, self.login, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach_next_to(self.password, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label('Capture device')
        self.capture = Gtk.ComboBoxText()
        for device in enum_snd_dev:
            self.capture.append_text(device.name)
        grid.attach(label, 0, 2, 1, 1)
        grid.attach_next_to(self.capture, label, Gtk.PositionType.RIGHT, 1, 1)

        label = Gtk.Label('Output device')
        self.output = Gtk.ComboBoxText()
        for device in enum_snd_dev:
            self.output.append_text(device.name)
        grid.attach(label, 2, 2, 1, 1)
        grid.attach_next_to(self.output, label, Gtk.PositionType.RIGHT, 1, 1)

        self._load_settings()

        self.server.connect('changed', self._change)
        self.port.connect('changed', self._change)
        self.login.connect('changed', self._change)
        self.password.connect('changed', self._change)
        self.capture.connect('changed', self._change)
        self.output.connect('changed', self._change)
        box = self.get_content_area()
        box.add(grid)

    def _load_settings(self):
        self.config = _decode_dict(json.load(open('config.json')))

        self.server.set_text(self.config['server'])
        self.port.set_text(self.config['port'])
        self.login.set_text(self.config['login'])
        self.password.set_text(self.config['password'])
        self.capture.set_active(self.config['capture'])
        self.output.set_active(self.config['output'])

    def save_settings(self):
        self.config.update({'server': self.server.get_text(), 'port': self.port.get_text(),
                            'login': self.login.get_text(), 'password': self.password.get_text(),
                            'capture': self.capture.get_active(), 'output': self.output.get_active()})
        json.dump(self.config, open('config.json', 'w'))
        self.hide()

    def retrieve_settings(self):
        self._load_settings()
        self.hide()

    def _change(self, widget):
        self.changed = True




