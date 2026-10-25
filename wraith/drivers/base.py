"""Device driver interface.

A driver is one way to control a phone:
  * AndroidDriver — `adb` (USB or `adb connect <ip>`)
  * IOSDriver     — Appium + WebDriverAgent
  * SimDriver     — a local fake device (no phone needed, for testing)

Every driver implements the same methods, so the agent loop is backend-agnostic.
"""


class DeviceDriver:
    name = 'base'

    def size(self):
        """Screen size as (width, height) in pixels."""
        raise NotImplementedError

    def screenshot(self):
        """Return a PNG screenshot as bytes."""
        raise NotImplementedError

    def tap(self, x, y):
        raise NotImplementedError

    def long_press(self, x, y, ms=800):
        raise NotImplementedError

    def swipe(self, x1, y1, x2, y2, ms=300):
        raise NotImplementedError

    def type_text(self, text):
        raise NotImplementedError

    def key(self, code):
        """Press a navigation key: back, home, enter, power, ..."""
        raise NotImplementedError

    def open_app(self, app):
        """Open an app by its package id (Android) or bundle id (iOS)."""
        raise NotImplementedError

    def close(self):
        pass
