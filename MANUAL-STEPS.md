# MANUAL-STEPS.md -- console runbook (GENERATED, do not hand-edit)

Routines, triggers, tokens and connector OAuth have no management API; they are
created in the web console. Generated from fleet.yaml for org **Datavation**.

> LEAST PRIVILEGE IS NOT OPTIONAL. The New-routine form pre-attaches every org
> connector. For each routine below you MUST remove all, add back only the listed set,
> and VERIFY the saved routine matches. A routine silently holding Stripe/Gmail on the
> real org account is the exact blast-radius failure this runbook exists to prevent.

In claude.ai/code/routines > New routine > Cloud:

## 1. Routine `cody`
    Name:        cody
    Model:       claude-opus-4-8
    Prompt:      paste agents/cody/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL. This routine needs no connector -- add nothing back.
    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):
                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:
                   (a) PRESENT -- the connector list equals exactly { } (NONE); and
                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:
                        docusign, gmail, ms365, outlook, paypal, quickbooks, square, stripe.
                 The console attaches all org connectors by default, so proving (b) ABSENT
                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api (event-driven wake)

## 2. Routine `holly`
    Name:        holly
    Model:       claude-sonnet-5
    Prompt:      paste agents/holly/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL, then add back ONLY: telegram (sandbox), notion (read)
    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):
                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:
                   (a) PRESENT -- the connector list equals exactly { telegram (sandbox), notion (read) }; and
                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:
                        docusign, gmail, ms365, outlook, paypal, quickbooks, square, stripe.
                 The console attaches all org connectors by default, so proving (b) ABSENT
                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api (event-driven wake)

## 3. Routine `marshall`
    Name:        marshall
    Model:       claude-opus-4-8
    Prompt:      paste agents/marshall/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL, then add back ONLY: google-drive (read)
    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):
                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:
                   (a) PRESENT -- the connector list equals exactly { google-drive (read) }; and
                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:
                        docusign, gmail, ms365, outlook, paypal, quickbooks, square, stripe.
                 The console attaches all org connectors by default, so proving (b) ABSENT
                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api, schedule (event-driven wake)

## 4. Routine `tessa`
    Name:        tessa
    Model:       claude-opus-4-8
    Prompt:      paste agents/tessa/CLAUDE.md
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL, then add back ONLY: notion (read)
    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):
                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:
                   (a) PRESENT -- the connector list equals exactly { notion (read) }; and
                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:
                        docusign, gmail, ms365, outlook, paypal, quickbooks, square, stripe.
                 The console attaches all org connectors by default, so proving (b) ABSENT
                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    api (event-driven wake)

## 5. Routine `cody-heartbeat`  -- autonomous PC-offline boot proof (runs bootcheck.py --trigger schedule)
    Name:        cody-heartbeat
    Model:       claude-opus-4-8
    Prompt:      ops routine owned by seat 'cody' -- autonomous PC-offline boot proof (runs bootcheck.py --trigger schedule)
    Repository:  Datavation/datavation-fleet (default branch)
    Environment: fleet-default
    Connectors:  REMOVE ALL. This routine needs no connector -- add nothing back.
    VERIFY (evidence, per Archy ruling 2026-08-02 -- no routine closed on assertion):
                 re-open the SAVED routine and confirm BOTH, capturing a screenshot:
                   (a) PRESENT -- the connector list equals exactly { } (NONE); and
                   (b) ABSENT  -- NONE of the forbidden money/live-comms set is attached:
                        docusign, gmail, ms365, outlook, paypal, quickbooks, square, stripe.
                 The console attaches all org connectors by default, so proving (b) ABSENT
                 matters as much as (a) PRESENT. A routine is DONE only with that evidence.
    Permissions: leave 'Allow unrestricted branch pushes' OFF.
    Triggers:    schedule (event-driven wake)

Then: `python verify.py`.
