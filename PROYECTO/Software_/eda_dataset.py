"""
EDA del dataset de latidos por clase AAMI (Persona 2, etapa c).

Para cada base (mitbih, icentia) y split (DS1/DS2) calcula: registros,
pacientes, duración, frecuencia de muestreo, derivación, latidos por clase
(conteo y %), latidos excluidos, y latidos por paciente.

Salidas en eda_output/:
  eda_clases.csv           tabla descriptiva por base y split
  eda_por_registro.csv     latidos por registro/paciente y clase
  eda_clases.md            las mismas tablas en markdown + avisos
  eda_clases_barras.png    latidos por clase, base y split
  eda_latidos_paciente.png latidos por paciente apilados por clase

Uso:
    python eda_dataset.py
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import data_loader as dl  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent / "eda_output"
CLASSES = list(dl.AAMI_CLASSES)

# Paleta categórica (un color fijo por clase; orden de la paleta de referencia)
CLASS_COLORS = {"N": "#2a78d6", "S": "#eb6834", "V": "#1baf7a", "F": "#eda100", "Q": "#e87ba4"}
GROUP_COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e2dc"

SCARCE_PCT = 1.0  # una clase con < 1 % de los latidos se marca como escasa


# --------------------------------------------------------------- datos
def per_record_table(dbs):
    rows = []
    for db in dbs:
        for rec_id in dl.list_records(db):
            split = dl.split_of(db, rec_id)
            if split is None:
                continue
            rec = dl.load_record(db, rec_id)
            counts = pd.Series(rec.ann_aami).value_counts()
            row = {
                "base": db, "split": split, "registro": rec_id,
                "paciente": rec.patient_id, "derivacion": rec.lead,
                "fs_orig_hz": rec.fs_orig, "fs_hz": rec.fs,
                "duracion_min": round(rec.duration_s / 60, 2),
                "latidos": int(len(rec.ann_aami)),
                "excluidos": rec.extra["n_excluidos"],
            }
            for c in CLASSES:
                row[c] = int(counts.get(c, 0))
            rows.append(row)
            print(f"  {db} {rec_id}: {row['latidos']} latidos")
    return pd.DataFrame(rows)


def summary_table(per_rec):
    rows = []
    for (db, split), g in list(per_rec.groupby(["base", "split"])) + [
            ((db, "total"), g) for db, g in per_rec.groupby("base")]:
        n = int(g["latidos"].sum())
        row = {
            "base": db, "split": split,
            "registros": len(g), "pacientes": g["paciente"].nunique(),
            "duracion_h": round(g["duracion_min"].sum() / 60, 2),
            "fs_orig_hz": "/".join(map(str, sorted(g["fs_orig_hz"].unique()))),
            "fs_hz": dl.TARGET_FS,
            "derivacion": "/".join(sorted(g["derivacion"].unique())),
            "latidos": n,
            "latidos_por_paciente_mediana": int(g.groupby("paciente")["latidos"].sum().median()),
            "excluidos": int(g["excluidos"].sum()),
        }
        for c in CLASSES:
            row[c] = int(g[c].sum())
        for c in CLASSES:
            row[f"{c}_%"] = round(100 * row[c] / n, 2) if n else 0.0
        rows.append(row)
    df = pd.DataFrame(rows)
    order = {"DS1": 0, "DS2": 1, "total": 2}
    return df.sort_values(["base", "split"], key=lambda s: s.map(order) if s.name == "split" else s,
                          ignore_index=True)


def warnings(summary):
    out = []
    for _, r in summary[summary["split"] == "total"].iterrows():
        for c in CLASSES:
            if c in dl.EXCLUDED_CLASSES[r["base"]]:
                out.append(f"{r['base']}: la clase {c} se excluye a propósito "
                           f"({r['excluidos']} latidos).")
            elif r[c] == 0:
                out.append(f"{r['base']}: la clase {c} no tiene ningún latido.")
            elif r[f"{c}_%"] < SCARCE_PCT:
                out.append(f"{r['base']}: la clase {c} es escasa ({r[c]} latidos, {r[f'{c}_%']} %).")
    return out


# ------------------------------------------------------------ markdown
def md_table(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def write_markdown(summary, per_rec, warns, path):
    main_cols = ["base", "split", "registros", "pacientes", "duracion_h", "fs_orig_hz",
                 "fs_hz", "derivacion", "latidos", "latidos_por_paciente_mediana", "excluidos"]
    cls = summary[["base", "split"]].copy()
    for c in CLASSES:
        cls[c] = [f"{n} ({p} %)" for n, p in zip(summary[c], summary[f"{c}_%"])]
    text = [
        "# EDA del dataset de latidos (clases AAMI)",
        "",
        "Generado por `python eda_dataset.py`. Todas las señales se usan a 360 Hz y con una "
        "sola derivación (MIT-BIH: MLII; Icentia11k: la única del parche, remuestreada de 250 Hz).",
        "",
        "## Resumen por base y split",
        "",
        md_table(summary[main_cols]),
        "",
        "## Latidos por clase (conteo y %)",
        "",
        md_table(cls),
        "",
        "## Avisos",
        "",
        *[f"- {w}" for w in warns],
        "- MIT-BIH: el registro 202 se excluye de DS2 porque es del mismo paciente que 201 (DS1).",
        "- MIT-BIH: se excluyen los registros con marcapasos (102, 104, 107, 217).",
        "- Icentia11k: se excluyen los latidos `Q` (sin definir/ruido); columna `excluidos`.",
        "- Icentia11k: subconjunto de 30 pacientes (semilla 42), segmento s00; todo es DS2 "
        "(prueba externa entre bases).",
        "",
        "## Latidos por registro",
        "",
        md_table(per_rec[["base", "split", "registro", "paciente", "duracion_min", "latidos",
                          *CLASSES, "excluidos"]]),
        "",
    ]
    path.write_text("\n".join(text), encoding="utf-8")


# ------------------------------------------------------------- figuras
def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def plot_class_bars(summary, path):
    """Una gráfica por clase (escala propia), barras = base/split."""
    groups = summary[summary["split"] != "total"].reset_index(drop=True)
    labels = [f"{'MIT-BIH' if b == 'mitbih' else 'Icentia'} {s}" for b, s in
              zip(groups["base"], groups["split"])]
    fig, axes = plt.subplots(1, len(CLASSES), figsize=(14, 3.8))
    x = np.arange(len(groups))
    for ax, c in zip(axes, CLASSES):
        vals = groups[c].to_numpy()
        ax.bar(x, vals, width=0.7, color=GROUP_COLORS[:len(groups)],
               edgecolor="white", linewidth=2)
        top = max(vals.max(), 1)
        for xi, v, p in zip(x, vals, groups[f"{c}_%"]):
            ax.text(xi, v + 0.02 * top, f"{v:,}\n{p:.2f} %", ha="center", va="bottom",
                    fontsize=7, color=INK)
        ax.set_ylim(0, top * 1.28)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_title(f"Clase {c}", fontsize=10, color=INK, loc="left")
        _style(ax)
    axes[0].set_ylabel("latidos", color=MUTED, fontsize=9)
    fig.suptitle("Latidos por clase AAMI, base y split (cada clase con su propia escala)",
                 fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_beats_per_patient(per_rec, path):
    dbs = list(per_rec["base"].unique())
    fig, axes = plt.subplots(len(dbs), 1, figsize=(14, 3.6 * len(dbs)))
    axes = np.atleast_1d(axes)
    for ax, db in zip(axes, dbs):
        g = per_rec[per_rec["base"] == db].sort_values(["split", "registro"]).reset_index(drop=True)
        x = np.arange(len(g))
        bottom = np.zeros(len(g))
        for c in CLASSES:
            if g[c].sum() == 0:
                continue
            ax.bar(x, g[c], bottom=bottom, width=0.8, color=CLASS_COLORS[c],
                   edgecolor="white", linewidth=0.6, label=c)
            bottom += g[c].to_numpy()
        ax.set_xticks(x)
        ax.set_xticklabels(g["registro"], rotation=90, fontsize=7)
        # separador entre DS1 y DS2
        n1 = int((g["split"] == "DS1").sum())
        if 0 < n1 < len(g):
            ax.axvline(n1 - 0.5, color=MUTED, ls="--", lw=1)
            ax.text(n1 - 0.6, bottom.max() * 1.02, "DS1 ", ha="right", fontsize=8, color=MUTED)
            ax.text(n1 - 0.4, bottom.max() * 1.02, " DS2", ha="left", fontsize=8, color=MUTED)
        name = "MIT-BIH" if db == "mitbih" else "Icentia11k (sin latidos Q)"
        ax.set_title(f"{name}: latidos por registro/paciente", fontsize=10, color=INK, loc="left")
        ax.set_ylabel("latidos", color=MUTED, fontsize=9)
        ax.set_ylim(0, bottom.max() * 1.1)
        ax.legend(title="clase", fontsize=8, title_fontsize=8, frameon=False,
                  loc="upper left", bbox_to_anchor=(1.0, 1.0))
        _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- main
def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--db", nargs="+", default=["mitbih", "icentia"],
                        choices=["mitbih", "icentia"])
    args = parser.parse_args(argv)
    OUT_DIR.mkdir(exist_ok=True)

    print("Cargando registros ...")
    per_rec = per_record_table(args.db)
    summary = summary_table(per_rec)
    warns = warnings(summary)

    per_rec.to_csv(OUT_DIR / "eda_por_registro.csv", index=False)
    summary.to_csv(OUT_DIR / "eda_clases.csv", index=False)
    write_markdown(summary, per_rec, warns, OUT_DIR / "eda_clases.md")
    plot_class_bars(summary, OUT_DIR / "eda_clases_barras.png")
    plot_beats_per_patient(per_rec, OUT_DIR / "eda_latidos_paciente.png")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", None)
    print(summary.to_string(index=False))
    print("\nAvisos:\n  " + "\n  ".join(warns))
    print(f"\nSalidas en {OUT_DIR.name}/")


if __name__ == "__main__":
    main()
