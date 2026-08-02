# Agent Builds Filing & Versioning Standard — v1.0 (RATIFIED)

**Status:** RATIFIED by Rex, 2026-07-31. Supersedes the SEED `Builds\_FILING-STANDARD.md` (v0.3, Archy, 2026-07-15) and Marshall's proposal `build-filing-and-versioning-standard-for-archy.md` (2026-07-31), merged into this single Canon standard.
**Owner:** Archy (CTO). **Applies to:** everything under `Agent-Fleet\Builds\`.
**Sibling standards:** the *Library* Filing Standard (`Agent-Library-Filing-Standard`) governs the Tabularium library; the Engineering Design & Build Standards govern *how* a build is engineered. This one governs *where a build lives and how its versions are kept* — the workshop, not the library or the engineering method.

> **`Builds\` is a dev / test / sandpit.** Nothing under `Builds\` is published live. Preview deploys (e.g. Vercel `*.vercel.app`) are **test previews of a candidate**, not production. Promotion to real production is a separate, future step (see §6) — as of ratification, no fleet build is in production.

---

## 1. Why this exists

Two failures to design against:

- **Sandbox sprawl** (SEED origin): version-suffixed sibling folders, the same product duplicated across trees, no home that tells you at a glance what a build is for. Version numbers baked into folder names always drift out of truth.
- **One build, many homes, drifting names, no version** (Marshall's origin): by mid-July the *same* Rex product existed under three names, its builds split across two trees, alternatives floating free of any version line, and per-job reports with no version at all. Finding "the latest" meant asking.

The fix is the same discipline for both: **file by purpose at the top level; key each product by a stable id; keep version history inside the product folder as `vN\` subfolders — never as sibling directories; carry one index per product that answers "where's the latest?" without asking.**

---

## 2. Top-level categories

Every build lives under exactly one category directory below `Builds\`. Pick by the decision rule in §4.

| Category | What lives here | Examples |
|---|---|---|
| `Websites\` | **Public-facing** marketing / brand sites, keyed by **domain**. | `datavation.ai\`, `datavation.co.uk\`, `austenking.com\`, `rexhomeservices.co.uk\` |
| `Dashboards\` | **Internal** monitor / command / ops views — *even if served as a web app*. Audience is the fleet/Rex, not the public. | `rex-ops-dashboard`, `rex-site-reports`, `fleet-state-view` |
| `Apps\` | Runnable **services / tools** — anything with a boot entry point (`server.py`, `bot.py`, `main.py`). | `agent-dispatcher`, `pc-cockpit`, `telegram-cockpit`, `voice-agent-engine` |
| `Reports\` | **Point-in-time** analytical outputs: audits, reviews, syntheses, inventories. Written once, not maintained. | Portfolio-Audit, build-inventory snapshots |
| `Documents\` | Standalone **documents / specs / instruments** not tied to a single build. | question sets, playbooks, standards drafts, briefs |
| `Seats\` | **Staged agent births / rebuilds** awaiting gate-review + promotion into `Agents\`. A staged identity+capability package, not a running service. | tessa-seat, quinn-cfo, dex-* |
| `Fleet\` | Cross-cutting **fleet plumbing / infrastructure** that isn't a single app. | fleet-guardrails, fleet-hooks, standup-routine |
| `Shared\` | Assets consumed by **many** builds — not deployable alone. | design-system (tokens + skins) |
| `_Provenance\` | **Superseded / duplicate** trees kept for lineage only. Never deploy candidates. Underscore sorts it aside. | fable-web-estate, `*-archive-*` |

These nine are the defined target. Existing builds migrate incrementally as they're next touched, or in a Rex-authorised sweep — not a big-bang move.

## 3. The product & versioning rules

1. **One home per product.** `Builds\<category>\<product-id>\`. A product is a thing that ships (a dashboard, a site, an app). Everything for it lives under that one folder — never split across trees.

2. **Stable technical id; display name may differ.** The product-id = the git repo name = the (sandpit) deploy-project name, and it **does not change** once things deploy from it. Renaming a *display* name is free; renaming the *id* churns the repo, the deploy project and the URL. (e.g. `rex-ops-dashboard` stayed the id even though the product is now displayed as "Rex Field Operations Dashboard".)

3. **Version folders `vN`, one per iteration — inside the product folder, never as sibling directories.** Linear. Gaps are allowed and honest (the Rex dashboard is `v1 → v3 → v4 → v5 → v6` because v2 never shipped). Don't renumber history to look tidy.

4. **The current candidate sits at the product root; `vN\` folders are frozen history.** The root holds the working build — the one pushed to the sandpit preview (`index.html` …). Prior iterations freeze as `vN\` folders. **Never overwrite a frozen `vN`, and never iterate by editing history** — cut/keep the prior state as `vN\`, then move the product forward at root. *(This supersedes the SEED's "highest `vN` = candidate": the candidate lives at root, not in the highest-numbered folder.)*

5. **Alternatives are tagged `vN-<variant>`** off the version they branch from — a different *design* or a different *tool* for the same product (e.g. `v6-powerbi`, `v7-record`). A variant is a branch of one product, **not** a new product.

6. **Every product carries a `register.html` at its root** — the single index for that product: the build catalogue, the **Brief**, the **Technical Design Spec**, the **Handover / operating** notes, and the deploy identity (§8), cross-linking sibling products. It is the thing you read instead of asking "where's the latest?". *(This is the primary index; a one-line note inside each `vN\` recording its standing is still welcome, but the `register` is the source of truth.)*

7. **Sandpit-deploy hygiene.** Only the current candidate ships to the preview. Version folders, the register and internal docs are held **out of the deployed bundle** — via `.gitignore` for git-backed deploys, or by construction for API deploys.

8. **Deploy identity is recorded** in the register: repo, deploy project, **preview URL (labelled as a test preview, not production)**, and any secret slug — so the previewed thing is always traceable back to its source.

## 4. Decision rule (which category?)

Ask in order; first match wins:
1. Superseded / kept only for lineage? → `_Provenance\`
2. A staged agent identity awaiting promotion to `Agents\`? → `Seats\`
3. Boots a service (has a runtime entry point)? → `Apps\`
4. An internal monitor/command/ops view (public = no)? → `Dashboards\`
5. Public-facing site? → `Websites\` (folder = domain)
6. Cross-cutting fleet plumbing used fleet-wide? → `Fleet\`
7. An asset many builds consume, not deployable alone? → `Shared\`
8. A once-off analysis/audit/review? → `Reports\`
9. Otherwise a standalone document/spec/instrument? → `Documents\`

## 5. Live routine that sweeps the Builds layout must be reconciled first (⚠)

`Builds\fleet-state-view-v1\generate.py` sweeps `Builds\` **one directory deep** and treats a folder as a website only if it holds `index.html` directly. Products nested under `<category>\<product-id>\` sit deeper than the generator sees. **Any routine that sweeps the Builds layout must be reconciled to this standard before a rollout that would move folders under it** — reconcile the sweeper (Cody), or don't regenerate its output, until it descends into the category/product structure.

## 6. `Builds\` = dev · production is a future, separate step

`Agent-Fleet\Builds\` is the dev / test / sandpit — everything **not** live. **No fleet build is in production as of ratification.** When a product is genuinely promoted to production, that is a distinct, Rex-authorised step that takes the chosen build *out* of the sandpit; the production topology (a sibling `Live\` tree, a managed host, or a promoted deploy) is decided at that point and is **out of scope for this version** — recorded here only so "current candidate at root" is never mistaken for "live in production".

**Nesting constraint (why some folders stay flat at `Builds\` root):** a build that computes its fleet-root by fixed depth, or a running service wired into scheduled tasks + `.env` paths, breaks when moved into a category folder. `pc-cockpit`, `agent-dispatcher-v1`, `telegram-cockpit`, `voice-agent-engine-v1`, and the `fleet-state-view-v1` generator stay flat until Cody makes them resolve the root by a marker rather than by depth. Do not drag these into a category folder — it's a coordinated migration, not a tidy.

## 7. Reference implementation (Rex estate, as built — sandpit)

| Product | Home | Versions | Sandpit preview |
|---|---|---|---|
| **Rex Field Operations Dashboard** | `Builds\Dashboards\rex-ops-dashboard\` (repo id kept) | `v1 v3 v4 v5 v6` + variants `v6-powerbi` `v7-record`; current candidate at root | `rex-ops-dashboard.vercel.app` (git) — **test preview** |
| **Rex Site Reports** | `Builds\Dashboards\rex-site-reports\` | `v1` (current); `v2` planned | `rex-report-demo.vercel.app` (REST API deploy) — **test preview** |

Each carries a `register.html`. The retired "Delivery Record" name is now the `v7-record` variant. The marketing site `Builds\Websites\rexhomeservices.co.uk\` is a separate product on the `vN` pattern.

## Changelog
- **v1.0 RATIFIED (2026-07-31, Rex)** — merged the Archy SEED (`Builds\_FILING-STANDARD.md` v0.3) with Marshall's proposal into one Canon standard. Adopted from Marshall: stable product-id = repo = deploy-project (§3.2), current-candidate-at-root / `vN` = frozen history (§3.4, superseding the SEED's "highest vN = candidate"), `vN-<variant>` alternatives (§3.5), per-product `register.html` as primary index (§3.6, superseding per-version `BUILD-NOTE.md`), sandpit-deploy hygiene (§3.7) and recorded deploy identity (§3.8). Kept from the SEED: the nine categories (§2), the decision rule (§4), the sweeper-reconciliation rule (§5), and the nesting constraint (§6). Corrected the framing per Rex: `Builds\` is a sandpit and **nothing is live**; preview URLs are test previews; production promotion is a deferred, separate step (§6).
- Prior lineage: SEED v0.1–v0.3 (2026-07-15, Archy) — see `_version-history`.
