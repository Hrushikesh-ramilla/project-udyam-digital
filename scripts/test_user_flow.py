import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.services.advisor_agent import AdvisorAgent
from backend.app.db.registry import get_registry

agent = AdvisorAgent(get_registry())
res1 = agent.process_turn("hola", script_mode="latin")
print("Turn 1 slots:", res1.slots)
print("Turn 1 display_latin:", repr(res1.display_latin[:60]))
print("Turn 1 display_native:", repr(res1.display_native[:60]))

res2 = agent.process_turn("ela unnaru", previous_slots=res1.slots, script_mode="latin")
print("Turn 2 display_latin:", repr(res2.display_latin[:60]))
print("Turn 2 display_native:", repr(res2.display_native[:60]))
print("Turn 2 display_markdown:", repr(res2.display_markdown[:60]))
