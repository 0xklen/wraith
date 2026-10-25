"""The agent loop: screenshot -> plan -> act -> repeat until done.

`planner` is any object with `.plan(task, screenshot_bytes, history) -> dict`.
Use `wraith.llm.LLM` for a real model, or a scripted planner for tests.
"""
import time


class Agent:
    def __init__(self, driver, planner, max_steps=25, delay=0.6):
        self.driver = driver
        self.planner = planner
        self.max_steps = max_steps
        self.delay = delay

    def run(self, task):
        history = []
        for step in range(1, self.max_steps + 1):
            shot = self.driver.screenshot()
            action = self.planner.plan(task, shot, history)
            if not isinstance(action, dict):
                raise RuntimeError('planner returned a non-dict action')
            kind = action.get('action', '')
            if kind == 'done':
                return {
                    'done': True,
                    'steps': step,
                    'summary': action.get('summary', ''),
                    'history': history,
                }
            self._execute(action)
            history.append(action)
            if self.delay:
                time.sleep(self.delay)
        return {
            'done': False,
            'steps': self.max_steps,
            'summary': 'reached max steps',
            'history': history,
        }

    def _execute(self, a):
        kind = a.get('action', '')
        if kind == 'tap':
            self.driver.tap(a['x'], a['y'])
        elif kind == 'long_press':
            self.driver.long_press(a['x'], a['y'], a.get('ms', 800))
        elif kind == 'swipe':
            self.driver.swipe(a['x1'], a['y1'], a['x2'], a['y2'], a.get('ms', 300))
        elif kind == 'type':
            self.driver.type_text(a['text'])
        elif kind == 'key':
            self.driver.key(a['code'])
        elif kind == 'open':
            self.driver.open_app(a['app'])
        elif kind == 'wait':
            time.sleep(a.get('ms', 1000) / 1000.0)
        else:
            raise RuntimeError('unknown action: ' + repr(a))
