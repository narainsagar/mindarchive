# Session Log

One concise entry per working session. Newest first. Durable facts only — what
changed and why, not conversation.

---

## 2026-09-09 — Ready to publish, and two things refused

**Session:** [2026-09-09-04-prepare-for-publication-on-github-and-pages](sessions/2026-09-09-04-prepare-for-publication-on-github-and-pages/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**D-017 is reversed.** The condition it set — a product worth showing — has been
met. Publishing needed no new infrastructure, which is exactly what writing the
workflows at Milestone 1 and leaving them dormant was for.

**A separate "clean" public branch was asked for and argued against.**
project-memory is already excluded from the published *site*; only repository
browsers see it. And branches share history, so a second branch hides nothing
once history is pushed, while costing a cherry-pick forever. The real mechanism
would be two repositories. Once put that way the choice became one public
repository with everything in it (**D-032**).

**A public VPS demo was asked for and refused.** `docs/SECURITY.md` says there
is no authentication because this is a single-user local application. A public
instance means one shared archive that any visitor can read, write and export —
whatever one person imports, everyone downloads. That is the failure this
product exists to prevent, and it would put strangers' conversations on the
maintainer's server. Deferred with the four prerequisites scoped in the backlog.

**Prepared:** `docs/index.html` rebuilt on the same token names as
`apps/web/src/styles.css` so the site and application cannot drift;
`docs/DEPLOYMENT.md` written end to end, including a VPS section that says what
would have to exist first.

**Checked before committing, not after:** no secrets tracked, `data/`, `tmp/`
and `.env` all ignored. Git identity turned out to be unset despite existing
commits having an author — fixed per-repository before committing rather than
mid-commit.

**Three commits, not five.** `App.tsx` and `styles.css` are touched by all three
feature sessions, so a finer split would have produced commits that do not
compile.

**Verified**: 98 tests, full gate green, working tree clean.

**Not done:** nothing is pushed. `gh` is not installed and the GitHub username
is unknown, so the first push is the maintainer's step.

**Follow-up, same day — the visual check caught a shipped bug.** Every
documentation link on the rebuilt landing page would have 404ed on GitHub Pages.
Jekyll only converts Markdown with YAML front matter, and no document in `docs/`
had any, so `PRODUCT.html` and the rest would never have existed. Fixed with
front matter on all eleven documents and a `layout` default, and the site given
the application's palettes and Light / Dark / System through one Jekyll layout
(**D-033**). The lesson written into the guides: `python -m http.server` runs no
Jekyll, so under it a correct site and a broken one look identical — verify by
building the real output.

---

## 2026-09-09 — Support, Contribute, and a footer

**Session:** [2026-09-09-03-support-contribute-footer-and-navigation-sections](sessions/2026-09-09-03-support-contribute-footer-and-navigation-sections/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**Two of the three requested backlog items were already built**, and checking
first is what stopped them being filed twice. `importers/claude.py` has existed
since Milestone 5 with its own tests, and `.json` exports already import —
D-027's shape-based detection is precisely what makes a bare
`conversations.json` work when ChatGPT and Claude share that filename. The real
gap is the *other* providers, and that is what the backlog now says.

**The privacy worry was checked, not assumed.** A real Claude export in `tmp/`
cannot be committed: `.gitignore` already covers `tmp/`, `conversations.json`
and `*.zip`. Confirmed with `git check-ignore`.

**Five nav sections now (D-031)**: Archive, Coming next, Status, Support,
Contribute, plus a footer with copyright, licence, contact and Back to top.
"Coming next" became its own section again, **reversing point 4 of D-030 on the
same day** — folding it into Status was tidier until it needed a nav entry.
D-030 is struck at that point rather than quietly rewritten.

**No handle, address or URL was invented.** Every donation link in the new
`support.ts` ships blank; unset ones are filtered out, and the panel says so
rather than showing a placeholder. Filling that one file in turns them on.

**Contribute tells people not to send their export files** when reporting an
importer bug — a broken export is a copy of someone's private conversations,
and a privacy-first product should not teach the opposite habit. Tested.

**One real bug caught by a test:** the `mailto:` subject was not
percent-encoded, so mail clients would truncate it at the first space. Fixed at
the source.

**Verified**: 98 frontend tests (was 94), full gate green.

**Not done:** still no visual check across any of the day's three sessions.

---

## 2026-09-09 — Import becomes a dialog, and the page gets navigation

**Session:** [2026-09-09-02-import-dialog-and-in-page-navigation](sessions/2026-09-09-02-import-dialog-and-in-page-navigation/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**The literal request would have made it worse, and reading the code first is
what caught that.** Import was to move above the archive. But `ImportPanel`
carries the export instructions, the timing warning and the inbox status — a
screenful — so lifting it would have pushed the conversations down on every
visit to fix something done a handful of times. Two alternatives were drawn on
the shipped design and published for a decision before any code changed.

**Import is now a dialog (D-030)** opened from the archive header and the nav,
both showing the inbox waiting count. It closes on Escape, on a click outside,
and on its close button, and gives focus back to whatever opened it. `Modal` is
the project's first dialog primitive — hand-written, because the native
`<dialog>`'s `showModal()` is not implemented everywhere the tests run, and
because this did not warrant a dependency.

**The page now navigates within itself.** Sticky header with anchor links to
Your archive and Status, the current section highlighted while scrolling, and a
Back to top link. These are anchors, not routes — D-008 is extended, not
reversed, and the extension is written down rather than slipped in.

**"What is coming next" moved into the Status panel**, and that panel stopped
calling itself "Your archive", which `ArchivePanel` already does.

**Inbox state moved into `useInbox`**, because the panel and the button both
need the waiting count and the backend should be asked once.

**Verified**: 94 frontend tests (was 82), full gate green. Two failures were hit
and fixed on the way — a props change that broke the panel's tests, and one
assertion on wording the compact row had changed.

**Not done:** no visual check. Everything is verified by tests and the build.

---

## 2026-09-10 — Taking money, without putting payment in the product

**Session:** [2026-09-10-03-support-page-and-project-memory-move](sessions/2026-09-10-03-support-page-and-project-memory-move/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**The promise was never in the way (D-038).** `LICENSING.md` says donations are
handled "on the project website, not inside the application" — which permits a
donate page exactly. What it forbids is payment code in `apps/`, and that is now
kept *and tested*: the Support panel holds one link to the website, and a test
fails if any payment provider is named anywhere in the interface.

**A merchant of record, not raw Stripe.** An EU consumer sale creates a VAT
obligation on the first transaction, with no threshold. Raw Stripe would leave
registration, quarterly filing and a decade of records with the maintainer.

**Hosted checkout by plain link, no third-party script** — and a build check now
enforces it: no `<script src="http…">` or `<iframe src="http…">` anywhere in the
built site. A privacy product cannot fingerprint visitors on its own donate
page. `/support/` is driven entirely by `docs/_data/support.yml`; every URL is
blank, so the page says so rather than showing a dead link.

**Project memory moved to the repository root (D-039).** It was never
documentation. Outside `docs/`, the site cannot publish it — structural rather
than a config rule someone could delete without knowing what it was for. 50
files repointed.

**Two bugs found by running the checks, not by reading them.** The "Any amount"
button shipped with `href=""`, because **Liquid's `assign` does not evaluate a
comparison** — `assign x = a != b` is not a boolean. And `session.py` builds its
memory path from separate segments, so a search for `docs/project-memory` missed
the one line that would have broken CI.

**Verified**: gate green at 107 tests, lint clean, 618/618 links resolve, no
third-party embed, no provider domain in `apps/`, no empty href, and
`project-memory/` absent from the built site.

**Not verified:** any actual payment. No account exists and every URL is blank.

---

## 2026-09-10 — One header row, and the last of the sideways scrolling

**Session:** [2026-09-10-02-one-row-header-with-appearance-menus](sessions/2026-09-10-02-one-row-header-with-appearance-menus/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**A preview came first, and earned its keep.** Published as an Artifact using
container queries, so three breakpoints sat on one page running the real
responsive logic with working menus — judged rather than imagined, and approved
unchanged.

**The header is one row now (D-037).** Two segmented radio groups became two
menu buttons; six visible options was what forced the second row. The
navigation merged into the header and folds into a hamburger below 1024px. The
appearance buttons never fold — under 640px they drop their label and keep the
icon, and the theme icon shows the current choice, so it still reads.

**The sideways scrolling is fixed at the cause.** `.site-nav__in` and
`.sectionnav__list` both had `overflow-x: auto`; the links fold now instead of
overflowing. `pre` and `table` keep theirs deliberately — that is a container
scrolling so the page does not.

**A native `<select>` was rejected on purpose.** Free and bulletproof, but it
cannot show colour, and the palette options carry real swatches. The cost — a
hand-built menu owning its keyboard and focus, written twice — was accepted.

**Two regressions caught during the work, both mine.** Rewriting the brand
markup dropped the page's `<h1>`; two existing tests failed on exactly that. And
the script that rewrote the app's header CSS took the responsive gutter steps
with it, leaving a phone on a 60px gutter. Both fixed.

**Verified**: full gate green at 106 tests; site rebuilt with 531/531 internal
links resolving; every page on one header band with the nav inside it; an `awk`
pass confirming only `pre` and `table` still declare `overflow-x`.

**Not verified:** that nothing scrolls sideways. jsdom has no layout and there
is no headless browser here, so that is a manual check at real widths — and
neither surface has been looked at yet.

---

## 2026-09-10 — A blog, on the site rather than in the app

**Session:** [2026-09-10-01-a-blog-on-the-jekyll-site](sessions/2026-09-10-01-a-blog-on-the-jekyll-site/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**The blog belongs to the Jekyll site (D-035).** Serving `/blog` and `/docs`
from `localhost:5173` was requested and argued against: 5173 is the Vite dev
server, present only on a developer's machine, and the application is
local-first. Bundling the public site into it would contradict D-008 and D-032
and would need `react-router` plus a proxy to do worse what Jekyll does
natively. `:5173` is the application, `:4000` the site.

Infrastructure is `_posts/`, `/blog/`, a post layout on top of the shared one, a
hand-written `feed.xml` and blog styles built from the existing tokens — so
posts follow the reader's palette and theme automatically. **No plugins:**
`jekyll-feed` is absent from the local preview image, and using it would make
the local and published builds differ, which is the drift D-033 exists to
prevent.

**Four posts** — an introduction, what local-first actually means, how it is
built, and four decisions worth stealing. Marketing-forward as asked, but every
technical claim points at something in the repository; no invented numbers and
never "open source".

**Verification found a subtlety worth recording.** The built feed carried
relative item links, which RSS forbids. `url` and `baseurl` are unset in
`_config.yml` on purpose — `configure-pages` injects them for a project site at
build time, and hardcoding them would break local preview. Documented rather
than wrongly "fixed"; the published feed still needs checking after deploy.

**Nothing auto-publishes.** Posts may be drafted from anything, including an AI
assistant or a session record, but a person approves before merge. The
`CONTRIBUTING.md` section says so, marked as taking effect once the CLA exists
so it does not contradict that file's own opening.

**Verified**: Jekyll build — index and all four posts present and linked, the
draft template not published, `feed.xml` valid with four items, shared layout on
a post, `project-memory/` still excluded, no unrendered Liquid. `dev.py verify`
green.

**Not live:** the repository is private, and Pages does not publish from a
private repository on a free plan.

---

## 2026-09-09 — Appearance controls, and two repairs

**Session:** [2026-09-09-01-appearance-controls-palette-and-light-dark-system](sessions/2026-09-09-01-appearance-controls-palette-and-light-dark-system/SESSION.md)

**Agent:** Claude Opus 5 (Claude Code)

**A file move had quietly disarmed the project's own instructions.**
`CLAUDE.md`, `GEMINI.md` and `QWEN.md` had been moved into `prompts/` to shorten
the root. Each of those tools auto-loads its file from the repository root and
says nothing when it is missing, so every future agent session would have run
with no project rules and no error. The three were restored; `MASTER.md`, which
is referenced by path and has no such constraint, stayed at `prompts/MASTER.md`.
Live documents were repointed; history was deliberately left as written.

**The docker failure was a stale container, not a naming problem.** A container
from before the directory was renamed was still running under the old Compose
project name, colliding with the pinned `container_name`. Removed, and
`name: mindarchive` pinned in `docker-compose.yml` so a directory rename cannot
repeat it.

**Appearance became two questions instead of one (D-029).** A palette — Light
minimal (default), Warm paper, Ink & violet — and a theme: Light, Dark or
System. Three palettes were drawn from the user's own references and published
as a full-page preview with a live switcher before any code changed.

**The old toggle had a real defect.** It resolved the system preference into a
concrete light/dark and immediately stored it, so a first visit permanently
pinned the reader to whatever their computer said at that moment; "follow the
system" was unreachable. `system` is now a stored choice, watched for changes.
Because the resolved theme is what gets stamped on `<html>`, the stylesheet
selects on `[data-palette][data-theme]` alone — which removed the pre-existing
duplication of every dark token across two selectors.

**A decision-number collision was caught before it landed** — D-020 was already
taken. Renumbered to D-029 and added to the `docs/DECISIONS.md` index, the step
missed for D-025 and D-026 in Milestone 4.

**Verified**: 82 frontend tests, full `dev.py verify` gate green.

**Not done:** the preview's layout and typography. Only the colour system and the
controls shipped; `docs/index.html` is untouched, and the Google-Fonts typography
in the preview cannot ship as-is in a privacy-first app.

---

## 2026-09-08 — Milestone 5: a second provider, and archive export

**Session:** [2026-09-08-07-milestone-5-second-importer-and-archive-export](sessions/2026-09-08-07-milestone-5-second-importer-and-archive-export/SESSION.md)
· [prompts](sessions/2026-09-08-07-milestone-5-second-importer-and-archive-export/PROMPTS.md)
· [report](sessions/2026-09-08-07-milestone-5-second-importer-and-archive-export/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

**The second importer did exactly the job it was for.** ChatGPT and Claude both
ship a file called `conversations.json`, and `detect()` matched on that
filename — so the ChatGPT importer would have claimed a Claude export and
reported it empty. A latent bug since Milestone 2 that no amount of testing one
importer could find. Detection now inspects shape (**D-027**).

That is the whole argument for generalising an interface against a real second
case rather than a guessed one, and it is why **`StorageProvider` was
deliberately not built** (**D-028**). An interface with one implementation is a
guess about the second; with cloud a milestone away, building it now would
repeat the mistake this milestone corrected.

**The formats share almost nothing** — a flat `chat_messages` list against a
`mapping` tree, `name` against `title`, ISO 8601 against epoch floats,
`sender: "human"` against `author.role: "user"`. What they do share moved into
`importers/reading.py`, now that two real callers want it.

**Whole-archive export.** `GET /api/export` zips the archive folder: exactly the
folder, plus a README for whoever opens it without Mind Archive. A test asserts
no `.db` is included — the index belongs to the application, the conversations
belong to the user.

**Two things caught by failures.** Strict detection broke an empty and a corrupt
export down to "not recognised" instead of a real explanation, fixed with a
documented fallback. And adding decisions to the index in `docs/DECISIONS.md`
failed because D-025 and D-026 had never been added there — Milestone 4 updated
the log but not its summary.

**Verified**: 295 backend tests (was 254), 66 frontend (was 64), full gate
green.

**Outstanding:** no real export from either provider has been imported, and
nothing since Milestone 3 has been used in a browser.

---

## 2026-09-08 — Milestone 4: tags

**Session:** [2026-09-08-06-milestone-4-tags-and-organisation](sessions/2026-09-08-06-milestone-4-tags-and-organisation/SESSION.md)
· [prompts](sessions/2026-09-08-06-milestone-4-tags-and-organisation/PROMPTS.md)
· [report](sessions/2026-09-08-06-milestone-4-tags-and-organisation/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

**One question shaped the whole milestone.** Everything in the archive so far is
*derived* — conversations from an export, Markdown from those, the index from
the Markdown. Tags are the first thing a person **makes**. Putting them in
SQLite would have made a rebuildable cache load-bearing and broken D-004 exactly
where it would destroy original work. They live in `metadata.json`; SQLite
indexes them and holds nothing else (**D-025**).

**And the bug that would have followed.** Every ChatGPT export is a full export,
so re-importing rewrites every `metadata.json` — and an export has no tags. Done
naively, next month's import would have erased months of someone's filing,
silently, with nobody noticing until far too late. The writer merges tags
forward, and the test is named after that failure.

**Scope.** Only tags, not the full "Project, Memory, Document..." list
originally specified (**D-026**). Tags plus search already answer *"where is
that conversation about X?"*; building a second hierarchical scheme at the same
time means guessing how they interact before anyone has used either.

**Found by the tooling.** `Object.entries(undefined)` blanked the entire archive
panel when a response lacked `tags` — a fair stand-in for a cached frontend
meeting a newer backend. mypy caught a signature that lied: `clean_tags` claimed
`list[str]` while genuinely reading untrusted JSON. Six SQL-injection warnings
were checked rather than suppressed — the tag is a bound parameter and only our
own literals are interpolated — and each suppression carries its reasoning.

**Verified** with `dev.py verify`: 254 backend tests (was 217), 64 frontend (was
54), full gate green. **Not yet clicked through in a browser** — the user's WSL
environment is still the blocker, not the code.

**Outstanding, still:** no real ChatGPT export has been imported. Four
milestones now.

---

## 2026-09-08 — Import ergonomics: the inbox and honest re-import reporting

**Session:** [2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/SESSION.md)
· [prompts](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/PROMPTS.md)
· [report](sessions/2026-09-08-05-import-ergonomics-inbox-and-re-import-reporting/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Milestone 3.5, prompted by the importer having gone three milestones without
seeing a real export. The obstacle was the product, not the code.

**Research corrected the premise** (R-004). OpenAI's own email says an export
"may take a few days". The famous "24 hours" is how long the **download link**
lasts — a deadline, not a wait — and only the most recent request is fulfilled,
so asking twice cancels your own job. Our import panel had that number exactly
backwards. There is no official API for ChatGPT history, so the wait cannot be
automated.

**The inbox** (D-023): drop an export into a folder and it imports itself. No
filesystem watcher — three scan triggers cover it. Configurable to a folder you
already keep exports in, and **that folder is read, never rearranged**; a ledger
remembers instead.

**Honest re-import reporting.** Every export is a full export, so re-importing
now says "12 new, 8 updated, 392 already in your archive", and unchanged
conversations are not rewritten at all.

**The fast path** (D-024): a script the user runs in their own logged-in tab.
No token is pasted anywhere, and Mind Archive never contacts OpenAI. Tools that
ask you to paste a session token are a different and much worse proposition —
that token can send messages as you. Mind Archive calling those endpoints itself
is rejected outright.

**Measuring beat guessing.** A 2,000-conversation import took 194s and looked
like a code problem. It takes 4.7s on the container filesystem and 127s on the
Windows bind mount — **27× slower, same code** (R-005). No optimisation needed;
recorded so nobody optimises the wrong thing later. It did justify moving the
startup scan to a background thread, after an inline version left the server
refusing connections for minutes.

**`inspect_export.py` leaked content in its first draft** by listing archive
filenames — ChatGPT names attachments after what they are. A tool built to avoid
leaking leaked, on draft one.

**Verified**: 217 backend tests (was 197), 54 frontend (was 45), full gate
green, plus 2,000 conversations imported end to end with the API responsive
throughout.

**Outstanding, still:** no real ChatGPT export has been imported. This makes it
cheap rather than replacing it.

---

## 2026-09-08 — Milestone 3: archive browser and search

**Session:** [2026-09-08-04-milestone-3-archive-browser-and-search](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/SESSION.md)
· [prompts](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/PROMPTS.md)
· [index and search notes](sessions/2026-09-08-04-milestone-3-archive-browser-and-search/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

You can now read and search what you imported, rather than opening the files
yourself.

**The index stays honest.** SQLite with FTS5, built three ways from one code
path: at startup when the archive has content but the index does not, on import
through the `conversation.created` event, and on demand. The D-004 rule — the
database is derived, never original — is enforced by
`test_deleting_the_database_loses_nothing`, which deletes it, rebuilds, and
requires identical results.

**Search takes what people type.** `MATCH` is a query language; a search box is
not. `C++`, `NEAR(` and a lone `"` are all FTS5 syntax errors, so input is split
into quoted words joined with `AND`, last word prefixed. All words must match,
the last matches as a prefix, and nothing searchable means no filter rather than
no results (D-022).

**Conversations are rendered as whole Markdown files** (D-020) rather than
parsed back into messages — round-tripping our own rendering would break on a
message containing `## You`, and the file is the readable artefact anyway. Read
from disk, not the index, so a hand-edited file shows immediately.

**Untrusted content cannot become markup.** `react-markdown` with raw HTML off
for bodies (D-021), and `<<`/`>>` delimiters rather than HTML for search
snippets. Both tested with an `<img onerror=...>`.

**A real design flaw, found by a failing test.** The index event handler called
the cached `get_settings()`, so it ignored dependency overrides and indexed the
real archive while the route wrote to a temporary one. Settings are now bound
when the handler is built; `lifespan` had the same problem. Separately, an
unusable archive folder used to crash startup and now logs and continues.

**Verified** with `dev.py verify`: 197 backend tests (was 137), 45 frontend
(was 29), ruff, mypy strict, eslint, tsc, production build — all passed. Also
end-to-end against the running stack: import, list, search, prefix search, read,
rebuild, hostile paths, and the web interface serving.

**Outstanding, unchanged:** no real ChatGPT export has been imported yet.

---

## 2026-09-08 — Milestone 2: the ChatGPT importer

**Session:** [2026-09-08-03-milestone-2-chatgpt-importer](sessions/2026-09-08-03-milestone-2-chatgpt-importer/SESSION.md)
· [prompts](sessions/2026-09-08-03-milestone-2-chatgpt-importer/PROMPTS.md)
· [format and security notes](sessions/2026-09-08-03-milestone-2-chatgpt-importer/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Mind Archive can now archive something.

**The importer interface.** `detect()`, `validate()`, `parse()` and a registry,
so core code never imports a provider module. `parse()` writes nothing — it
returns `Conversation` objects and storing them is the archive's job, which kept
every parser test filesystem-free.

**The ChatGPT parser.** The format's real difficulty is that `mapping` is a
tree, not a list: editing or regenerating a message forks the conversation
rather than replacing anything. Walking up from `current_node` gives what the
person last saw. Abandoned branches are deliberately not imported. Full notes in
the session report.

**Hostile input** is the theme of this milestone. Zip slip, zip bombs, size
caps, and conversation titles that try to escape the archive when they become
folder names. `local/` was created and git-ignored *before* any importer code,
so a real export can never be committed by accident.

**Three real problems found and fixed.** A hostile archive was being reported as
merely "not recognised", which was untrue. The interface showed
`/data/archive` — the path inside the container, which does not exist on the
user's machine; `MIND_ARCHIVE_DISPLAY_DATA_DIR` fixes that. An unwritable
archive folder produced a raw 500 instead of an explanation.

**Verified** with `dev.py verify`: 137 backend tests (was 33), 29 frontend
tests, ruff, mypy strict, eslint, tsc, production build — all passed. Also
tested end-to-end against the running stack with a synthetic export containing a
normal, an awkward and a broken conversation.

**Outstanding:** only synthetic exports have been tested. The user is placing a
real ChatGPT export in `local/`; verifying against it is the next step, before
Milestone 3.

---

## 2026-09-08 — Archive cleanup and developer-controlled workflow

**Session:** [2026-09-08-02-archive-cleanup-and-dev-workflow](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/SESSION.md)
· [prompts](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/PROMPTS.md)
· [archive audit](sessions/2026-09-08-02-archive-cleanup-and-dev-workflow/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

Groundwork before Milestone 2, all from explicit direction.

**`docs/archive/` removed.** Audited all nine files: only `SETUP.md` held
durable content not already in project memory, and it was merged into
`RESEARCH.md` R-002 with the `pc_specs` probe commands. The rest were duplicates
of session 01's verbatim prompts or superseded by the real repository layout.
Deleted rather than kept, because all nine are committed in `fcf1f5c` and so
remain recoverable. Eight files with dangling links now point at that commit.
Also caught a Milestone 1 mistake: `agent-tooling-research.md` was misnamed —
it was a prompt, not research.

**D-018 — verification is developer-controlled.** Tests no longer run on every
change. Required before a milestone completes, before a pull request, and before
a release. Exploratory work is expected to leave the code broken; a slow gate
after every edit gets skipped, which is worse than an explicit one.

**D-019 — Docker containers are disposable.** Checks run in throwaway
containers, `verify` tears the stack down, `clean` removes this project's
images. `./data` is a bind mount, so no cleanup command can touch the archive.

**`scripts/dev.py`** added as the single entry point for both the stack and the
checks. Two small bugs fixed along the way: `slugify` truncated session folder
names mid-word, and `dev.py` emitted ANSI escapes into consoles that cannot
render them.

**Verified** with `dev.py verify`: 33 backend tests, 19 frontend tests, ruff,
mypy strict, eslint, tsc, production build — all passed. The memory check
correctly failed until this session's record was written.

**Next:** Milestone 2, the ChatGPT importer.

---

## 2026-09-08 — Audit and Milestone 1

**Session:** [2026-09-08-01-audit-and-milestone-1](sessions/2026-09-08-01-audit-and-milestone-1/SESSION.md)
· [prompts](sessions/2026-09-08-01-audit-and-milestone-1/PROMPTS.md)
· [audit report](sessions/2026-09-08-01-audit-and-milestone-1/REPORT.md)

**Agent:** Claude Opus 5 (Claude Code)

**Audit findings.** The repository held a strong specification (`MASTER.md`) and
no implementation. All ten `docs/*.md` files, `AGENTS.md` and `README.md` were
0 bytes. `project-memory/` did not exist despite being described as
existing. There was no `.gitignore`, no `.env.example`, and no `LICENSE`. Git
had no commits and no configured `user.name` or `user.email`, so committing was
impossible. About half the repository by size was raw conversation transcript.
`CLAUDE.md` directed agents to read five empty files as the source of truth and
never mentioned `MASTER.md`.

**Measured environment.** Windows 11; Node.js absent on the Windows host and
v24.18.0 in WSL2 (Ubuntu 22.04.2); Python 3.7.9 on Windows and 3.8.10 in WSL2,
both end-of-life; Docker 29.7.2 with Compose v5.4.0, daemon running. Recorded in
[RESEARCH.md](RESEARCH.md) R-001.

**Implemented.** Milestone 1 in full: `.gitignore` first as the priority safety
item; the eight project-memory files; `AGENTS.md` as canonical cross-agent
instructions with `CLAUDE.md`, `GEMINI.md` and `QWEN.md` as pointers; all
product documentation; MIT `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
`CHANGELOG.md`, `.env.example`; a FastAPI backend with health and config
endpoints, typed settings and a small in-process event bus; a React +
TypeScript + Vite single-page workspace with light default and dark toggle;
tests on both sides; Docker and Compose; GitHub Actions CI; a GitHub Pages
documentation foundation.

**Verified by running, not reading.** 33 backend tests, 19 frontend tests, ruff,
mypy strict, eslint, tsc, a production build, both Docker images, the full stack
up with both endpoints answering correctly. Three real bugs surfaced this way
and were fixed — see the session record.

**Decisions recorded.** D-006 Docker as the primary backend path (forced by the
end-of-life local Pythons), D-007 Python 3.11 floor, D-008 plain CSS over a UI
framework, D-009 in-process event bus for V1, D-010 `project-memory/` as
the single memory system, D-015 `main` branch with per-repository git identity,
**D-016 PolyForm Noncommercial 1.0.0 replacing MIT** — decided mid-session,
before anything was published, because licence changes only travel one way —
and D-017 no git remote for now.

**Added on request.** Session memory (`SESSION_PROTOCOL.md`, `sessions/`,
`scripts/session.py`) so no future session depends on a chat history, and
project identity configuration (`project.json`, `scripts/set_identity.py`).

**Repository cleanup.** Durable knowledge was extracted from the planning
transcripts into project memory. The substantive transcripts moved verbatim to
`docs/archive/`; scratch fragments carrying nothing durable were removed.
`MASTER.md` was kept at the root as the founding specification.

**Not done, deliberately.** No importer, archive browser, search, cloud or sync
code — all belong to later milestones.

**Next:** Milestone 2, the ChatGPT importer.
