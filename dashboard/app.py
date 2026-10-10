
    
  
    )

    st.write("")

    st.markdown("### A ponte entre as duas visões")

    fig = go.Figure(
        go.Waterfall(
            name="Conciliação",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=[
                "Marcas com orçamento",
                "Marcas sem orçamento direto",
                "GMV total do canal",
            ],
            y=[
                brands_realized,
                unbudgeted_gmv,
                0,
            ],
            text=[
                fmt_currency(brands_realized),
                fmt_currency(unbudgeted_gmv),
                fmt_currency(channel_gmv),
            ],
            textposition="outside",
            connector={"line": {"color": GRID}},
            increasing={"marker": {"color": BLUE}},
            totals={"marker": {"color": PINK}},
        )
    )

    fig.update_layout(
        showlegend=False,
        yaxis_tickprefix="R$ ",
        yaxis_tickformat="~s",
        xaxis_title="Composição do GMV",
        yaxis_title="Receita",
    )

    st.plotly_chart(
        style_fig(fig, 360),
        use_container_width=True,
        theme=None,
    )

    st.markdown("### Realizado por marca e disponibilidade de orçamento")

    budget_by_brand = orcamento[
        (orcamento["nr_ciclo"] == selected_cycle)
        & (orcamento["des_kpi"].str.lower() == "gmv")
        & (orcamento["des_marca"].isin(brand_budgeted))
    ][["des_marca", "vlr_kpi"]].rename(
        columns={"vlr_kpi": "orcado"}
    )

    brand_table = all_brand[
        ["des_marca", "gmv"]
    ].merge(
        budget_by_brand,
        on="des_marca",
        how="left",
    )

    brand_table["GMV realizado"] = brand_table["gmv"].map(fmt_currency)

    brand_table["GMV orçado"] = brand_table["orcado"].apply(
        lambda value: fmt_currency(value)
        if pd.notna(value) else "Sem orçamento"
    )

    brand_table["Atingimento"] = brand_table.apply(
        lambda row: fmt_pct(row["gmv"] / row["orcado"])
        if pd.notna(row["orcado"]) and row["orcado"] != 0
        else "Sem orçamento",
        axis=1,
    )

    brand_table = brand_table.rename(
        columns={"des_marca": "Marca"}
    )

    st.dataframe(
        brand_table[
            ["Marca", "GMV realizado", "GMV orçado", "Atingimento"]
        ],
        hide_index=True,
        use_container_width=True,
    )

    names_without_budget = ", ".join(
        sorted(unbudgeted_brands["des_marca"].astype(str).unique())
    ) or "Nenhuma"

    reconciled = abs(
        brands_realized + unbudgeted_gmv - channel_gmv
    ) < 0.01

    reconciliation_text = (
        "A soma dos escopos fecha com o GMV total."
        if reconciled
        else "Existe uma diferença residual a investigar na conciliação."
    )

    insight(
        "ACHADO DE ESCOPO",
        (
            f"No conjunto sintético, o GMV do canal é composto pelo "
            f"realizado das marcas com orçamento e por {names_without_budget}, "
            f"que não possui orçamento direto. "
            f"{reconciliation_text} "
            "Essa diferença não prova, por si só, um erro nos dados. "
            "Ela demonstra por que realizado e orçamento precisam ser "
            "comparados dentro do mesmo escopo."
        ),
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

