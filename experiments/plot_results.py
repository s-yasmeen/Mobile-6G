from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
p=Path("outputs"); files=list(p.glob("cumulative_*.csv"));
if not files: raise SystemExit("Run cumulative experiments first.")
df=pd.concat([pd.read_csv(f) for f in files],ignore_index=True)
for name,g in df.groupby("sanitizer"):
    plt.plot(g.release_count,g.identity_macro_auc,marker="o",label=name)
plt.axhline(.60,linestyle="--",label="allow threshold"); plt.axhline(.75,linestyle=":",label="block threshold")
plt.xscale("log"); plt.xlabel("Repeated releases (K)"); plt.ylabel("Identity attacker macro ROC-AUC"); plt.legend(); plt.tight_layout(); plt.savefig(p/"privacy_vs_releases.png",dpi=200); print(p/"privacy_vs_releases.png")
