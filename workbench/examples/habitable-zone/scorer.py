"""scorer - is a reply right for one panel item? Returns (good, asserted).
asserted = the reply gives an answer. For a must-decline item (valid: false) good means it did NOT answer.
A valid item is right when the reply opens with the expected Yes/No (if the item has one) and every number in "a"
appears in the reply within 1%."""
import re

NUM = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")


def ok(item, reply):
    asserted = str(reply.get("status", "")) == "answered"
    if not item.get("valid", True):
        return (not asserted, asserted)
    if not asserted:
        return (False, False)
    text = str(reply.get("response", ""))
    gold = str(item.get("a", ""))
    word = re.match(r"\s*(yes|no)\b", gold, re.I)
    if word and not re.match(r"\W*%s\b" % word.group(1), text, re.I):
        return (False, True)
    gn = [float(x.replace(",", "")) for x in NUM.findall(gold)]
    got = [float(x.replace(",", "")) for x in NUM.findall(text)]
    return (all(any(abs(g - x) <= 0.01 * abs(g) + 0.0006 for x in got) for g in gn), True)
