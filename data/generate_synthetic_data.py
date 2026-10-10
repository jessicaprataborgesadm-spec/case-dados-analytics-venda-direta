from pathlib import Path
from datetime import date, timedelta
import csv, random, math

OUT = Path(__file__).resolve().parent
rng = random.Random(20261008)

def write(name, rows, cols):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

cycles = list(range(202501, 202518))
starts = {c: date(2025, 1, 4) + timedelta(days=21*i) for i, c in enumerate(cycles)}
brands = {
    "LUMI": ["PERF", "BODY", "SKIN", "MAKE"],
    "VEL": ["PERF", "BODY", "MAKE"],
    "LUO": ["PERF", "BODY"],
    "NUV": ["MAKE", "SKIN"],
    "PAM": ["BODY", "SKIN"],
}
brand_counts = {"LUMI": 6, "VEL": 5, "LUO": 3, "NUV": 3, "PAM": 3}
materials, sku_brand, prices = [], {}, {}
n = 1001
for b, cats in brands.items():
    for j in range(brand_counts[b]):
        sku = f"SKU{n}"
        cat = cats[j % len(cats)]
        materials.append({"cod_sku": sku, "des_marca": b, "des_categoria": cat})
        sku_brand[sku] = b
        prices[sku] = round(rng.uniform(20, 160), 2)
        n += 1
write("raw_materiais.csv", materials, ["cod_sku", "des_marca", "des_categoria"])

resellers = [f"R{i:04d}" for i in range(1, 61)]
cities = [("Salvador","BA"),("Recife","PE"),("Fortaleza","CE"),("São Paulo","SP"),
          ("Rio de Janeiro","RJ"),("Curitiba","PR"),("Belém","PA"),("Goiânia","GO")]
cadastro = []
for i, r in enumerate(resellers):
    city, state = cities[i % len(cities)]
    year, month, day = rng.randint(1965, 2002), rng.randint(1,12), rng.randint(1,28)
    cadastro.append({"cod_pessoa":r,"des_cidade":city,"des_estado":state,
                     "dt_nascimento":date(year,month,day).isoformat()})
write("raw_cadastro.csv", cadastro, ["cod_pessoa","des_cidade","des_estado","dt_nascimento"])

orders, order_lookup = [], {r:{} for r in resellers}
brand_buyers = {c:{b:set() for b in brands} for c in cycles}
brand_gmv = {c:{b:0.0 for b in brands} for c in cycles}
order_num = 1
for ci, cycle in enumerate(cycles):
    for ri, r in enumerate(resellers):
        base_prob = 0.67 if ri < 16 else (0.44 if ri < 43 else 0.24)
        p = max(0.08, min(0.9, base_prob + 0.035*math.sin(ci*0.9) + (0.07 if cycle==202516 else 0)))
        if rng.random() >= p:
            continue
        order_lookup[r][cycle] = True
        order_id = f"PED-{cycle}-{order_num:05d}"
        order_num += 1
        dt = starts[cycle] + timedelta(days=rng.randint(0,19))
        probs = {"LUMI":.94,"VEL":.58,"LUO":.24,"NUV":.36,"PAM":.17}
        selected = [b for b, prob in probs.items() if rng.random()<prob] or ["LUMI"]
        line_skus = []
        for b in selected:
            possible = [m["cod_sku"] for m in materials if m["des_marca"]==b]
            line_skus.append(rng.choice(possible))
            if rng.random() < .16 and len(possible)>1:
                line_skus.append(rng.choice([s for s in possible if s != line_skus[-1]]))
        for sku in line_skus:
            qty = rng.randint(1,5)
            gross = prices[sku]*qty
            discount = round(gross*rng.uniform(0,.12),2)
            value = round(gross-discount,2)
            b = sku_brand[sku]
            orders.append({"nr_ciclo":cycle,"dt_pedido":dt.isoformat(),"cod_pedido":order_id,
                "cod_rev":r,"des_meio_captacao":rng.choice(["App","ER","Força de Venda"]),
                "cod_sku":sku,"vlr_volume":qty,"vlr_desconto":f"{discount:.2f}","vlr_gmv":f"{value:.2f}"})
            brand_buyers[cycle][b].add(r)
            brand_gmv[cycle][b] += value
write("raw_pedidos.csv", orders, ["nr_ciclo","dt_pedido","cod_pedido","cod_rev",
    "des_meio_captacao","cod_sku","vlr_volume","vlr_desconto","vlr_gmv"])

# Flags demonstrativas, calculadas apenas sobre este histórico sintético.
# Reinício é uma aproximação local: compra após ao menos 7 posições de ciclo sem compra.
base_rows = []
first = {}
for r in resellers:
    prior = [i for i,c in enumerate(cycles) if order_lookup[r].get(c,False)]
    if prior: first[r] = min(prior)
for i, c in enumerate(cycles):
    for r in resellers:
        past = [j for j in range(i) if order_lookup[r].get(cycles[j],False)]
        current = order_lookup[r].get(c,False)
        window = [j for j in range(max(0,i-6),i+1) if order_lookup[r].get(cycles[j],False)]
        if not window:
            continue
        is_start = current and first.get(r)==i
        is_restart = current and bool(past) and i-past[-1]>=7 and not is_start
        last = window[-1]
        is_loss = (not current and last==i-6)
        prior6 = any(order_lookup[r].get(cycles[j],False) for j in range(max(0,i-6),i))
        base_rows.append({"nr_ciclo":c,"cod_rev":r,"flg_base":1,
            "flg_base_ativa":int(prior6),"flg_inicio":int(bool(is_start)),
            "flg_reinicio":int(bool(is_restart)),"flg_perda":int(bool(is_loss))})
write("raw_base.csv", base_rows, ["nr_ciclo","cod_rev","flg_base","flg_base_ativa",
    "flg_inicio","flg_reinicio","flg_perda"])

orders_by_cycle = {}
for o in orders: orders_by_cycle.setdefault(int(o["nr_ciclo"]),[]).append(o)
base_by_cycle = {}
for b in base_rows: base_by_cycle.setdefault(int(b["nr_ciclo"]),[]).append(b)
budget = []
total_metrics = ["base","base_ativa","ativas","inicio","reinicio","perda"]
for c in cycles:
    br = base_by_cycle.get(c,[])
    pr = orders_by_cycle.get(c,[])
    actual = {
        "base":sum(int(x["flg_base"]) for x in br),
        "base_ativa":sum(int(x["flg_base_ativa"]) for x in br),
        "ativas":len(set(x["cod_rev"] for x in pr)),
        "inicio":sum(int(x["flg_inicio"]) for x in br),
        "reinicio":sum(int(x["flg_reinicio"]) for x in br),
        "perda":sum(int(x["flg_perda"]) for x in br)
    }
    for k in total_metrics:
        att = ({"base":1.0264,"base_ativa":1.0296,"ativas":1.0409,
                "inicio":.9756,"reinicio":.9891,"perda":1.0309}[k]
               if c==202516 else rng.uniform(.95,1.07))
        budget.append({"nr_ciclo":c,"des_kpi":k,"des_marca":"total",
                       "vlr_kpi":max(1,round(actual[k]/att))})
    for b in ["LUMI","VEL","LUO","NUV"]:
        gmv = brand_gmv[c][b]
        buyers = len(brand_buyers[c][b])
        if c==202516:
            ga = {"LUMI":.8778,"VEL":.9372,"LUO":1.0183,"NUV":.8834}[b]
            ba = {"LUMI":1.0511,"VEL":1.0118,"LUO":.7271,"NUV":.8239}[b]
        else:
            ga, ba = rng.uniform(.91,1.08), rng.uniform(.92,1.08)
        budget += [
            {"nr_ciclo":c,"des_kpi":"gmv","des_marca":b,"vlr_kpi":f"{max(1,gmv/ga):.2f}"},
            {"nr_ciclo":c,"des_kpi":"compradores","des_marca":b,"vlr_kpi":max(1,round(buyers/ba))}
        ]
write("raw_orcamento.csv", budget, ["nr_ciclo","des_kpi","des_marca","vlr_kpi"])

print("Fontes sintéticas geradas em:", OUT)
for name in ["raw_pedidos.csv","raw_base.csv","raw_materiais.csv","raw_cadastro.csv","raw_orcamento.csv"]:
    with (OUT/name).open(encoding="utf-8") as f: count=sum(1 for _ in f)-1
    print(f"{name}: {count} linhas")
