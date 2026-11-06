"""Pruebas del emparejamiento pico-anotación y del pipeline de build_features."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import build_features as bf  # noqa: E402
import data_loader as dl  # noqa: E402
from validation import match_beats, match_indices  # noqa: E402


def test_match_indices_basic():
    ref = np.array([100, 400, 700, 1000])
    det = np.array([105, 395, 550, 1030])  # 550 = FP; 700 no detectado; 1030 fuera de tol
    out = match_indices(det, ref, tol=18)
    assert out.tolist() == [0, 1, -1, -1]


def test_match_indices_one_to_one():
    ref = np.array([100, 110])
    det = np.array([104])
    assert match_indices(det, ref, tol=18).tolist() == [0] or \
        match_indices(det, ref, tol=18).tolist() == [1]
    assert (match_indices(det, ref, tol=18) >= 0).sum() == 1


def test_match_beats_unchanged():
    ref = np.array([100, 400, 700])
    det = np.array([102, 550, 698])
    used, ref_matched = match_beats(det, ref, tol=18)
    assert used.tolist() == [True, False, True]
    assert ref_matched.tolist() == [True, False, True]


def _have(db, rec):
    base, _, _ = dl._local_base(db, rec)
    return all(base.with_suffix(e).exists() for e in (".hea", ".dat", ".atr"))


@pytest.mark.skipif(not _have("mitbih", "100"), reason="registro 100 no descargado")
def test_process_record_gt_columns():
    df, log = bf.process_record("mitbih", "100", "DS2", None, tol=18)
    assert list(df.columns) == bf.COLUMNS
    assert log is None
    assert set(df["clase_aami"]) <= set(dl.AAMI_CLASSES)
    assert df["beat_idx"].is_monotonic_increasing


@pytest.mark.skipif(not _have("mitbih", "100"), reason="registro 100 no descargado")
def test_process_record_with_fake_detector():
    rec = dl.load_record("mitbih", "100")
    ann = rec.ann_samples

    def fake_detector(signal, fs):
        # desplaza 5 muestras, pierde el latido 10 y añade un FP entre 20 y 21
        peaks = np.delete(ann + 5, 10)
        return np.sort(np.append(peaks, (ann[20] + ann[21]) // 2)), None

    df, log = bf.process_record("mitbih", "100", "DS2", fake_detector, tol=18)
    assert log["no_detectados"] == 1
    assert log["falsos_positivos"] == 1
    assert len(df) == len(ann) - 1
    assert (df["r_sample"].to_numpy() == np.delete(ann + 5, 10)).all()
    assert (df["clase_aami"].to_numpy() == np.delete(rec.ann_aami, 10)).all()
    # el FP no aparece pero sí cuenta para los RR: hay un hueco en beat_idx
    assert df["beat_idx"].diff().max() == 2
