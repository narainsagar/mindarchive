---
title: Support
permalink: /support/
description: Donate to keep the importers working, and where a licensing question goes.
---

# Support Mind Archive

Mind Archive asks for nothing while you use it — no feature limits, no accounts,
no nags, permanently. Donations are optional and unlock nothing.

{%- comment -%}
  Blank entries in _data/support.yml render nothing, so the page never shows a
  dead payment link.

  Note the comparisons live inside `if`, not `assign`. Liquid's `assign` does
  not evaluate a comparison — `assign x = a != b` does not produce a boolean,
  and an earlier version of this page rendered an "Any amount" button pointing
  at href="" because of exactly that.
{%- endcomment -%}
{% assign donations = site.data.support.donations | where_exp: "d", "d.url != ''" %}
{% assign wallets = site.data.support.crypto | where_exp: "c", "c.address != ''" %}
{% assign custom_url = site.data.support.custom_amount_url %}

## Say thanks

{% if donations.size > 0 or custom_url != "" %}
<div class="tiers">
  {%- for tier in donations -%}
    <a class="tier" href="{{ tier.url }}">
      <span class="tier__emoji" aria-hidden="true">{{ tier.emoji }}</span>
      <span class="tier__amount">${{ tier.amount }}</span>
      <span class="tier__label">{{ tier.label }}</span>
    </a>
  {%- endfor -%}
  {%- if custom_url != "" -%}
    <a class="tier tier--custom" href="{{ custom_url }}">
      <span class="tier__emoji" aria-hidden="true">💛</span>
      <span class="tier__amount">Any amount</span>
      <span class="tier__label">You choose</span>
    </a>
  {%- endif -%}
</div>
{% else %}
> **Donations are not set up yet.** Until they are, the most useful thing you
> can send is a bug report — especially an export that will not import.
> [{{ site.data.support.contact_email }}](mailto:{{ site.data.support.contact_email }})
{% endif %}

**Why it matters.** AI tools change constantly, and provider export formats
change with them. Keeping importers working for ChatGPT, Claude, Gemini and
whatever comes next is ongoing work, not a one-off. Donations fund that
directly.

A donation unlocks nothing. There is nothing to unlock.

{% if wallets.size > 0 %}
### Or send crypto

{% for wallet in wallets %}
<div class="wallet">
  <p class="wallet__label">{{ wallet.label }}</p>
  <code class="wallet__address" id="wallet-{{ forloop.index }}">{{ wallet.address }}</code>
  <button type="button" class="button wallet__copy" data-copy="wallet-{{ forloop.index }}">
    Copy
  </button>
</div>
{% endfor %}

No processor, no account, no third party watching. Gifts only — a licence needs
a buyer we can identify and a receipt we can produce, so those go through
checkout below.
{% endif %}

## Using it at work

**Mind Archive is proprietary software, all rights reserved.** No licence to use
it — at work or anywhere else — is currently granted, and nothing is for sale.

There is no price list, no checkout and no commercial tier, and inventing one
here would be worse than saying so plainly. If you want to use Mind Archive in a
company, write and ask:

> [{{ site.data.support.contact_email }}](mailto:{{ site.data.support.contact_email }}?subject=Licensing%20enquiry)

The position in full is on the
[licensing page]({{ '/licensing/' | relative_url }}).

## What this page does not do

There is **no payment code on this site** — every button above is an ordinary
link to the payment provider's own hosted page. No Stripe script, no PayPal
SDK, no embedded frame. Nothing here watches you, and nothing loads until you
choose to go and pay.

The same rule applies more strictly inside the application: Mind Archive itself
will never contain payment code, phone home, or ask you for money while you are
using it. That is a promise in
[LICENSING.md]({{ '/licensing/' | relative_url }}),
and it is why this page exists instead.

<script>
  // Copy a wallet address. First-party, a few lines, and entirely optional —
  // the address above is selectable text whether or not this runs.
  (function () {
    document.querySelectorAll("[data-copy]").forEach(function (button) {
      button.addEventListener("click", function () {
        var target = document.getElementById(button.getAttribute("data-copy"));
        if (!target) return;
        var text = target.textContent.trim();
        var done = function () {
          var was = button.textContent;
          button.textContent = "Copied";
          setTimeout(function () { button.textContent = was; }, 1500);
        };
        try {
          navigator.clipboard.writeText(text).then(done, function () {});
        } catch (error) {
          // No clipboard access. The address is still there to select.
        }
      });
    });
  })();
</script>
