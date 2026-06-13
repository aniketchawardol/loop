"""Perceptual-hash image similarity (active embedding provider).

A cheap, dependency-free fraud signal: compare buyer-uploaded photos against the
original listing/reference photos. Low similarity can mean a wrong/substituted
item or doctored images; near-identical uploads can mean a reused photo. Real
CLIP/embedding similarity can be slotted in later behind the same interface.

dHash (difference hash) is robust to mild resize/compression — exactly what our
frontend does — while staying sensitive to content changes.
"""

import logging
from io import BytesIO

from django.conf import settings
from django.core.cache import cache

from . import base

log = logging.getLogger(__name__)

_HASH_W, _HASH_H = 9, 8  # 8x8 = 64-bit dHash
_BITS = _HASH_H * (_HASH_W - 1)
_DUP_THRESHOLD = 0.96  # uploads this similar to each other look reused

# dHash is grayscale, so it is blind to colour: a blue vs a silver phone of the
# same shape hash almost identically. We blend in a coarse colour-histogram
# similarity so a colour/material swap (a common return fraud) actually lowers
# the score instead of sailing through.
_COLOR_WEIGHT = 0.45
_COLOR_BINS = 4  # per channel -> 4^3 = 64 buckets


def _dhash(data: bytes) -> str:
    """Return a 64-bit difference hash as a 16-char hex string, or "" on failure."""
    try:
        from PIL import Image

        with Image.open(BytesIO(data)) as im:
            im = im.convert("L").resize((_HASH_W, _HASH_H))
            px = list(im.getdata())
    except Exception:  # noqa: BLE001 — unreadable image -> no signature
        log.warning("dHash failed for an image; skipping", exc_info=True)
        return ""

    bits = 0
    i = 0
    for row in range(_HASH_H):
        base_idx = row * _HASH_W
        for col in range(_HASH_W - 1):
            left = px[base_idx + col]
            right = px[base_idx + col + 1]
            bits = (bits << 1) | (1 if left > right else 0)
            i += 1
    return f"{bits:0{_BITS // 4}x}"


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    dist = bin(int(a, 16) ^ int(b, 16)).count("1")
    return 1.0 - dist / _BITS


def _color_sig(data: bytes):
    """Coarse normalized RGB histogram — a colour fingerprint robust to resize/JPEG.

    Returns a list summing to 1.0, or None if the image can't be read.
    """
    try:
        from PIL import Image

        with Image.open(BytesIO(data)) as im:
            px = list(im.convert("RGB").resize((32, 32)).getdata())
    except Exception:  # noqa: BLE001
        return None
    step = 256 // _COLOR_BINS
    hist = [0] * (_COLOR_BINS ** 3)
    for r, g, b in px:
        idx = (r // step) * _COLOR_BINS * _COLOR_BINS + (g // step) * _COLOR_BINS + (b // step)
        hist[idx] += 1
    total = len(px) or 1
    return [c / total for c in hist]


def _color_similarity(a, b) -> float:
    """Histogram intersection in [0,1]; 1.0 when colour unknown (don't penalize)."""
    if not a or not b:
        return 1.0
    return sum(min(x, y) for x, y in zip(a, b))


def _combined_similarity(dhash_a, color_a, dhash_b, color_b) -> float:
    """Blend structural (dHash) and colour similarity into one 0..1 score."""
    d = _similarity(dhash_a, dhash_b)
    if color_a is None or color_b is None:
        return d
    return (1.0 - _COLOR_WEIGHT) * d + _COLOR_WEIGHT * _color_similarity(color_a, color_b)


def phash_bytes(data: bytes) -> str:
    return _dhash(data)


class PHashEmbedding(base.EmbeddingProvider):
    name = "phash"

    def _ref_phash(self, img: base.GradingImageData) -> str:
        key = f"grading:phash:{img.path}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        h = _dhash(img.data)
        if h:
            cache.set(key, h, getattr(settings, "GRADING_REFERENCE_CACHE_TTL", 86400))
        return h

    def _ref_color(self, img: base.GradingImageData):
        key = f"grading:color:{img.path}"
        cached = cache.get(key)
        if cached is not None:
            return cached
        sig = _color_sig(img.data)
        if sig is not None:
            cache.set(key, sig, getattr(settings, "GRADING_REFERENCE_CACHE_TTL", 86400))
        return sig

    def compare(self, uploaded: list, reference: list) -> dict:
        up = [(u.path, _dhash(u.data), _color_sig(u.data)) for u in uploaded]
        refs = [(self._ref_phash(r), self._ref_color(r)) for r in reference]
        refs = [(h, c) for h, c in refs if h]

        per_image = []
        best_values = []
        for path, h, csig in up:
            best = None
            if h and refs:
                best = max(_combined_similarity(h, csig, rh, rc) for rh, rc in refs)
                best_values.append(best)
            per_image.append(
                {"path": path, "best_similarity": best, "phash": h}
            )

        # Near-duplicate uploads (possible reused photo) — structural dHash only.
        duplicate_pairs = []
        for i in range(len(up)):
            for j in range(i + 1, len(up)):
                hi, hj = up[i][1], up[j][1]
                if hi and hj and _similarity(hi, hj) >= _DUP_THRESHOLD:
                    duplicate_pairs.append([up[i][0], up[j][0]])

        overall = sum(best_values) / len(best_values) if best_values else None
        return {
            "overall": overall,
            "per_image": per_image,
            "reference_phashes": [h for h, _ in refs],
            "duplicate_pairs": duplicate_pairs,
            "source": self.name,
        }
