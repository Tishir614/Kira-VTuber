# Kira Desktop

Kira can run as a local desktop-style application while keeping the core bound to localhost.

Run:

```bash
./scripts/kira-desktop.sh
```

To add a launcher to the Linux application menu:

```bash
./scripts/install-desktop-entry.sh
```

The launcher starts Ollama if its executable is available, starts Kira Core, waits for the health endpoint, and opens Kira Studio in browser app mode when Chromium is available.

Logs are written to `runtime/kira.log`. This directory is ignored by Git.

The future transparent Live2D window will be a separate renderer process connected to Kira Core, so OBS capture and the control panel can remain independent.
