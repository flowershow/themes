# Themes Closeout and Successor Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the completed August theme-cloning phase accurately and establish one current successor epic in `flowershow/flowershow`.

**Architecture:** Persist the successor epic body in the themes repository, publish it through GitHub, then update repository-local state and the historical Flowershow blog post to reference that issue. Close old issues only after their successor and outcome links exist.

**Tech Stack:** Markdown, Git, GitHub CLI, Flowershow content repository

## Global Constraints

- All GitHub issues remain in `flowershow/flowershow`.
- Leave `content/flowershow-app/docs/reference/themes.md` unchanged.
- Keep #1338 open as a linked near-term child issue.
- Keep #854 open and limit work to bounded triage.
- Keep L4 layout architecture out of the successor epic's implementation scope.
- Material and code.storage remain preview/beta themes.
- Use feature branches and pull requests; do not push directly to `main`.
- Do not tag or release themes.

---

### Task 1: Create the successor epic

**Files:**
- Create: `docs/plans/2026-08-21-themes-discovery-authoring-epic.md`

**Interfaces:**
- Consumes: `docs/plans/2026-08-21-themes-next-phase-design.md`
- Produces: a reusable issue body and a GitHub issue URL/number in `flowershow/flowershow`

- [ ] **Step 1: Write the epic body**

Include the outcome, five workstreams, acceptance criteria, non-goals, and
links to #1339, #1337, #1338, #854, themes PR #8, and the design document.

- [ ] **Step 2: Check required sections and references**

```bash
rg -n "Outcome|Workstreams|Acceptance criteria|Non-goals|1339|1337|1338|854|pull/8" \
  docs/plans/2026-08-21-themes-discovery-authoring-epic.md
```

Expected: every required section and link is present.

- [ ] **Step 3: Commit the issue body**

```bash
git add -- docs/plans/2026-08-21-themes-discovery-authoring-epic.md
git commit -m "docs: define themes discovery and authoring epic"
```

- [ ] **Step 4: Create the GitHub epic**

```bash
gh issue create --repo flowershow/flowershow \
  --title "[epic] Themes discovery, authoring, and preview releases" \
  --label epic \
  --body-file docs/plans/2026-08-21-themes-discovery-authoring-epic.md
```

Expected: one new open issue URL. Capture it for every later reference.

### Task 2: Refresh repository-local state

**Files:**
- Modify: `NEXT.md`
- Modify: `docs/features.yaml`

**Interfaces:**
- Consumes: successor epic URL and 2026-08-21 verification output
- Produces: concise current state for humans and agents

- [ ] **Step 1: Record the completed human review**

For both preview themes, set `fidelity: reviewed-close`, set
`last_verified: 2026-08-21`, and prepend a short fidelity note that Rufus
reviewed the live theme and reported it looked okay. Preserve historical notes.

- [ ] **Step 2: Rewrite `NEXT.md` around the successor**

Set branch to `main`; link the successor as the tracking source; record the
completed fidelity and #1349 checks; list preview site, authoring hub,
release-readiness, and #1338 as next work; keep #1348 and L4 research separate.

- [ ] **Step 3: Verify and validate the state**

```bash
scripts/verify.sh
rg -n "reviewed-close|2026-08-21" docs/features.yaml
rg -n "main|preview site|authoring|1338|1348" NEXT.md
! rg -n "Human fidelity review|Verify flowershow/flowershow#1349 fix" NEXT.md
```

Expected: verification passes and completed tasks are not presented as pending.

- [ ] **Step 4: Commit repository state**

```bash
git add -- NEXT.md docs/features.yaml
git commit -m "docs: close completed theme cloning phase"
```

### Task 3: Update the historical theming blog

**Files:**
- Modify: `/Users/rgrp/src/flowershow/flowershow/content/flowershow-app/blog/2026-08-08-whats-actually-changeable-in-theming.md`
- Do not modify: `/Users/rgrp/src/flowershow/flowershow/content/flowershow-app/docs/reference/themes.md`

**Interfaces:**
- Consumes: successor epic URL and completed #1339 outcome
- Produces: a dated follow-up note near the top of the public blog post

- [ ] **Step 1: Create a main-repository feature branch**

```bash
git -C /Users/rgrp/src/flowershow/flowershow switch -c docs/themes-work-follow-up
```

- [ ] **Step 2: Add `Update, 21 August 2026` after frontmatter**

Link completed #1339, the successor epic, the current themes reference page,
the human tutorial, and the AI workflow. Do not rewrite the historical body.

- [ ] **Step 3: Prove the reference gallery was untouched**

```bash
git -C /Users/rgrp/src/flowershow/flowershow diff --exit-code \
  main -- content/flowershow-app/docs/reference/themes.md
```

Expected: exit 0 and no output.

- [ ] **Step 4: Validate and commit**

```bash
git -C /Users/rgrp/src/flowershow/flowershow diff --check
rg -n "Update, 21 August 2026|issues/1339|docs/reference/themes|theme-authoring-tutorial|ai-theme-cloning" \
  /Users/rgrp/src/flowershow/flowershow/content/flowershow-app/blog/2026-08-08-whats-actually-changeable-in-theming.md
git -C /Users/rgrp/src/flowershow/flowershow add -- \
  content/flowershow-app/blog/2026-08-08-whats-actually-changeable-in-theming.md
git -C /Users/rgrp/src/flowershow/flowershow commit -m "docs: link theming article to follow-up work"
```

- [ ] **Step 5: Push, open a non-draft PR, await checks, and merge**

```bash
git -C /Users/rgrp/src/flowershow/flowershow push -u origin docs/themes-work-follow-up
gh pr create --repo flowershow/flowershow --base main --head docs/themes-work-follow-up \
  --title "docs: link theming article to follow-up work" \
  --body "Adds a dated status note linking the completed theme-cloning phase, current gallery, authoring material, and successor epic. Leaves the themes reference page unchanged."
```

Then run `gh pr checks --watch`, merge normally with branch deletion, switch
the local checkout back to `main`, and `git pull --ff-only`.

### Task 4: Close completed issues with evidence

**Files:** None

**Interfaces:**
- Consumes: successor epic URL, themes PR #8, and blog PR URL
- Produces: clean closure comments on #1339 and #1337

- [ ] **Step 1: Close #1339 as completed**

The closure comment records the two verified preview themes, authoring guides,
structural findings, themes PR #8, successor epic, #1338, and #1348.

- [ ] **Step 2: Close #1337 as completed**

Link the deployed gallery and its August 13 implementation. State that the
parallel preview-site experiment is tracked by the successor and does not
change the current reference page.

- [ ] **Step 3: Link #1338 without closing it**

Add one concise comment identifying it as a near-term child of the successor.

- [ ] **Step 4: Verify issue state**

```bash
gh issue view 1339 --repo flowershow/flowershow --json state,stateReason,url
gh issue view 1337 --repo flowershow/flowershow --json state,stateReason,url
gh issue view 1338 --repo flowershow/flowershow --json state,url
```

Expected: #1339 and #1337 closed/completed; #1338 open.

### Task 5: Bounded #854 triage and themes-repo PR

**Files:**
- Modify: `docs/plans/2026-08-21-themes-discovery-authoring-epic.md` only if a directly relevant dependency is missing

**Interfaces:**
- Consumes: #854 and its listed open children
- Produces: one triage comment and integrated closeout documents

- [ ] **Step 1: Inspect the listed open children**

Read #975, #864, #903, #883, #837, #916, #937, #1150, #1169, and #1167.
Classify each as directly relevant, independently tracked, or later triage.
Do not implement them.

- [ ] **Step 2: Comment on #854**

Post one dated summary, link the successor, identify direct dependencies, and
leave #854 open.

- [ ] **Step 3: Verify, push, and open the themes PR**

```bash
scripts/verify.sh
git diff --check
git status --short --branch
git push -u origin docs/themes-next-phase-design
gh pr create --repo flowershow/themes --base main --head docs/themes-next-phase-design \
  --title "docs: close theme-cloning phase and define successor" \
  --body "Adds the approved next-phase design and implementation plans, persists the successor epic, and refreshes NEXT/ledger state after verified human review."
```

- [ ] **Step 4: Await checks, merge, and verify `main`**

Run `gh pr checks --watch`, merge normally with branch deletion, switch to
`main`, pull with `--ff-only`, and run `scripts/verify.sh`.

Expected: merged PR, clean `main`, passing verifier.
