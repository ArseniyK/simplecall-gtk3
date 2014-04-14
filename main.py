import pjsua
from gi.repository import Gtk, GObject
from settings import Settings
from callback import AccountCallback, CallCallback

class Simplecall:
    def __init__(self):
        self.tray = Gtk.StatusIcon()
        self.tray.set_from_stock(Gtk.STOCK_NO)
        self.tray.connect('popup-menu', self.on_right_click)
        self.tray.set_visible(True)
        self.pj = pjsua.Lib()
        self.pj.init()
        self.call = None
        self.acc = None
        self.settings = Settings(self.pj.enum_snd_dev())

        self.dialer = Gtk.Window()
        self.dialer.set_size_request(300, 50)
        self.dialer.set_border_width(10)
        self.dialer.connect('delete-event', lambda w, e: w.hide() or True)

        self.stack = Gtk.Stack()

        self.label = Gtk.Label()

        self.number_entry = Gtk.Entry()
        self.number_entry.connect('activate', self.make_call)

        self.call_button = Gtk.Button()
        self.call_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_YES, 2))
        self.call_button.set_always_show_image(True)
        self.call_button.set_relief(Gtk.ReliefStyle.NONE)
        self.call_button.connect('clicked', self.make_call)

        self.hungup_button = Gtk.Button()
        self.hungup_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_NO, 2))
        self.hungup_button.set_always_show_image(True)
        self.hungup_button.set_relief(Gtk.ReliefStyle.NONE)
        self.hungup_button.connect('clicked', self.hungup_call)

        self.answer_button = Gtk.Button()
        self.answer_button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_YES, 2))
        self.answer_button.set_always_show_image(True)
        self.answer_button.set_relief(Gtk.ReliefStyle.NONE)
        self.answer_button.connect('clicked', self.answer_call)

        self.dialer_box = Gtk.HBox()
        self.dialer_box.add(self.number_entry)
        self.dialer_box.add(self.call_button)

        self.call_box = Gtk.HBox()
        self.incoming_box = Gtk.HBox()

        self.stack.add_named(self.dialer_box, 'dialer')
        self.stack.add_named(self.call_box, 'call')
        self.incoming_box.add(self.label)
        self.incoming_box.add(self.answer_button)
        self.incoming_box.add(self.hungup_button)
        self.stack.add_named(self.incoming_box, 'incoming')

        self.dialer.add(self.stack)
        self._pj_start()
        GObject.timeout_add(1000, self.auto_reconnect)

    def auto_reconnect(self):
        if self.acc is None or self.acc.info().reg_status !=200:
            self._pj_reload()
        return True

    def switch_stack(self, name, text=None):
        if name == 'call':
            self.label.set_text(text)
            self.label.reparent(self.call_box)
            self.hungup_button.reparent(self.call_box)
        elif name=='incoming':
            self.label.set_text(text)
            self.label.reparent(self.incoming_box)
            self.answer_button.unparent()
            self.incoming_box.add(self.answer_button)
            self.hungup_button.reparent(self.incoming_box)

        self.stack.set_visible_child_name(name)

    def on_right_click(self, icon, event_button, event_time):
        self.make_menu(event_button, event_time)

    def make_menu(self, event_button, event_time):
        menu = Gtk.Menu()

        dialer = Gtk.MenuItem("Dialer")
        dialer.show()
        dialer.connect('activate', self.show_dialer)
        menu.append(dialer)

        settings = Gtk.MenuItem("Settings")
        settings.show()
        settings.connect('activate', self.show_settings)
        menu.append(settings)

        about = Gtk.MenuItem("About")
        about.show()
        about.connect('activate', self.show_about_dialog)
        menu.append(about)

        quit = Gtk.MenuItem("Quit")
        quit.show()
        quit.connect('activate', Gtk.main_quit)
        menu.append(quit)

        menu.popup(None, None, lambda w,x: self.tray.position_menu(menu, self.tray), self.tray, event_button, event_time)

    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()
        about_dialog.set_license_type(Gtk.License.GPL_2_0)
        about_dialog.set_destroy_with_parent (True)
        about_dialog.set_name('Simplecall')
        about_dialog.set_program_name('Simplecall')
        about_dialog.set_version('0.1')
        about_dialog.set_copyright("(C) 2014 Arseniy Krasnov")
        about_dialog.set_comments(("Gtk3 and PJSIP based minimalistic SIP Client "))
        about_dialog.set_authors(['Arseniy Krasnov <arseniy@krasnoff.org>'])
        about_dialog.run()
        about_dialog.destroy()

    def show_settings(self, widget):
        self.settings.show_all()
        response = self.settings.run()
        if response == Gtk.ResponseType.OK:
            if self.settings.changed:
                self.settings.save_settings()
                self.tray.set_from_stock(Gtk.STOCK_NO)
                GObject.idle_add(self._pj_reload)
                self.settings.hide()

        elif response == Gtk.ResponseType.CANCEL:
            self.settings.retrieve_settings()

    def show_dialer(self, widget):
        self.switch_stack('dialer')
        self.dialer.show_all()

    def _pj_reload(self):
        self._pj_stop()
        self.pj = pjsua.Lib()
        self.pj.init()
        self._pj_start()

    def _pj_start(self):
        try:
            self.transport = self.pj.create_transport(pjsua.TransportType.UDP, pjsua.TransportConfig(5070))
            self.pj.set_snd_dev(self.settings.config['capture'], self.settings.config['output'])
            self.pj.start()
            self.acc = self.pj.create_account(pjsua.AccountConfig(self.settings.config['server'], self.settings.config['login'], self.settings.config['password']))
            acc_cb = AccountCallback(self.acc)
            acc_cb.connect('register', self.register)
            acc_cb.connect('incoming', self.incoming)
            self.acc.set_callback(acc_cb)
        except:
            pass

    def _pj_stop(self):
        try:
            self.pj.hangup_all()
            if self.acc is not None:
                self.acc.delete()
            if self.pj:
                self.pj.destroy()
            self.pj = None
        except:
            pass

    def register(self, widget, code):
        if code == 200:
            self.tray.set_from_stock(Gtk.STOCK_YES)
        else:
            self.tray.set_from_stock(Gtk.STOCK_NO)

    def incoming(self, widget, call):
        if self.call:
            call.answer(code=486)
            return
        self.call= call
        call_cb = CallCallback(self.call)
        call_cb.connect('state', self.on_state)
        self.call.set_callback(call_cb)
        self.switch_stack('incoming', self.call.info().uri)

    def make_call(self, widget):
        self.call = self.acc.make_call('sip:{0}@{1}'.format(self.number_entry.get_text(), self.settings.config['server']))
        call_cb = CallCallback(self.call)
        call_cb.connect('state', self.on_state)
        self.call.set_callback(call_cb)
        self.switch_stack('call', 'Calling {0}'.format(self.number_entry.get_text()))

    def hungup_call(self, widget):
        self.call.hangup()

    def answer_call(self, widget):
        self.call.answer()

    def on_state(self, widget, state):
        if state == pjsua.CallState.DISCONNECTED:
            self.switch_stack('dialer')
            self.call = None
        elif state == pjsua.CallState.CONNECTING:
            self.switch_stack('call', self.call.info().uri)
        elif state == pjsua.CallState.CONFIRMED:
            self.switch_stack('call', self.call.info().uri)

if __name__ == "__main__":
    sc = Simplecall()
    sc.show_dialer(None)

    Gtk.main()