import json, subprocess, sys
from pathlib import Path

HERE=Path(__file__).parent
subprocess.run([sys.executable,str(HERE/"smoke_benchmark.py")],check=True,capture_output=True,text=True)
p=json.loads((HERE/"metrics.json").read_text())
assert p["quantum_hardware"] is False
assert p["claim"]=="No quantum advantage claimed."
assert len(p["results"])==2
assert {r["model"] for r in p["results"]}=={"classical_esn","quantum_statevector_simulator"}
for r in p["results"]:
    assert r["mae"]>=0 and r["wape"]>=0
print("quantum reservoir smoke contract passed")
