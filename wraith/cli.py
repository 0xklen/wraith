"""WRAITH command line interface.

    python -m wraith devices                 # list what can be bound
    python -m wraith bind --device sim       # bind a device (sim | android | ios)
    python -m wraith task "open the app and check the news" --mock
    python -m wraith screenshot -o shot.png
    python -m wraith tap 540 1200
    python -m wraith swipe 540 1800 540 600
"""
import argparse
import json
import os
import subprocess

from .agent import Agent
from .llm import LLM

CONFIG_PATH = os.path.expanduser('~/.wraith/config.json')


def load_config():
    cfg = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
    env = {
        'base_url': os.environ.get('WR_BASE_URL'),
        'api_key': os.environ.get('WR_API_KEY'),
        'model': os.environ.get('WR_MODEL'),
        'device': os.environ.get('WR_DEVICE'),
        'appium_url': os.environ.get('WR_APPIUM_URL'),
        'serial': os.environ.get('WR_ANDROID_SERIAL'),
    }
    for k, v in env.items():
        if v:
            cfg[k] = v
    return cfg


def make_driver(cfg, device):
    from .drivers.sim import SimDriver
    if device == 'sim':
        return SimDriver()
    if device == 'android':
        from .drivers.android import AndroidDriver
        return AndroidDriver(cfg.get('serial'))
    if device == 'ios':
        from .drivers.ios import IOSDriver
        return IOSDriver(cfg.get('appium_url', 'http://127.0.0.1:4723'), cfg.get('caps', {}))
    raise SystemExit(f"unknown device '{device}' (use sim, android, or ios)")


class MockPlanner:
    """Scripted planner — exercises the full loop with no LLM key."""

    def __init__(self, script=None):
        self.script = script or [
            {'action': 'tap', 'x': 540, 'y': 1200},
            {'action': 'swipe', 'x1': 540, 'y1': 1800, 'x2': 540, 'y2': 600},
            {'action': 'type', 'text': 'hello'},
            {'action': 'key', 'code': 'enter'},
            {'action': 'done', 'summary': 'demo completed'},
        ]
        self.i = 0

    def plan(self, task, shot, history):
        if self.i >= len(self.script):
            return {'action': 'done', 'summary': 'script exhausted'}
        a = self.script[self.i]
        self.i += 1
        return a


def cmd_devices(args):
    import shutil
    print('sim      — built-in simulator (no device needed)')
    if not shutil.which('adb'):
        print('android  — adb not found (install Android platform-tools)')
    else:
        r = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        lines = [l for l in r.stdout.splitlines()[1:] if l.strip()]
        if lines:
            for l in lines:
                print('android  — ' + l.strip())
        else:
            print('android  — adb present, no device attached')
    print('ios      — Appium + WebDriverAgent (set WR_APPIUM_URL)')


def cmd_bind(args):
    cfg = load_config()
    device = args.device or 'sim'
    cfg['device'] = device
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=2)
    d = make_driver(cfg, device)
    w, h = d.size()
    print(f'bound {device} — screen {w}x{h}')


def cmd_task(args):
    cfg = load_config()
    device = args.device or cfg.get('device') or 'sim'
    driver = make_driver(cfg, device)
    if args.mock:
        planner = MockPlanner()
    else:
        if not cfg.get('api_key'):
            raise SystemExit('no API key: set WR_API_KEY (or run with --mock to test)')
        llm = LLM(cfg['base_url'], cfg['api_key'], cfg['model'])
        planner = llm
    agent = Agent(driver, planner, max_steps=args.steps)
    result = agent.run(args.task)
    print(json.dumps(result, indent=2))


def cmd_screenshot(args):
    cfg = load_config()
    device = args.device or cfg.get('device') or 'sim'
    driver = make_driver(cfg, device)
    data = driver.screenshot()
    out = args.out or 'screenshot.png'
    with open(out, 'wb') as f:
        f.write(data)
    w, h = driver.size()
    print(f'saved {out} ({len(data)} bytes, {w}x{h})')


def cmd_tap(args):
    cfg = load_config()
    device = args.device or cfg.get('device') or 'sim'
    make_driver(cfg, device).tap(args.x, args.y)
    print(f'tapped ({args.x}, {args.y})')


def cmd_swipe(args):
    cfg = load_config()
    device = args.device or cfg.get('device') or 'sim'
    make_driver(cfg, device).swipe(args.x1, args.y1, args.x2, args.y2, args.ms)
    print(f'swiped ({args.x1},{args.y1}) -> ({args.x2},{args.y2})')


def main(argv=None):
    p = argparse.ArgumentParser(prog='wraith', description='WRAITH — an AI agent that operates your phone')
    sub = p.add_subparsers(dest='cmd')

    sub.add_parser('devices', help='list devices that can be bound')

    b = sub.add_parser('bind', help='bind a device (persists to ~/.wraith/config.json)')
    b.add_argument('--device', '-d', help='sim | android | ios (default sim)')

    t = sub.add_parser('task', help='run an AI task on the bound device')
    t.add_argument('task', help='the task, in plain language')
    t.add_argument('--device', '-d')
    t.add_argument('--mock', action='store_true', help='use a scripted planner (no LLM key)')
    t.add_argument('--steps', type=int, default=25)

    s = sub.add_parser('screenshot', help='save a screenshot')
    s.add_argument('--device', '-d')
    s.add_argument('--out', '-o', default='screenshot.png')

    tp = sub.add_parser('tap', help='tap at coordinates')
    tp.add_argument('--device', '-d')
    tp.add_argument('x', type=int)
    tp.add_argument('y', type=int)

    sw = sub.add_parser('swipe', help='swipe between two points')
    sw.add_argument('--device', '-d')
    sw.add_argument('x1', type=int)
    sw.add_argument('y1', type=int)
    sw.add_argument('x2', type=int)
    sw.add_argument('y2', type=int)
    sw.add_argument('--ms', type=int, default=300)

    args = p.parse_args(argv)
    if args.cmd == 'devices':
        cmd_devices(args)
    elif args.cmd == 'bind':
        cmd_bind(args)
    elif args.cmd == 'task':
        cmd_task(args)
    elif args.cmd == 'screenshot':
        cmd_screenshot(args)
    elif args.cmd == 'tap':
        cmd_tap(args)
    elif args.cmd == 'swipe':
        cmd_swipe(args)
    else:
        p.print_help()


if __name__ == '__main__':
    main()
