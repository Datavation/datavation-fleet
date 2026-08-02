# MANUAL-STEPS.md -- console runbook (GENERATED, do not hand-edit)

Routines, triggers, tokens and connector OAuth have no management API; they are
created in the web console. Generated from fleet.yaml for org **Datavation**.

For each seat, in claude.ai/code/routines > New routine > Cloud:

## 1. Routine `cody`
    Name:        cody
    Model:       claude-opus-4-8
    Prompt:      paste agents/cody/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL (least privilege -- this seat needs none)
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api (event-driven wake)

## 2. Routine `holly`
    Name:        holly
    Model:       claude-sonnet-5
    Prompt:      paste agents/holly/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  telegram (sandbox), notion (read)
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api (event-driven wake)

## 3. Routine `marshall`
    Name:        marshall
    Model:       claude-opus-4-8
    Prompt:      paste agents/marshall/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  google-drive (read)
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api, schedule (event-driven wake)

Then: `python verify.py`.
