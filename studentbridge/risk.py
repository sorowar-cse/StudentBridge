"""Isolation Forest plus split-conformal anomaly ranks.

Training/calibration examples are explicitly synthetic normal student transfers.
The output is an anomaly rank under that synthetic distribution, not a fraud
probability. It supplements fixed limits and cannot authorize an action.
"""

import math
import numpy as np
from sklearn.ensemble import IsolationForest


def features(usd, hour, new_recipient, recent_count):
    return [
        math.log1p(float(usd)),
        math.sin(2 * math.pi * hour / 24),
        math.cos(2 * math.pi * hour / 24),
        float(bool(new_recipient)),
        min(float(recent_count), 100),
    ]


def normal_samples(seed, size):
    rng = np.random.default_rng(seed)
    return np.array(
        [
            features(min(x, 1700), h, n, c)
            for x, h, n, c in zip(
                rng.lognormal(4.8, 0.9, size),
                rng.integers(0, 24, size),
                rng.binomial(1, 0.25, size),
                rng.poisson(0.7, size),
            )
        ]
    )


class RiskEngine:
    def __init__(self, alpha=0.01):
        self.alpha = alpha
        self.model = IsolationForest(
            n_estimators=160, random_state=20261012, contamination="auto", n_jobs=1
        ).fit(normal_samples(401, 1200))
        # Independent seed and sample set; calibration is never used to train the forest.
        self.calibration = -self.model.score_samples(normal_samples(402, 800))

    def assess(self, usd, hour, new_recipient=False, recent_count=0):
        score = float(
            -self.model.score_samples([features(usd, hour, new_recipient, recent_count)])[0]
        )
        p_value = float(
            (1 + np.count_nonzero(self.calibration >= score)) / (len(self.calibration) + 1)
        )
        fixed = []
        if float(usd) > 2000:
            fixed.append("Exceeds sandbox per-transfer limit of USD 2,000 equivalent")
        if recent_count >= 5:
            fixed.append("Too many completed transfers in the last 30 minutes")
        anomaly = p_value <= self.alpha
        return {
            "score": round(score, 6),
            "conformal_p": round(p_value, 6),
            "alpha": self.alpha,
            "anomaly": anomaly,
            "blocked": bool(fixed) or anomaly,
            "reasons": fixed
            + (
                ["Outside synthetic normal-transfer distribution; review required"]
                if anomaly
                else []
            ),
            "training": "Synthetic only; not a trained real-world fraud detector",
        }

    def evaluate(self, size=500):
        held_out = normal_samples(403, size)
        scores = -self.model.score_samples(held_out)
        p = np.array(
            [
                (1 + np.count_nonzero(self.calibration >= s)) / (len(self.calibration) + 1)
                for s in scores
            ]
        )
        abnormal = np.array(
            [features(10000 + i * 100, i % 24, True, 10 + i % 10) for i in range(100)]
        )
        scores_a = -self.model.score_samples(abnormal)
        pa = [
            (1 + np.count_nonzero(self.calibration >= s)) / (len(self.calibration) + 1)
            for s in scores_a
        ]
        return {
            "normal_test_n": size,
            "normal_flag_rate": float(np.mean(p <= self.alpha)),
            "constructed_anomaly_n": 100,
            "constructed_anomaly_flag_rate": float(np.mean(np.array(pa) <= self.alpha)),
            "scope": "Synthetic held-out seed 403; no real fraud detection claim",
        }
