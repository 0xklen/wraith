"""Simulated device — a fake phone for exercising the agent loop with no
hardware and no LLM key. It records every action so tests can assert on them."""
import struct
import zlib

from .base import DeviceDriver


def _blank_png(w, h, rgb=(18, 18, 20)):
    def chunk(t, data):
        c = t + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    row = b'\x00' + bytes(rgb) * w
    idat = zlib.compress(row * h)
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', idat)
            + chunk(b'IEND', b''))


class SimDriver(DeviceDriver):
    name = 'sim'

    def __init__(self):
        self.taps = 0
        self.swipes = 0
        self.typed = ''
        self.actions = []

    def size(self):
        return (1080, 2400)

    def screenshot(self):
        return _blank_png(1080, 2400)

    def tap(self, x, y):
        self.taps += 1
        self.actions.append(('tap', x, y))

    def long_press(self, x, y, ms=800):
        self.taps += 1
        self.actions.append(('long_press', x, y, ms))

    def swipe(self, x1, y1, x2, y2, ms=300):
        self.swipes += 1
        self.actions.append(('swipe', x1, y1, x2, y2, ms))

    def type_text(self, text):
        self.typed += text
        self.actions.append(('type', text))

    def key(self, code):
        self.actions.append(('key', code))

    def open_app(self, app):
        self.actions.append(('open', app))
