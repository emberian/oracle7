"""scorer - is a reply right for one panel item? Returns (good, asserted).
asserted = the reply gives an answer. For a must-decline item (valid: false) good means it did NOT answer.
A valid item is right when every number in "a" appears in the reply (within 1%) or, for words, the reply contains "a"."""
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
    gn = [float(x.replace(",", "")) for x in NUM.findall(gold)]
    if gn:
        got = [float(x.replace(",", "")) for x in NUM.findall(text)]
        return (all(any(abs(g - x) <= 0.01 * max(1.0, abs(g)) for x in got) for g in gn), True)
    return (gold.lower() in text.lower(), True)
