<div align="center">

# WRAITH

### An AI agent that operates your phone.

Bind your iPhone or Android to your Mac, tell the agent what to do in plain
language, and it screenshots → plans → taps, swipes and types → repeats, until
the task is done. Hands-free.

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.9%2B-3776ab.svg)](https://python.org)
[![stdlib](https://img.shields.io/badge/core-stdlib%20only-43c25c.svg)](#install)

</div>

---

## What it does

You run the agent on your computer (macOS or Linux). You bind a phone to it —
Android over `adb` (USB or Wi-Fi), or iPhone over Appium + WebDriverAgent. Then
you type a task and walk away:

```
$ wraith task "open WhatsApp, find the chat with Mom, and send 'on my way'"
```

WRAITH takes a screenshot, sends it to any vision LLM, the model returns the
next action as JSON, the driver executes it, and the loop repeats until the
model reports `done`.

## How it works

```
   you                    the agent loop (on your Mac)                the phone
   ───                                                               ─────
   "send Mom a text" ──▶  screenshot ──▶ LLM ──▶ {"action":"tap", ...}
                              ▲                      │
                              └──────── repeat ◀────┘
                                                       │
                                          driver: adb / WDA / sim
                                                       ▼
                                              tap · swipe · type · key
```

One backend-agnostic loop, three drivers:

| Driver     | Controls              | Needs                                 |
|------------|-----------------------|---------------------------------------|
| `android`  | any Android device    | `adb` + USB debugging (or `adb connect`) |
| `ios`      | iPhone / iPad         | Appium server + WebDriverAgent        |
| `sim`      | a fake in-memory phone| nothing (built for tests)             |

## Install

The core is **stdlib-only** — no pip install required.

```bash
git clone https://github.com/0xklen/wraith.git
cd wraith
python3 -m wraith --help
```

Optional: iOS support (Android and `sim` need nothing extra).

```bash
pip install -r requirements-ios.txt
```

## Quickstart

```bash
# 1. See what you can bind
python3 -m wraith devices

# 2. Bind a device (sim works with zero setup)
python3 -m wraith bind --device sim          # android | ios

# 3. Run a task
python3 -m wraith task "open settings and turn on dark mode" --mock   # no API key
python3 -m wraith task "open settings and turn on dark mode"          # real LLM
```

Run a task end-to-end with **no phone and no API key** (uses a scripted planner):

```bash
python3 -m wraith task "anything" --mock
```

## Configure the LLM

WRAITH talks to any OpenAI-compatible `/chat/completions` endpoint. Set env
vars, or write `~/.wraith/config.json`:

```bash
export WR_BASE_URL="https://api.openai.com/v1"   # or DeepSeek / OpenRouter / local
export WR_API_KEY="sk-..."
export WR_MODEL="gpt-4o"
```

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model": "gpt-4o",
  "device": "sim"
}
```

Any vision-capable model works. See `config.example.json`.

## Android setup

1. Install platform-tools so `adb` is on your `PATH`.
2. On the phone: enable **Developer options → USB debugging**.
3. USB: `wraith bind --device android`. Wi-Fi: `adb connect <phone-ip>:5555`
   first, then `export WR_ANDROID_SERIAL=<ip>:5555`.

## iOS setup

1. `brew install appium` and start it (or `appium` from npm).
2. Build and run WebDriverAgent on the device with Xcode.
3. Point WRAITH at the server and bind:

```bash
export WR_APPIUM_URL="http://127.0.0.1:4723"
python3 -m wraith bind --device ios
```

## Manual control

The agent loop is just the drivers composed. Drive the phone directly too:

```bash
python3 -m wraith screenshot -o shot.png
python3 -m wraith tap 540 1200
python3 -m wraith swipe 540 1800 540 600
```

## Project layout

```
wraith/
├── agent.py            # the loop: screenshot → plan → act → repeat
├── llm.py              # stdlib OpenAI-compatible chat client
├── prompts.py          # the agent's action schema
├── cli.py              # command line interface
└── drivers/
    ├── base.py         # DeviceDriver interface
    ├── android.py      # adb backend
    ├── ios.py          # Appium / WebDriverAgent backend
    └── sim.py          # in-memory fake phone (tests)
```

## Security

WRAITH runs entirely on **your** machine and operates **your** device over a
connection **you** set up (adb or Appium). It never phones home, uploads
screenshots anywhere except the LLM endpoint you configure, and stores nothing
beyond your own `~/.wraith/config.json`. Treat the LLM endpoint as you would
any third-party API: it receives the screenshots it needs to see the screen.

## License

[MIT](LICENSE)
