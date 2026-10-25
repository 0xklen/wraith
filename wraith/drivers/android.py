"""Android driver via adb.

Requirements:
  * `adb` on PATH (Android platform-tools)
  * a device with USB debugging enabled, or `adb connect <ip>:5555`
"""
import re
import subprocess

from .base import DeviceDriver

KEYCODES = {
    'back': '4',
    'home': '3',
    'enter': '66',
    'power': '26',
    'volume_up': '24',
    'volume_down': '25',
    'tab': '61',
    'escape': '111',
}


class AndroidDriver(DeviceDriver):
    name = 'android'

    def __init__(self, serial=None):
        self.serial = serial

    def _adb(self, *args):
        cmd = ['adb']
        if self.serial:
            cmd += ['-s', self.serial]
        return list(cmd) + list(args)

    def size(self):
        r = subprocess.run(self._adb('shell', 'wm', 'size'), capture_output=True)
        m = re.search(rb'(\d+)x(\d+)', r.stdout)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)

    def screenshot(self):
        r = subprocess.run(self._adb('exec-out', 'screencap', '-p'), capture_output=True)
        return r.stdout

    def tap(self, x, y):
        subprocess.run(self._adb('shell', 'input', 'tap', str(int(x)), str(int(y))))

    def long_press(self, x, y, ms=800):
        subprocess.run(self._adb('shell', 'input', 'swipe',
                                 str(int(x)), str(int(y)), str(int(x)), str(int(y)), str(ms)))

    def swipe(self, x1, y1, x2, y2, ms=300):
        subprocess.run(self._adb('shell', 'input', 'swipe',
                                 str(int(x1)), str(int(y1)), str(int(x2)), str(int(y2)), str(ms)))

    def type_text(self, text):
        # adb `input text` treats spaces specially
        subprocess.run(self._adb('shell', 'input', 'text', text.replace(' ', '%s')))

    def key(self, code):
        subprocess.run(self._adb('shell', 'input', 'keyevent', KEYCODES.get(code, code)))

    def open_app(self, app):
        subprocess.run(self._adb('shell', 'monkey', '-p', app,
                                 '-c', 'android.intent.category.LAUNCHER', '1'))
