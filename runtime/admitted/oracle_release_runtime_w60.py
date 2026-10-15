#!/usr/bin/env python3
"""oracle_release_runtime_w60 - CORRECTNESS RELEASE: a refusal is not a missing warrant.

The justification fold reads the previous turn's record and reports the warrant it
finds. Asked "how did you get that" after a turn where the machine DECLINED, it
found no warrant, because nothing had been asserted, and reported:

    my record for it holds no warrant of any kind, neither a citation nor a check
    I can replay. I should not have presented it as settled.

Every clause of that is false about a refusal. Nothing was presented. Nothing was
settled. The turn was the machine working correctly, and its own account of itself
called it a lapse.

This is the second time in one day that the justification fold has been wrong in
the same direction, and the direction is worth naming: it was written to catch a
machine overclaiming, so when it meets a turn that claimed nothing it reads the
absence of a warrant as the absence of grounds. The first case was citation, where
the warrant was real and in a different field. This case is refusal, where there
is correctly no warrant at all and the right report is why there is none.

A turn is now read by its STATUS first and its warrant second:

    answered  + warrant     report the warrant, as before
    answered  + citations   report the source, as w58 already did
    withheld                report that it declined, and say a refusal has no
                            working to show, because that is the honest account
    answered  + nothing     the original complaint, which remains correct in the
                            one case it was written for

Hand-authored 2026-08-28. Judged by the gate.
"""

from __future__ import annotations

from oracle_release_runtime_w59 import OracleReleaseRuntimeW59

_REFUSAL_TAILS = ('does_not_follow', 'out_of_fragment', 'unverified',
                  'no_primitive', 'unsupported')


class OracleReleaseRuntimeW60(OracleReleaseRuntimeW59):
    """Justification that can tell an absent answer from an ungrounded one."""

    @staticmethod
    def _was_refusal(prior):
        if str(prior.get('out_status', '')) == 'withheld':
            return True
        return str(prior.get('operator', '')).endswith(_REFUSAL_TAILS)

    def _justify(self, kind, prior):
        if kind in ('how_got', 'what_did') and self._was_refusal(prior):
            op = str(prior.get('operator', '') or 'an unrecorded route')
            if kind == 'how_got':
                return ('I did not work that one out, I declined it. A refusal has '
                        'no working to show, which is the point of it: I stopped '
                        'because I had no way to check an answer, so there is no '
                        'answer of mine to account for. My record marks that turn '
                        'as withheld by %s. [self:witness]' % op)
            return ('That turn was a refusal rather than an answer. %s took it, '
                    'found it outside what it can check, and withheld rather than '
                    'producing something neither of us could verify. '
                    '[self:witness]' % op)
        return super()._justify(kind, prior)
