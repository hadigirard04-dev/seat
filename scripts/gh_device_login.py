# Detached GitHub device login helper
import os
import subprocess
import time
from pathlib import Path

for k in ["http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
    os.environ.pop(k, None)

gh = r"C:\Program Files\GitHub CLI\gh.exe"
log = Path(os.environ.get("TEMP", ".")) / "gh-device-login.log"
log.write_text("starting\n", encoding="utf-8")

p = subprocess.Popen(
    [gh, "auth", "login", "--hostname", "github.com", "--git-protocol", "https", "--web"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
    env=os.environ.copy(),
)
with log.open("a", encoding="utf-8") as f:
    f.write(f"pid={p.pid}\n")
    f.flush()
    while True:
        line = p.stdout.readline()
        if not line:
            break
        f.write(line)
        f.flush()
    f.write(f"exit={p.poll()}\n")
