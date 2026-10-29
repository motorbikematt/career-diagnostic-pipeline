import pytest

import verbatim


@pytest.mark.parametrize("quote, text", [
    ("Managed a smart-camera hardware product",
     "- Managed a smart-camera hardware product from prototype to production"),
    ("cut latency 80%", "- Led the overhaul; **cut latency 80%** in a quarter"),
    ("cut latency by\n80%", "cut latency by   80%"),
    ("Led “discovery” work", 'Led "discovery" work'),
    ("Led the team’s roadmap", "Led the team's roadmap"),
])
def test_matches_despite_markup_whitespace_and_quote_style(quote, text):
    assert verbatim.in_text(quote, text)


@pytest.mark.parametrize("quote, text", [
    ("Shipped 50k units", "Managed a smart-camera product to production"),
    ("cut latency 80%", "Cut latency 80% in a quarter"),                # case matters
    ("grew revenue 3x", "grew revenue 3 times"),
    ("led the team — and the roadmap", "led the team - and the roadmap"),  # dashes matter
    ("", "anything"),
    ("   ", "anything"),
])
def test_does_not_match_changed_words(quote, text):
    assert not verbatim.in_text(quote, text)
