import numpy as np


def make_synthetic_rf(n_samples=3000, n_features=32, n_activities=4, n_identities=8, seed=42):
    """Synthetic RF-like feature matrix with separable utility and identity components."""
    rng = np.random.default_rng(seed)
    y_activity = rng.integers(0, n_activities, n_samples)
    y_identity = rng.integers(0, n_identities, n_samples)
    activity_centers = rng.normal(0, 1.2, (n_activities, n_features))
    identity_centers = rng.normal(0, 0.45, (n_identities, n_features))
    noise = rng.normal(0, 1.0, (n_samples, n_features))
    X = activity_centers[y_activity] + identity_centers[y_identity] + noise
    return X, y_activity, y_identity
