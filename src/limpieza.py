"""Limpieza: data/raw/*.xlsx -> data/processed/subidas_limpio.parquet (+ log de decisiones)."""
import pandas as pd, json, pathlib
RAW = pathlib.Path("data/raw/Subidas_Paradero_Estacion_2026_04_v3__1_.xlsx")
OUT = pathlib.Path("data/processed")
FUERA = ["LAMPA", "PADRE HURTADO", "COLINA", "PIRQUE", "BUIN", "SIN_COMUNA"]

def limpiar():
    d = pd.read_excel(RAW, sheet_name="SUBIDAS_2026_04")
    log = {"filas_originales": len(d), "nulos": int(d.isna().sum().sum()),
           "duplicados": int(d.duplicated().sum())}
    d = d.rename(columns={"Paradero Usuario": "SIMIT"})
    d["Modo"] = d["Modo"].replace({"BUS": "Bus", "Tren": "Metrotren"})
    d["Tipo_dia"] = d["Tipo_dia"].str.capitalize().replace({"Sabado": "Sábado"})
    d["Comuna"] = d["Comuna"].str.title()
    fuera = [c.title() for c in FUERA]
    log["filas_fuera_alcance"] = int(d["Comuna"].isin(fuera).sum())
    d = d[~d["Comuna"].isin(fuera)].copy()
    d["Media_hora"] = d["Media_hora"].astype(str).str[:5]
    d["Hora"] = d["Media_hora"].str[:2].astype(int) + (d["Media_hora"].str[3:] == "30") * 0.5
    d["Tipo_dia"] = pd.Categorical(d["Tipo_dia"], ["Laboral", "Sábado", "Domingo"])
    for c in ["Modo", "Comuna", "Media_hora"]:
        d[c] = d[c].astype("category")
    log["filas_finales"] = len(d)
    log["paraderos_finales"] = int(d["Paradero"].nunique())
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_parquet(OUT / "subidas_limpio.parquet", index=False)
    json.dump(log, open(OUT / "log_limpieza.json", "w"), indent=2)
    return d, log

if __name__ == "__main__":
    print(limpiar()[1])
