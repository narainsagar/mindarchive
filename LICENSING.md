# Licensing

Mind Archive is **source-available**, not open source. The short version:

| You are | You pay | Under |
|---|---|---|
| A person archiving your own AI conversations | **Nothing, forever** | [PolyForm Noncommercial 1.0.0](LICENSE) |
| A school, charity, public research body or government | **Nothing, forever** | [PolyForm Noncommercial 1.0.0](LICENSE) |
| Someone who wants to support the work anyway | Whatever you like | Optional donation |
| A company or anyone using it commercially | A commercial licence | Contact us |
| Something else entirely | Let's talk | Contact us |

If you are unsure which applies to you, ask. We would much rather answer a
question than have someone quietly get it wrong.

---

## Free — noncommercial use

The whole application, free, no feature limits, no accounts, no nags, under the
[PolyForm Noncommercial License 1.0.0](LICENSE).

**Permitted:** personal use, study, research, experiment, hobby projects, and
use by charitable organisations, educational institutions, public research
organisations, public safety and health organisations, environmental protection
organisations and government institutions — regardless of how they are funded.

You may read the source, run it, modify it, and share your modifications, as
long as the purpose stays noncommercial and you pass these terms along.

## Paid — commercial use

Using Mind Archive as part of a business, or in work you are paid for, needs a
commercial licence.

Planned pricing, once there is a product worth selling:

| | Price | |
|---|---|---|
| **Commercial** | $49 per seat | Perpetual, includes one year of updates |
| **Team** | $39 per seat | 10 seats or more |
| **Enterprise** | Contact us | Site licences, invoicing, custom terms |

Perpetual means the version you buy is yours forever. Renewal only buys
continued updates — which matter here, because AI providers keep changing their
export formats and importers need maintenance.

**Nothing is for sale yet.** Mind Archive is at Milestone 1: a runnable
foundation with no import capability. This section describes the intent so that
anyone reading the source knows where it is going.

## Supporting the project

**The free tier is free forever.** Donating is entirely optional and unlocks
nothing — there are no hidden features, no reminders, and no degraded
experience for people who never pay a penny. That is the deal, permanently.

If Mind Archive is useful to you and you would like it to keep being developed,
there will be a simple way to say so:

| | |
|---|---|
| ☕ **Buy a coffee** | $5 |
| 🍺 **Buy a beer** | $10 |
| 🍕 **Buy lunch** | $15 |
| 🍽️ **Buy dinner** | $20 |
| 💛 **Something else** | Any amount you choose |

Why it matters: AI tools change constantly, and provider export formats change
with them. Keeping importers working for ChatGPT, Claude, Gemini and whatever
comes next is ongoing work, not a one-off. Donations fund that work directly.

Donations will be handled on the project website, not inside the application.
Mind Archive itself will never contain payment code, phone home, or ask you for
money while you are using it.

That promise is kept literally, and it is checked. The Support panel in the
application holds one link to the website and nothing else — no provider, no
amounts, no checkout — and a test fails if any payment provider's name ever
appears in the interface. The website's donate page is only links to hosted
checkout: no Stripe script, no PayPal SDK, no embedded frame, so nothing on it
watches you before you choose to go and pay. See decision D-038.

## Why not MIT or Apache?

Mind Archive should be readable, inspectable, forkable and trustworthy — you are
handing it your private conversations, and you should be able to check what it
does with them. Source-available gives you all of that.

What it does not give away is the right for someone else to sell your work back
to you. A fully permissive licence would, and the project needs to be able to
sustain itself.

This is a deliberate trade-off, made with open eyes. See
[project-memory/DECISIONS.md](project-memory/DECISIONS.md) D-012.

## Might this become open source later?

Possibly, and the direction is deliberately kept open.

A licence can always be relaxed — restrictive to permissive — but never
tightened, because any version already published under a permissive licence
stays that way forever. Starting here keeps both futures available; starting at
MIT would have closed one of them permanently.

The [Functional Source License](https://fsl.software) was considered as an
alternative: it permits commercial use except for building a competing product,
and converts automatically to MIT or Apache 2.0 after two years. It remains the
most likely route if Mind Archive moves toward open source.

FSL and PolyForm Noncommercial cannot both apply at once. FSL is strictly more
permissive, so offering a choice between them would mean every commercial user
simply chose FSL — the noncommercial terms would never apply to anyone.

## Contributing

Contributions are welcome. Because commercial licences are sold, contributors
will be asked to sign a Contributor Licence Agreement before their first
contribution is merged, granting the rights needed to include their work in a
commercially licensed release.

The CLA is not written yet — no outside contributions are being accepted at this
stage. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Your data is yours regardless

None of this touches your archive. Your conversations, notes and files are
yours, stored as ordinary readable files on your own computer, exportable at any
time, under every tier including the free one. Licensing governs the software,
never your data.

## Contact

Open an issue for licensing questions that are not confidential, or contact the
maintainers directly for commercial enquiries, custom terms, or anything the
tiers above do not cover.

---

*This document explains the licence in plain language. Where it and
[LICENSE](LICENSE) differ, LICENSE governs. It is not legal advice.*
