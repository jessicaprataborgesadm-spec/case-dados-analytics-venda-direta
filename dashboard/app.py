from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------
# Dashboard demonstrativo para portfólio.
# Lê somente CSVs sintéticos do diretório /data do repositório.
# A lógica de consulta/modelagem também está documentada em /sql.
# ---------------------------------------------------------------------
APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
DATA = ROOT / "data"

st.set_page_config(
    page_title="Venda Direta | Performance Analytics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#142B49"
BLUE = "#2F5D7C"
BLUE_LIGHT = "#DDE6ED"
PINK = "#D84079"
PINK_LIGHT = "#F7E5ED"
GREEN = "#25836D"
AMBER = "#C17B2D"
INK = "#1F2E40"
MUTED = "#718096"
PAPER = "#F6F5F1"
WHITE = "#FFFFFF"
GRID = "#E5E8EC"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
    .stApp {{ background: {PAPER}; color: {INK}; }}
    [data-testid="stSidebar"] {{ background: {NAVY}; }}
    [data-testid="stSidebar"] * {{ color: #F5F7FA; }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{ padding: 7px 8px; }}
    .block-container {{ padding-top: 1.45rem; padding-bottom: 2.25rem; max-width: 1440px; }}
    h1, h2, h3 {{ font-family: 'Manrope', sans-serif; letter-spacing: -0.035em; }}
    h1 {{ color: {NAVY}; font-size: 2.15rem; font-weight: 800; }}
    h2 {{ color: {NAVY}; font-size: 1.28rem; font-weight: 750; }}
    h3 {{ color: {NAVY}; font-size: 1.02rem; font-weight: 700; }}
    [data-testid="stMetric"] {{ background: {WHITE}; padding: 17px 18px; border: 1px solid #E6E8EB; border-radius: 16px; box-shadow: 0 5px 18px rgba(20,43,73,.045); }}
    [data-testid="stMetricLabel"] {{ color: {MUTED}; font-size: .78rem; font-weight: 700; text-transform: uppercase; }}
    [data-testid="stMetricValue"] {{ color: {NAVY}; font-family: 'Manrope', sans-serif; font-weight: 800; }}
    .eyebrow {{ color: {PINK}; font-weight: 800; font-size: .73rem; letter-spacing: .12em; text-transform: uppercase; }}
    .lede {{ font-size: 1rem; line-height: 1.55; color: #526174; margin-top: -.25rem; margin-bottom: 1.0rem; }}
    .section-card {{ background: {WHITE}; padding: 20px 22px; border: 1px solid #E4E7EB; border-radius: 17px; box-shadow: 0 5px 18px rgba(20,43,73,.035); }}
    .insight {{ background: {NAVY}; color: #F8FAFC; border-radius: 18px; padding: 21px 24px; border-left: 5px solid {PINK}; margin: 8px 0 18px 0; }}
    .insight strong {{ color: #FFFFFF; font-size: 1.02rem; }}
    .insight p {{ color: #D8E1EB; margin: 7px 0 0 0; line-height: 1.55; }}
    .tag {{ display:inline-block; background:{PINK_LIGHT}; color:{PINK}; border-radius: 999px; padding: 5px 10px; font-size:.72rem; font-weight:800; letter-spacing:.03em; }}
    .note {{ color: {MUTED}; font-size: .78rem; line-height: 1.5; }}
    .step-num {{ color:{PINK}; font-weight:800; font-size:.75rem; letter-spacing:.1em; }}
    div[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def read_sources():
    required = [
        "raw_pedidos.csv", "raw_base.csv", "raw_materiais.csv",
        "raw_cadastro.csv", "raw_orcamento.csv"
    ]
    missing = [f for f in required if not (DATA / f).exists()]
    if missing:
        raise FileNotFoundError(
            "Não encontrei: " + ", ".join(missing) +
            f". A aplicação espera estes arquivos dentro de {DATA}."
        )

    pedidos = pd.read_csv(DATA / "raw_pedidos.csv")
    base = pd.read_csv(DATA / "raw_base.csv")
    materiais = pd.read_csv(DATA / "raw_materiais.csv")
    cadastro = pd.read_csv(DATA / "raw_cadastro.csv")
    orcamento = pd.read_csv(DATA / "raw_orcamento.csv")

    for frame in [pedidos, base, orcamento]:
        frame["nr_ciclo"] = pd.to_numeric(frame["nr_ciclo"], errors="coerce").astype("Int64")
    for col in ["vlr_gmv", "vlr_volume", "vlr_desconto"]:
        pedidos[col] = pd.to_numeric(pedidos[col], errors="coerce")
    orcamento["vlr_kpi"] = pd.to_numeric(orcamento["vlr_kpi"], errors="coerce")
    for col in ["flg_base", "flg_base_ativa", "flg_inicio", "flg_reinicio", "flg_perda"]:
        base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0).astype(int)
    return pedidos, base, materiais, cadastro, orcamento

@st.cache_data
def build_analytics():
    pedidos, base, materiais, cadastro, orcamento = read_sources()
    pedidos = pedidos.merge(materiais, on="cod_sku", how="left", validate="many_to_one")

    cycles = sorted(set(pedidos["nr_ciclo"].dropna().astype(int)) |
                    set(base["nr_ciclo"].dropna().astype(int)))

    channel = (
        pedidos.groupby("nr_ciclo", as_index=False)
        .agg(
            gmv=("vlr_gmv", "sum"),
            volume=("vlr_volume", "sum"),
            ativas=("cod_rev", "nunique"),
        )
    )
    pop = (
        base.groupby("nr_ciclo", as_index=False)
        .agg(
            base=("flg_base", "sum"),
            base_ativa=("flg_base_ativa", "sum"),
            inicio=("flg_inicio", "sum"),
            reinicio=("flg_reinicio", "sum"),
            perda=("flg_perda", "sum"),
        )
    )
    channel = pd.DataFrame({"nr_ciclo": cycles}).merge(channel, on="nr_ciclo", how="left").merge(
        pop, on="nr_ciclo", how="left"
    ).fillna(0)
    channel["atividade"] = channel["ativas"].div(channel["base"].replace(0, pd.NA))
    channel["atividade_base_ativa"] = (
        channel["ativas"] - channel["inicio"] - channel["reinicio"]
    ).div(channel["base_ativa"].replace(0, pd.NA))
    channel["rpa"] = channel["gmv"].div(channel["ativas"].replace(0, pd.NA))
    channel["upa"] = channel["volume"].div(channel["ativas"].replace(0, pd.NA))

    by_brand = (
        pedidos.groupby(["nr_ciclo", "des_marca"], as_index=False)
        .agg(
            gmv=("vlr_gmv", "sum"),
            volume=("vlr_volume", "sum"),
            pedidos=("cod_pedido", "nunique"),
            compradores=("cod_rev", "nunique"),
        )
    )
    by_brand = by_brand.merge(
        channel[["nr_ciclo", "ativas", "gmv"]].rename(columns={"gmv": "gmv_canal"}),
        on="nr_ciclo", how="left", validate="many_to_one"
    )
    by_brand["penetracao"] = by_brand["compradores"].div(by_brand["ativas"].replace(0, pd.NA))
    by_brand["participacao_gmv_canal"] = by_brand["gmv"].div(by_brand["gmv_canal"].replace(0, pd.NA))

    mix = (
        pedidos.groupby(["nr_ciclo", "des_marca", "des_categoria"], as_index=False)
        .agg(
            gmv=("vlr_gmv", "sum"),
            volume=("vlr_volume", "sum"),
            pedidos=("cod_pedido", "nunique"),
            compradores=("cod_rev", "nunique"),
        )
    )
    mix["participacao_categoria_marca"] = mix["gmv"].div(
        mix.groupby(["nr_ciclo", "des_marca"])["gmv"].transform("sum").replace(0, pd.NA)
    )
    mix["participacao_categoria_canal"] = mix["gmv"].div(
        mix.groupby(["nr_ciclo"])["gmv"].transform("sum").replace(0, pd.NA)
    )
    return channel, by_brand, mix, orcamento, materiais, cadastro

def fmt_currency(v, decimals=1):
    if pd.isna(v):
        return "—"
    return f"R$ {v / 1_000_000:,.{decimals}f} mi".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_int(v):
    if pd.isna(v):
        return "—"
    return f"{int(round(v)):,}".replace(",", ".")

def fmt_pct(v):
    if pd.isna(v):
        return "—"
    return f"{v*100:.1f}%".replace(".", ",")

def style_fig(fig, height=330):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=10, t=35, b=8),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="DM Sans, sans-serif", color=INK, size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hoverlabel=dict(bgcolor=NAVY, font_color=WHITE),
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False)
    return fig

def money_axis(fig):
    fig.update_yaxes(tickprefix="R$ ", tickformat="~s")
    return fig

def attainment_table(actual_df, budget_df, kpi_names, brand="total"):
    target = budget_df[
        (budget_df["nr_ciclo"] == selected_cycle) &
        (budget_df["des_marca"].astype(str).str.lower() == brand.lower()) &
        (budget_df["des_kpi"].astype(str).str.lower().isin(kpi_names))
    ].copy()
    actual_map = actual_df.set_index("nr_ciclo").loc[selected_cycle]
    out = []
    col_map = {
        "base": "base", "base_ativa": "base_ativa", "ativas": "ativas",
        "inicio": "inicio", "reinicio": "reinicio", "perda": "perda"
    }
    for _, row in target.iterrows():
        kpi = str(row["des_kpi"]).lower()
        col = col_map.get(kpi)
        if not col:
            continue
        realized = float(actual_map[col])
        budget = float(row["vlr_kpi"])
        out.append({
            "KPI": {"base":"Base","base_ativa":"Base Ativa","ativas":"Ativas",
                    "inicio":"Inícios","reinicio":"Reinícios","perda":"Perdas"}.get(kpi,kpi),
            "Realizado": realized,
            "Orçado": budget,
            "Diferença": realized - budget,
            "Atingimento": realized / budget if budget else None,
        })
    return pd.DataFrame(out)

try:
    pedidos_raw, base_raw, materiais_raw, cadastro_raw, orcamento_raw = read_sources()
    channel, brand_cycle, mix_cycle, orcamento, materiais, cadastro = build_analytics()
except Exception as exc:
    st.error("Não consegui carregar as fontes sintéticas.")
    st.code(str(exc))
    st.markdown(
        "Confira se o repositório contém `data/raw_pedidos.csv`, `data/raw_base.csv`, "
        "`data/raw_materiais.csv`, `data/raw_cadastro.csv` e `data/raw_orcamento.csv`."
    )
    st.stop()

# Sidebar story navigation
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding:8px 8px 22px 8px;">
          <div style="font-size:.72rem;letter-spacing:.16em;font-weight:800;color:#F09AB9;">PORTFÓLIO • DATA</div>
          <div style="font-family:Manrope,sans-serif;font-size:1.55rem;font-weight:800;line-height:1.1;color:#FFFFFF;margin-top:9px;">VENDA<br> DIRETA</div>
          <div style="height:4px;width:50px;background:{PINK};margin-top:14px;border-radius:9px;"></div>
          <div style="color:#CCD6E2;font-size:.77rem;line-height:1.5;margin-top:13px;">Performance analytics<br>Dados sintéticos para demonstração</div>
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("### NAVEGAR")
    page = st.radio(
        "Perspectiva da análise",
        ["Visão geral", "Diagnóstico do ciclo", "Produtividade", "Mix de produtos"],
        label_visibility="collapsed",
    )
    cycle_options = sorted(channel["nr_ciclo"].astype(int).tolist())
    default_cycle = 202516 if 202516 in cycle_options else cycle_options[-1]
    selected_cycle = st.selectbox("Ciclo em foco", cycle_options, index=cycle_options.index(default_cycle),
                                  format_func=lambda c: f"{str(c)[:4]}-{str(c)[-2:]}")
    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:.72rem;color:#C7D2DF;line-height:1.6;">
        <b style="color:#FFFFFF;">COMO LER</b><br>
        01 · Resultado<br>
        02 · Componentes<br>
        03 · Produtividade<br>
        04 · Composição
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown("---")
    st.caption("Protótipo público • fontes 100% sintéticas")

c = channel[channel["nr_ciclo"] == selected_cycle].iloc[0]
bcycle = brand_cycle[brand_cycle["nr_ciclo"] == selected_cycle].copy()
mcycle = mix_cycle[mix_cycle["nr_ciclo"] == selected_cycle].copy()
cycle_label = f"{str(selected_cycle)[:4]}-{str(selected_cycle)[-2:]}"
brand_budgeted = ["BOTI", "EUD", "OUI", "QDB"]
budgeted_gmv_realized = bcycle[bcycle["des_marca"].isin(brand_budgeted)]["gmv"].sum()
budgeted_gmv_budget = orcamento[
    (orcamento["nr_ciclo"] == selected_cycle) &
    (orcamento["des_kpi"].str.lower() == "gmv") &
    (orcamento["des_marca"].isin(brand_budgeted))
]["vlr_kpi"].sum()
total_channel_gmv = float(c["gmv"])
active_count = float(c["ativas"])
rpa_value = float(c["rpa"]) if pd.notna(c["rpa"]) else 0
upa_value = float(c["upa"]) if pd.notna(c["upa"]) else 0

def page_header(kicker, title, subtitle):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="lede">{subtitle}</div>', unsafe_allow_html=True)

def insight(title, body):
    st.markdown(f'<div class="insight"><strong>{title}</strong><p>{body}</p></div>', unsafe_allow_html=True)

if page == "Visão geral":
    page_header("01 / RESULTADO", "A história começa pelo resultado", 
                f"Performance do canal ao longo dos ciclos, com aprofundamento em {cycle_label}.")
    st.markdown('<span class="tag">DADOS SINTÉTICOS • DEMONSTRAÇÃO</span>', unsafe_allow_html=True)
    st.write("")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("GMV do canal", fmt_currency(total_channel_gmv))
    k2.metric("GMV · marcas orçadas", fmt_currency(budgeted_gmv_realized),
              delta=fmt_pct(budgeted_gmv_realized / budgeted_gmv_budget - 1) if budgeted_gmv_budget else None)
    k3.metric("Ativas", fmt_int(active_count))
    k4.metric("RPA", f"R$ {rpa_value:,.0f}".replace(",", "."))
    k5.metric("UPA", f"{upa_value:.1f}".replace(".", ","))

    st.write("")
    left, right = st.columns([1.45, 1])
    with left:
        st.markdown("### Trajetória de GMV")
        trend = channel.sort_values("nr_ciclo")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=trend["nr_ciclo"].astype(str), y=trend["gmv"],
            mode="lines+markers", name="GMV do canal",
            line=dict(color=BLUE, width=3), marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(47,93,124,0.09)"
        ))
        fig.add_vline(x=str(selected_cycle), line_dash="dot", line_color=PINK, line_width=2)
        fig.update_layout(yaxis_tickprefix="R$ ", yaxis_tickformat="~s",
                          xaxis_title="Ciclo comercial", yaxis_title="Receita")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
    with right:
        st.markdown("### GMV por marca")
        brand_data = bcycle[bcycle["des_marca"].isin(brand_budgeted)].copy()
        bbud = orcamento[
            (orcamento["nr_ciclo"] == selected_cycle) &
            (orcamento["des_kpi"].str.lower() == "gmv") &
            (orcamento["des_marca"].isin(brand_budgeted))
        ][["des_marca", "vlr_kpi"]].rename(columns={"vlr_kpi":"orcado"})
        brand_data = brand_data.merge(bbud, on="des_marca", how="left")
        melt = brand_data.melt(id_vars="des_marca", value_vars=["gmv", "orcado"],
                               var_name="tipo", value_name="valor")
        melt["tipo"] = melt["tipo"].map({"gmv":"Realizado", "orcado":"Orçado"})
        fig = px.bar(melt, x="des_marca", y="valor", color="tipo", barmode="group",
                     color_discrete_map={"Realizado":PINK, "Orçado":BLUE},
                     labels={"des_marca":"Marca","valor":"GMV","tipo":""})
        fig.update_layout(yaxis_tickprefix="R$ ", yaxis_tickformat="~s")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)

    insight(
        "LEITURA EXECUTIVA",
        "O GMV total do canal e o GMV das marcas com orçamento são visões diferentes. "
        "Use o subtotal BOTI + EUD + OUI + QDB para comparar com o orçamento dessas marcas; "
        "não misture escopos. A trajetória mostra o resultado; as próximas páginas investigam os componentes."
    )
    st.markdown(
        '<div class="note">RPA = GMV do canal ÷ Ativas. UPA = Volume ÷ Ativas. '
        'RPA e UPA não têm orçamento direto neste conjunto sintético. </div>',
        unsafe_allow_html=True
    )

elif page == "Diagnóstico do ciclo":
    page_header("02 / COMPONENTES", "Mais população não explica tudo",
                f"Comparação entre realizado e orçado no ciclo {cycle_label}; valores artificiais para demonstrar a lógica analítica.")
    kpis = ["base", "base_ativa", "ativas", "inicio", "reinicio", "perda"]
    names = {"base":"Base","base_ativa":"Base Ativa","ativas":"Ativas",
             "inicio":"Inícios","reinicio":"Reinícios","perda":"Perdas"}
    budget = orcamento[
        (orcamento["nr_ciclo"] == selected_cycle) &
        (orcamento["des_marca"].str.lower() == "total") &
        (orcamento["des_kpi"].str.lower().isin(kpis))
    ].copy()
    actual = {k:float(c[k]) for k in kpis}
    comp = []
    for _, row in budget.iterrows():
        name = str(row["des_kpi"]).lower()
        comp.append({"Indicador":names.get(name,name.title()),
                     "Realizado":actual.get(name,0),
                     "Orçado":float(row["vlr_kpi"]),
                     "Atingimento":actual.get(name,0)/float(row["vlr_kpi"]) if row["vlr_kpi"] else None})
    comp_df = pd.DataFrame(comp)
    movement_names = ["Inícios","Reinícios","Perdas"]
    p1, p2 = st.columns([1.1, 1])
    with p1:
        st.markdown("### População do canal")
        subset = comp_df[comp_df["Indicador"].isin(["Base","Base Ativa","Ativas"])]
        melted = subset.melt(id_vars="Indicador", value_vars=["Realizado","Orçado"],
                             var_name="Série", value_name="Revendedoras")
        fig = px.bar(melted, x="Indicador", y="Revendedoras", color="Série", barmode="group",
                     color_discrete_map={"Realizado":BLUE,"Orçado":PINK},
                     labels={"Indicador":"","Revendedoras":"Quantidade","Série":""})
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)
    with p2:
        st.markdown("### Movimento da base")
        subset = comp_df[comp_df["Indicador"].isin(movement_names)]
        melted = subset.melt(id_vars="Indicador", value_vars=["Realizado","Orçado"],
                             var_name="Série", value_name="Revendedoras")
        fig = px.bar(melted, x="Indicador", y="Revendedoras", color="Série", barmode="group",
                     color_discrete_map={"Realizado":BLUE,"Orçado":PINK},
                     labels={"Indicador":"","Revendedoras":"Quantidade","Série":""})
        st.plotly_chart(style_fig(fig, 330), use_container_width=True)

    st.markdown("### Alcance das marcas")
    buyers = orcamento[
        (orcamento["nr_ciclo"] == selected_cycle) &
        (orcamento["des_kpi"].str.lower() == "compradores") &
        (orcamento["des_marca"].isin(brand_budgeted))
    ][["des_marca","vlr_kpi"]].rename(columns={"vlr_kpi":"Orçado"})
    buyers = buyers.merge(
        bcycle[["des_marca","compradores"]].rename(columns={"compradores":"Realizado"}),
        on="des_marca", how="left"
    )
    buyers["Atingimento"] = buyers["Realizado"] / buyers["Orçado"].replace(0,pd.NA)
    melted = buyers.melt(id_vars="des_marca", value_vars=["Realizado","Orçado"],
                         var_name="Série", value_name="Compradores")
    fig = px.bar(melted, x="des_marca", y="Compradores", color="Série", barmode="group",
                 color_discrete_map={"Realizado":PINK,"Orçado":BLUE},
                 labels={"des_marca":"Marca","Compradores":"Compradoras da marca","Série":""})
    st.plotly_chart(style_fig(fig, 300), use_container_width=True)

    view = comp_df.copy()
    view["Realizado"] = view["Realizado"].round(0).astype(int)
    view["Orçado"] = view["Orçado"].round(0).astype(int)
    view["Atingimento"] = view["Atingimento"].map(fmt_pct)
    st.markdown("### Conferência numérica")
    st.dataframe(view, hide_index=True, use_container_width=True)
    insight(
        "O QUE O DIAGNÓSTICO PERMITE DIZER",
        "A população, a movimentação da base e o alcance das marcas precisam ser lidos em conjunto. "
        "Atingimento acima de 100% não é automaticamente positivo: depende do indicador, especialmente no caso de Perdas. "
        "Os dados mostram onde investigar, mas não provam causalidade."
    )

elif page == "Produtividade":
    page_header("03 / PRODUTIVIDADE", "Quanto a população ativa movimenta?",
                f"RPA e UPA ajudam a contextualizar o resultado por ativa ao longo dos ciclos. Ciclo em foco: {cycle_label}.")
    k1, k2, k3 = st.columns(3)
    k1.metric("GMV do canal", fmt_currency(total_channel_gmv))
    k2.metric("RPA · receita por ativa", f"R$ {rpa_value:,.0f}".replace(",", "."))
    k3.metric("UPA · unidades por ativa", f"{upa_value:.1f}".replace(".", ","))

    st.write("")
    left, right = st.columns(2)
    trend = channel.sort_values("nr_ciclo").copy()
    trend["ciclo_label"] = trend["nr_ciclo"].astype(str).str[:4] + "-" + trend["nr_ciclo"].astype(str).str[-2:]
    with left:
        st.markdown("### Evolução de RPA")
        fig = px.line(trend, x="ciclo_label", y="rpa", markers=True,
                      labels={"ciclo_label":"Ciclo","rpa":"R$ por ativa"})
        fig.update_traces(line_color=BLUE, line_width=3, marker_color=PINK)
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
    with right:
        st.markdown("### Evolução de UPA")
        fig = px.line(trend, x="ciclo_label", y="upa", markers=True,
                      labels={"ciclo_label":"Ciclo","upa":"Unidades por ativa"})
        fig.update_traces(line_color=PINK, line_width=3, marker_color=BLUE)
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)

    insight(
        "COMO INTERPRETAR",
        "RPA = GMV ÷ Ativas e UPA = Volume ÷ Ativas. RPA mede receita média por ativa; UPA mede unidades médias por ativa. "
        "Os dois indicadores são complementares, e nenhum isoladamente prova por que o GMV subiu ou caiu."
    )
    st.markdown(
        '<div class="note">Não há orçamento direto de RPA/UPA neste protótipo. '
        'Não calculamos atingimento orçamentário para eles sem validar o escopo dos componentes usados.</div>',
        unsafe_allow_html=True
    )

elif page == "Mix de produtos":
    page_header("04 / COMPOSIÇÃO", "O resultado também tem uma composição",
                f"Exploração demonstrativa do mix por marca e categoria no ciclo {cycle_label}. Esta perspectiva amplia o portfólio usando dados sintéticos.")
    brands_available = sorted(mcycle["des_marca"].dropna().unique().tolist())
    selected_brand = st.selectbox("Marca para explorar", brands_available,
                                  index=brands_available.index("BOTI") if "BOTI" in brands_available else 0)
    brand_mix = mcycle[mcycle["des_marca"] == selected_brand].copy().sort_values("gmv", ascending=False)
    total_brand_gmv = brand_mix["gmv"].sum()
    k1, k2, k3 = st.columns(3)
    k1.metric("GMV da marca", fmt_currency(total_brand_gmv))
    k2.metric("Categorias no ciclo", str(brand_mix["des_categoria"].nunique()))
    k3.metric("Categoria líder", brand_mix.iloc[0]["des_categoria"] if len(brand_mix) else "—")

    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("### Contribuição por categoria")
        fig = px.bar(brand_mix.sort_values("gmv"), x="gmv", y="des_categoria", orientation="h",
                     color="des_categoria", color_discrete_sequence=[BLUE, PINK, GREEN, AMBER],
                     labels={"gmv":"GMV","des_categoria":"Categoria"})
        fig.update_layout(showlegend=False, xaxis_tickprefix="R$ ", xaxis_tickformat="~s")
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)
    with right:
        st.markdown("### Participação na marca")
        fig = px.pie(brand_mix, names="des_categoria", values="gmv", hole=.68,
                     color_discrete_sequence=[NAVY, PINK, BLUE, GREEN])
        fig.update_traces(textposition="inside", textinfo="percent+label",
                          marker=dict(line=dict(color=WHITE, width=3)))
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig, 340), use_container_width=True)

    table = brand_mix[["des_categoria","gmv","volume","pedidos","compradores","participacao_categoria_marca"]].copy()
    table = table.rename(columns={"des_categoria":"Categoria","gmv":"GMV","volume":"Volume",
        "pedidos":"Pedidos","compradores":"Compradores","participacao_categoria_marca":"Participação na marca"})
    table["Participação na marca"] = table["Participação na marca"].map(fmt_pct)
    st.dataframe(table, hide_index=True, use_container_width=True)
    insight(
        "PRÓXIMA PERGUNTA ANALÍTICA",
        "A distribuição por categoria aponta onde o GMV está concentrado dentro da marca. Para transformar isso em recomendação, "
        "seria preciso comparar a composição entre ciclos, avaliar volume e compradores e validar se as diferenças são consistentes."
    )

st.markdown("---")
st.markdown(
    f"""
    <div class="note">
    <b style="color:{NAVY};">METODOLOGIA E LIMITAÇÕES</b><br>
    Este dashboard usa exclusivamente dados sintéticos para portfólio. Os resultados não representam o Grupo Boticário nem o resultado do case original.
    Os gráficos permitem explorar relações; não estabelecem causalidade. O SQL está documentado separadamente na pasta <code>sql/</code>.
    </div>
    """,
    unsafe_allow_html=True,
)
