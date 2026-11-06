"""Pruebas mínimas del loader: mapeo AAMI y split por paciente sin fugas."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import data_loader as dl  # noqa: E402


# ---------------------------------------------------------------- AAMI
@pytest.mark.parametrize("sym,cls", [
    ("N", "N"), ("L", "N"), ("R", "N"), ("e", "N"), ("j", "N"),
    ("A", "S"), ("a", "S"), ("J", "S"), ("S", "S"),
    ("V", "V"), ("E", "V"),
    ("F", "F"),
    ("/", "Q"), ("f", "Q"), ("Q", "Q"),
])
def test_aami_beats(sym, cls):
    assert dl.symbol_to_aami(sym) == cls


@pytest.mark.parametrize("sym", list(dl.NON_BEAT_SYMBOLS) + ["?", ""])
def test_aami_non_beats_ignored(sym):
    assert dl.symbol_to_aami(sym) is None


def test_aami_only_valid_classes():
    assert set(dl.AAMI_MAP.values()) == set(dl.AAMI_CLASSES)


def test_beats_only_filters_and_maps():
    samples, symbols, aami = dl._beats_only([10, 20, 30, 40, 50], ["N", "+", "V", "~", "A"])
    assert samples.tolist() == [10, 30, 50]
    assert symbols.tolist() == ["N", "V", "A"]
    assert aami.tolist() == ["N", "V", "S"]


# --------------------------------------------------------------- split
@pytest.mark.parametrize("db", ["mitbih", "icentia"])
def test_no_patient_in_both_splits(db):
    ds1, ds2 = dl.get_split(db)
    p1 = {dl.get_patient_id(db, r) for r in ds1}
    p2 = {dl.get_patient_id(db, r) for r in ds2}
    assert p1.isdisjoint(p2)


def test_original_de_chazal_split_leaks_201_202():
    # Documenta por qué strict=True es el valor por defecto.
    ds1, ds2 = dl.get_split("mitbih", strict=False)
    p1 = {dl.get_patient_id("mitbih", r) for r in ds1}
    p2 = {dl.get_patient_id("mitbih", r) for r in ds2}
    assert p1 & p2 == {"201"}


def test_mitbih_split_excludes_paced_and_sizes():
    ds1, ds2 = dl.get_split("mitbih")
    assert not set(dl.MITBIH_PACED) & (set(ds1) | set(ds2))
    assert len(ds1) == 22 and len(ds2) == 21
    assert set(ds1).isdisjoint(ds2)


def test_icentia_subset_stable():
    assert len(dl.list_records("icentia")) == 30
    assert len(set(dl.ICENTIA_SUBSET)) == 30


def test_resample_250_to_360():
    x = np.sin(2 * np.pi * 1.0 * np.arange(2500) / 250)  # 10 s
    y = dl._resample(x, 250, 360)
    assert len(y) == 3600


# ------------------------------------- carga real (solo si hay datos)
def _have(db, rec):
    base, _, _ = dl._local_base(db, rec)
    return all(base.with_suffix(e).exists() for e in (".hea", ".dat", ".atr"))


@pytest.mark.skipif(not _have("mitbih", "114"), reason="registro 114 no descargado")
def test_mitbih_114_uses_mlii_channel():
    rec = dl.load_record("mitbih", "114")
    assert rec.lead == "MLII" and rec.fs == 360 and rec.signal.ndim == 1
    assert set(rec.ann_aami) <= set(dl.AAMI_CLASSES)


@pytest.mark.skipif(not _have("icentia", dl.ICENTIA_SUBSET[0]), reason="icentia no descargada")
def test_icentia_resampled_to_360():
    rec = dl.load_record("icentia", dl.ICENTIA_SUBSET[0])
    assert rec.fs == 360 and rec.fs_orig == 250
    assert rec.ann_samples.max() < len(rec.signal)
    assert "Q" not in set(rec.ann_aami)  # Q de Icentia excluida
    assert rec.extra["n_excluidos"] == len(rec.extra["excluded_samples"])
    full = dl.load_record("icentia", dl.ICENTIA_SUBSET[0], drop_excluded=False)
    assert len(full.ann_aami) == len(rec.ann_aami) + rec.extra["n_excluidos"]
