"""Habitable zone (example specialist), from Kopparapu et al. 2013 (ApJ 765, 131, erratum values).

The zone's edges are limits on the starlight a planet receives (S, in units of Earth's), each a polynomial in the
star's effective temperature T: S = S0 + a t + b t^2 + c t^3 + d t^4, t = T - 5780 K. Valid for 2600-7200 K.
  conservative zone: runaway greenhouse (inner) to maximum greenhouse (outer)
  optimistic zone:   recent Venus (inner) to early Mars (outer)
Distance of an edge = sqrt(L / S) AU, L in solar luminosities. A planet's S = L / d^2, or the share of Earth's sunlight
the question gives. Answers: the edges in AU for a star, or yes/no for a planet. Declines a star outside 2600-7200 K, a
missing temperature or luminosity, and any size that is zero or negative."""
import math
import re

LIMITS = {"recent Venus": (1.7753, 1.4316e-4, 2.9875e-9, -7.5702e-12, -1.1635e-15),
          "runaway greenhouse": (1.0512, 1.3242e-4, 1.5418e-8, -7.9895e-12, -1.8328e-15),
          "maximum greenhouse": (0.3438, 5.8942e-5, 1.6558e-9, -3.0045e-12, -5.2983e-16),
          "early Mars": (0.3179, 5.4513e-5, 1.5313e-9, -2.7786e-12, -4.8997e-16)}
NUM = r"(-?\d[\d,]*(?:\.\d+)?)"
HZ = re.compile(r"\bhabitable\s+zone\b", re.I)
TEMP = re.compile(NUM + r"\s*(?:K|kelvin)\b", re.I)
LUM = re.compile(NUM + r"\s*(?:times the sun'?s luminosity|solar luminosit(?:y|ies)|L_?sun\b|L\u2609)", re.I)
DIST = re.compile(NUM + r"\s*(?:AU|astronomical units?)\b", re.I)
FLUX = re.compile(NUM + r"\s*times (?:(?:the )?Earth'?s? (?:sunlight|insolation|stellar flux|flux|irradiation)|the (?:stellar flux|insolation|flux|sunlight) (?:that )?Earth (?:gets|receives))", re.I)


def val(m):
    return float(m.group(1).replace(",", "")) if m else None


def seff(name, teff):
    s0, a, b, c, d = LIMITS[name]
    t = teff - 5780.0
    return s0 + a * t + b * t ** 2 + c * t ** 3 + d * t ** 4


def f(x, n=2):
    return "{:,.{n}f}".format(x, n=n)


class Organ:
    def answer(self, text, session):
        q = str(text or "")
        if not HZ.search(q):
            return None
        teff, lum, dist, flux = val(TEMP.search(q)), val(LUM.search(q)), val(DIST.search(q)), val(FLUX.search(q))
        if teff is None:
            return {"kind": "underspecified", "status": "withheld",
                    "response": "Give the star's temperature (for example 3,400 K) and I can place its habitable zone."}
        if not 2600 <= teff <= 7200:
            return {"kind": "out_of_range", "status": "withheld",
                    "response": "The habitable-zone formulas I use (Kopparapu et al. 2013) are fitted for stars of 2,600-7,200 K; %s K is outside them, so I won't guess." % f(teff, 0)}
        if any(x is not None and x <= 0 for x in (lum, dist, flux)):
            return {"kind": "underspecified", "status": "withheld", "response": "A luminosity, distance or share of sunlight must be more than zero."}
        S = {k: seff(k, teff) for k in LIMITS}
        star = "%s K star" % f(teff, 0)
        if flux is None and dist is not None and lum is not None:
            flux = lum / dist ** 2
        if flux is not None:
            opt = S["early Mars"] <= flux <= S["recent Venus"]
            cons = S["maximum greenhouse"] <= flux <= S["runaway greenhouse"]
            where = ("inside the conservative zone" if cons else "inside the optimistic zone only") if opt else \
                ("too much starlight: inside the inner edge" if flux > S["recent Venus"] else "too little starlight: beyond the outer edge")
            return {"kind": "inside", "status": "answered",
                    "response": "%s: it receives %s times Earth's sunlight, %s. For a %s the conservative zone runs from %s to %s times Earth's sunlight, the optimistic zone from %s to %s (Kopparapu et al. 2013)." % (
                        "Yes" if opt else "No", f(flux), where, star, f(S["runaway greenhouse"]), f(S["maximum greenhouse"]), f(S["recent Venus"]), f(S["early Mars"]))}
        if lum is None:
            return {"kind": "underspecified", "status": "withheld",
                    "response": "Give the star's luminosity (for example 0.02 solar luminosities) and I can give the zone's edges in AU."}
        au = {k: math.sqrt(lum / s) for k, s in S.items()}
        return {"kind": "zone", "status": "answered",
                "response": "For a %s of %s solar luminosities, the conservative habitable zone runs from %s to %s AU (runaway greenhouse to maximum greenhouse); the optimistic zone from %s to %s AU (recent Venus to early Mars). Kopparapu et al. 2013." % (
                    star, f(lum, 4).rstrip("0").rstrip("."), f(au["runaway greenhouse"], 3), f(au["maximum greenhouse"], 3), f(au["recent Venus"], 3), f(au["early Mars"], 3))}
