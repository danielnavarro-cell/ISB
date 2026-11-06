"""
Reproduce todo lo de datos y features con un solo comando:

    python reproduce.py

Pasos: descarga MIT-BIH y el subconjunto de Icentia11k (una vez) -> tests ->
EDA (eda_output/) -> CSV v1 con picos de referencia (features_out/) -> CSV con
los detectores de P1 que ya existan en peak_detection.py.
"""
import subprocess
import sys

import build_features
import data_loader as dl
import eda_dataset
import peak_detection


def main():
    for db in ("mitbih", "icentia"):
        print(f"[1/4] Descargando {db} (si falta) ...")
        dl.download_all(db)

    print("[2/4] Tests ...")
    if subprocess.call([sys.executable, "-m", "pytest", "-q", "tests"]) != 0:
        sys.exit("Fallaron los tests; no se generan los CSV.")

    print("[3/4] EDA ...")
    eda_dataset.main([])

    print("[4/4] Features ...")
    for db in ("mitbih", "icentia"):
        build_features.build(db, "gt")
        for det, fn_name in build_features.DETECTORS.items():
            if hasattr(peak_detection, fn_name):
                build_features.build(db, det)
            else:
                print(f"  (se omite {det}: peak_detection.{fn_name} aún no existe)")


if __name__ == "__main__":
    main()
