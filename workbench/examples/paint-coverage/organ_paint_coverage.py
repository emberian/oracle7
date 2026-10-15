"""Paint coverage (example specialist): litres of paint for a wall or ceiling from its width and height.
Litres = width x height x coats / spread rate. Spread rate: the one the question gives ("covers 12 square metres per
litre"), else 10 m2 per litre per coat, a typical interior emulsion, and the reply says so. Declines when a size is
missing, zero or negative."""
import re

PAINT = re.compile(r"\bpaint\w*\b", re.I)
DIMS = re.compile(r"(-?\d+(?:\.\d+)?)\s*(m|metres?|meters?|ft|feet|foot)?\s*(?:by|x|\u00d7)\s*(-?\d+(?:\.\d+)?)\s*(m|metres?|meters?|ft|feet|foot)\b", re.I)
COATS = re.compile(r"\b(one|two|three|four|\d+)\s+coats?\b", re.I)
RATE = re.compile(r"covers?\s+(\d+(?:\.\d+)?)\s*(?:m2|m\^2|square met(?:re|er)s?|sq\.? ?m)\s*(?:per|a|/)\s*lit(?:re|er)", re.I)
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4}
FT = 0.3048


def fmt(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


class Organ:
    def answer(self, text, session):
        t = str(text or "")
        if not PAINT.search(t) or not re.search(r"\b(how much|how many lit(?:re|er)s|litres|liters)\b", t, re.I):
            return None
        m = DIMS.search(t)
        if not m:
            return {"kind": "underspecified", "status": "withheld",
                    "response": "Give the width and height (for example 4 m by 2.5 m) and I can work out the litres."}
        w, u1, h, u2 = float(m.group(1)), (m.group(2) or m.group(4)).lower(), float(m.group(3)), m.group(4).lower()
        if w <= 0 or h <= 0:
            return {"kind": "underspecified", "status": "withheld", "response": "A wall's width and height must both be more than zero."}
        if u1.startswith("f"):
            w *= FT
        if u2.startswith("f"):
            h *= FT
        c = COATS.search(t)
        coats = (WORDS.get(c.group(1).lower()) or int(c.group(1))) if c else 1
        r = RATE.search(t)
        rate = float(r.group(1)) if r else 10.0
        area = w * h
        litres = area * coats / rate
        why = "at the %s m2 per litre you gave" % fmt(rate) if r else "at 10 m2 per litre per coat, a typical interior emulsion (check your tin)"
        return {"kind": "litres", "status": "answered",
                "response": "%s litres: %s m2 x %d coat%s, %s." % (fmt(litres), fmt(area), coats, "" if coats == 1 else "s", why)}
