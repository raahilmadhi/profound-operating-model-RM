import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Profound Operating Model", page_icon="📈", layout="wide")

DATA_PATH = Path(__file__).parent / "data.json"
payload = json.loads(DATA_PATH.read_text())
quarters = payload["quarters"]
scenarios = payload["scenarios"]


def fmt_pct(value, decimals=0):
    """Format percentages with parentheses for negatives."""
    pct = abs(value) * 100
    formatted = f"{pct:.{decimals}f}%"
    return f"({formatted})" if value < 0 else formatted

st.title("Profound Operating Model")
st.caption("Quarterly operating model | Q1'26–Q4'28 | Financial figures in $mm unless otherwise noted")

scenario = st.segmented_control(
    "Scenario",
    options=["Bear", "Base", "Bull"],
    default="Base",
    selection_mode="single",
)
if scenario is None:
    scenario = "Base"

d = scenarios[scenario]
y28 = d["annual"]["2028"]
cash_trough = min(d["cash"])
financing = "No" if cash_trough >= 25 else "Yes"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("2028 ARR", f"${y28['arr']:.0f}mm")
c2.metric("2028 ARR Growth", f"{y28['growth']:.0%}")
c3.metric("2028 EBITDA Margin", fmt_pct(y28["ebitda_margin"]))
c4.metric("Cash Trough", f"${cash_trough:.0f}mm")
c5.metric("Financing Required", financing)

st.subheader("Key Takeaways")
for insight in d["insights"]:
    st.markdown(f"- {insight.rstrip('.').replace('$M', '$mm').replace('~$75M', '~$75mm').replace('~$50M', '~$50mm').replace('$25M', '$25mm').replace('~$178M', '~$178mm').replace('~$100M', '~$100mm')}")

left, right = st.columns(2)

with left:
    st.subheader("ARR Growth ($mm)")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quarters,
        y=d["arr"],
        name="Ending ARR",
        text=[f"${v:.0f}mm" for v in d["arr"]],
        textposition="outside",
        hovertemplate="%{x}<br>Ending ARR: $%{y:.1f}mm<extra></extra>",
    ))
    fig.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis_title="$mm",
        showlegend=False,
    )
    fig.update_yaxes(tickprefix="$", ticksuffix="mm")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Profitability & Free Cash Flow")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=quarters,
        y=[x * 100 for x in d["ebitda_margin"]],
        mode="lines+markers+text",
        name="EBITDA Margin",
        text=[fmt_pct(x) for x in d["ebitda_margin"]],
        textposition="top center",
        customdata=[fmt_pct(x, 1) for x in d["ebitda_margin"]],
        hovertemplate="%{x}<br>EBITDA Margin: %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=quarters,
        y=d["fcf"],
        name="FCF",
        yaxis="y2",
        opacity=0.45,
        text=[f"${v:.1f}mm" for v in d["fcf"]],
        textposition="outside",
        hovertemplate="%{x}<br>FCF: $%{y:.1f}mm<extra></extra>",
    ))
    fig.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis=dict(title="EBITDA Margin (%)", ticksuffix="%"),
        yaxis2=dict(title="FCF ($mm)", overlaying="y", side="right", tickprefix="$", ticksuffix="mm"),
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Liquidity ($mm)")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=quarters,
    y=d["cash"],
    mode="lines+markers+text",
    name="Ending Cash",
    text=[f"${v:.0f}mm" for v in d["cash"]],
    textposition="top center",
    hovertemplate="%{x}<br>Ending Cash: $%{y:.1f}mm<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=quarters,
    y=[25] * len(quarters),
    mode="lines",
    name="$25mm Minimum Cash",
    line=dict(dash="dash"),
    hovertemplate="%{x}<br>Minimum Cash: $25.0mm<extra></extra>",
))
fig.update_layout(
    height=370,
    margin=dict(l=10, r=10, t=25, b=10),
    yaxis_title="$mm",
    legend=dict(orientation="h", y=1.15),
)
fig.update_yaxes(tickprefix="$", ticksuffix="mm")
st.plotly_chart(fig, use_container_width=True)
st.info(d["liquidity"].replace("$25M", "$25mm"))

left, right = st.columns(2)

with left:
    st.subheader("Operating Efficiency")
    eff = pd.DataFrame({
        "Quarter": quarters,
        "Headcount": d["headcount"],
        "ARR / Employee ($000)": [f"${v:,.0f}k" for v in d["arr_per_employee"]],
    })
    st.dataframe(eff, use_container_width=True, hide_index=True)

with right:
    st.subheader("Key Assumptions")
    assump = pd.DataFrame({
        "Metric": [
            "GRR", "NRR",
            "New ARR 2026", "New ARR 2027", "New ARR 2028",
            "Gross Margin 2026", "Gross Margin 2027", "Gross Margin 2028",
            "Net HC Adds 2026", "Net HC Adds 2027", "Net HC Adds 2028"
        ],
        "Value": [
            fmt_pct(d["grr"]), fmt_pct(d["nrr"]),
            f"${d['new_arr'][0]}mm", f"${d['new_arr'][1]}mm", f"${d['new_arr'][2]}mm",
            fmt_pct(d["gm"][0]), fmt_pct(d["gm"][1]), fmt_pct(d["gm"][2]),
            str(d['hc_adds'][0]), str(d['hc_adds'][1]), str(d['hc_adds'][2]),
        ],
    })
    st.dataframe(assump, use_container_width=True, hide_index=True)

st.caption(
    "Source: Profound operating model. Model assumptions are illustrative based upon "
    "industry reports as available and SaaS benchmarks."
)
