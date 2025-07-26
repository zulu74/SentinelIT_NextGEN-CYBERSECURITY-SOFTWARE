# sentinelitgui.py – Rebuilt Interface

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
import threading
import os

from sentinelIT.Eventlogger import log_event
from schedule import schedule_compliance_check

Window.size = (900, 600)

class SentinelPanel(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.build_tabs()

    def build_tabs(self):
        self.add_widget(self.build_dashboard_tab())
        self.add_widget(self.build_modules_tab())
        self.add_widget(self.build_logs_tab())
        self.add_widget(self.build_settings_tab())

    def build_dashboard_tab(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='[SentinelIT] Live System Dashboard', font_size=18))
        layout.add_widget(Label(text='System Status: ACTIVE', color=(0, 1, 0, 1)))
        layout.add_widget(Label(text='Security Events Logged: OK'))
        return self.create_tab(layout, 'Dashboard')

    def build_modules_tab(self):
        layout = GridLayout(cols=2, spacing=10, padding=10)
        modules = ['USB Monitor', 'Event Logger', 'SOC2 Audit', 'Live Status', 'Updater', 'FTP Watch']
        for mod in modules:
            btn = ToggleButton(text=mod, group='modules', size_hint=(1, None), height=40)
            layout.add_widget(btn)
        return self.create_tab(layout, 'Modules')

    def build_logs_tab(self):
        layout = BoxLayout(orientation='vertical')
        log_viewer = TextInput(readonly=True, font_size=12)
        try:
            with open('sentinel.log', 'r') as log_file:
                log_viewer.text = log_file.read()
        except:
            log_viewer.text = '[No logs found]'
        layout.add_widget(log_viewer)
        return self.create_tab(layout, 'Logs')

    def build_settings_tab(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        btn_run_compliance = Button(text='Run Compliance Check')
        btn_run_compliance.bind(on_press=self.run_compliance)
        layout.add_widget(btn_run_compliance)
        return self.create_tab(layout, 'Settings')

    def create_tab(self, content, title):
        panel = BoxLayout(orientation='vertical')
        panel.add_widget(content)
        panel.text = title
        return panel

    def run_compliance(self, instance):
        threading.Thread(target=schedule_compliance_check).start()
        self.popup_msg("Compliance check scheduled.")
        log_event("gui", "User triggered compliance check from GUI")

    def popup_msg(self, message):
        popup = Popup(title='SentinelIT', content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

class SentinelGUI(App):
    def build(self):
        self.title = 'SentinelIT Interface'
        return SentinelPanel()

if __name__ == '__main__':
    SentinelGUI().run()
