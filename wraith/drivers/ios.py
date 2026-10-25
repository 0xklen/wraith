"""iOS driver via Appium + WebDriverAgent.

Requirements:
  * a running Appium server (default http://127.0.0.1:4723)
  * WebDriverAgent installed and running on the device (or simulator)
  * `pip install -r requirements-ios.txt`
"""
import base64

from .base import DeviceDriver


class IOSDriver(DeviceDriver):
    name = 'ios'

    def __init__(self, appium_url='http://127.0.0.1:4723', caps=None):
        self.appium_url = appium_url
        self.caps = caps or {}
        self._driver = None

    def _d(self):
        if self._driver is None:
            from appium import webdriver
            from appium.options.ios import XCUITestOptions
            opts = XCUITestOptions()
            for k, v in self.caps.items():
                opts.set_capability(k, v)
            self._driver = webdriver.Remote(self.appium_url, options=opts)
        return self._driver

    def size(self):
        s = self._d().get_window_size()
        return (s['width'], s['height'])

    def screenshot(self):
        return base64.b64decode(self._d().get_screenshot_as_base64())

    def tap(self, x, y):
        self._d().tap([(int(x), int(y))])

    def long_press(self, x, y, ms=800):
        self._d().execute_script('mobile: touchAndHold',
                                 {'x': int(x), 'y': int(y), 'duration': ms / 1000.0})

    def swipe(self, x1, y1, x2, y2, ms=300):
        self._d().swipe(int(x1), int(y1), int(x2), int(y2), ms)

    def type_text(self, text):
        self._d().send_keys(text)

    def key(self, code):
        d = self._d()
        if code == 'home':
            d.execute_script('mobile: pressButton', {'name': 'home'})
        elif code == 'back':
            # iOS has no global back; swipe-from-edge is app-specific.
            w, h = self.size()
            d.swipe(5, h // 2, w // 2, h // 2, 200)
        elif code == 'enter':
            d.send_keys('\n')

    def open_app(self, app):
        self._d().activate_app(app)
