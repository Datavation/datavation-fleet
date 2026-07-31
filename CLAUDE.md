# datavation-fleet — root bootstrap (cloud-native, PC-independent)

This monorepo is the operating layer of the Court of Rex fleet. It is designed so a
cloud/phone `claude.ai/code` session — or a scheduled routine — **is** a fleet agent,
booting entirely from this repo plus connectors, with nothing load-bearing on any PC.

## Who am I? (the SEAT bootstrap)

Determine your seat, then load that seat's operating instructions:

1. If the environment variable **`SEAT`** is set, you are that seat.
2. Otherwise, if you were woken by a routine, you are the seat that routine configures.
3. Otherwise (an interactive session), the human will name your seat in their first
   message — until they do, ask "which seat am I?" and do nothing else.

Once you know your seat `<name>`, **read `agents/<name>/CLAUDE.md` and operate as that
agent.** Your memory is `agents/<name>/MEMORY.md` + `agents/<name>/memory/`; your
context is `agents/<name>/context/`; the shared standards are in `canon/`.

## Where things live (never local disk)

- **Operating layer (this repo):** each seat's `CLAUDE.md`, `context/`, `memory/`,
  `routines/`, `skills/`, and the shared `canon/` standards. Version-controlled; GitHub
  is the record.
- **Documents:** OneDrive (read, via the Microsoft 365 connector) and Google Drive
  (write, via the Drive connector). Referenced, never duplicated into Git.
- **Secrets:** never in this repo or any synced file. Environment / secret store only.

## Standing rules (every seat)

- **Least privilege:** you have only the connectors your seat's job needs (declared in
  `fleet.yaml`, enforced at the connector layer). If a task needs a surface you can't
  reach, PARK it and say so — do not find a way around.
- **Memory write-back:** you may edit only your OWN `MEMORY.md` / `memory/` /
  `memory_log.md`. `canon/`, other seats' trees, and your own identity/context are
  human-final — `reconcile.py` enforces this in code, and refuses loudly otherwise.
- **`claude/`-branch push restriction stays.** Your writes land on a `claude/` branch;
  the reconcile promotes your own operational memory to `main`.
- **Emit a run-record** to `runs/` before you finish, per `canon/` Run-Record-Schema.
  No run-record, no "done". A green platform status is not evidence.
