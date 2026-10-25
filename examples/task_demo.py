"""Run a task on the simulated device with a scripted planner.

The shortest possible example of the full agent loop — no phone, no API key.
Swap the planner for a real `wraith.llm.LLM` to drive a real device.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wraith.agent import Agent
from wraith.cli import MockPlanner
from wraith.drivers.sim import SimDriver

driver = SimDriver()
agent = Agent(driver, MockPlanner())

result = agent.run("open the app and check the weather")

print("done:", result["done"], "| steps:", result["steps"])
print("summary:", result["summary"])
print("actions the agent performed:", driver.actions)
