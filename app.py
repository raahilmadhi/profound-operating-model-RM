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

st.title("Profound Operating Model")
st.caption("Quarterly operating model | Q1'26–Q4'28")

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
c1.metric("2028 ARR", f"${y28['arr']:.0f}M")
c2.metric("2028 ARR Growth", f"{y28['growth']:.0%}")
c3.metric("2028 EBITDA Margin", f"{y28['ebitda_margin']:.0%}")
c4.metric("Cash Trough", f"${cash_trough:.0f}M")
c5.metric("Financing Required", financing)

st.subheader("Key takeaways")
for insight in d["insights"]:
    st.markdown(f"- {insight}")

left, right = st.columns(2)

with left:
    st.subheader("ARR Growth")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=quarters, y=d["arr"], name="Ending ARR ($M)"))
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis_title="$M",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Profitability & Free Cash Flow")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quarters, y=[x * 100 for x in d["ebitda_margin"]],
                             mode="lines+markers", name="EBITDA Margin (%)"))
    fig.add_trace(go.Bar(x=quarters, y=d["fcf"], name="FCF ($M)", yaxis="y2", opacity=0.45))
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(title="EBITDA Margin (%)"),
        yaxis2=dict(title="FCF ($M)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Liquidity")
fig = go.Figure()
fig.add_trace(go.Scatter(x=quarters, y=d["cash"], mode="lines+markers", name="Ending Cash"))
fig.add_trace(go.Scatter(x=quarters, y=[25] * len(quarters), mode="lines",
                         name="$25M Minimum Cash", line=dict(dash="dash")))
fig.update_layout(
    height=340,
    margin=dict(l=10, r=10, t=20, b=10),
    yaxis_title="$M",
    legend=dict(orientation="h", y=1.12),
)
st.plotly_chart(fig, use_container_width=True)
st.info(d["liquidity"])

left, right = st.columns(2)

with left:
    st.subheader("Operating Efficiency")
    eff = pd.DataFrame({
        "Quarter": quarters,
        "Headcount": d["headcount"],
        "ARR / Employee ($K)": d["arr_per_employee"],
    })
    st.dataframe(eff, use_container_width=True, hide_index=True)

with right:
    st.subheader("Key Assumptions")
    assump = pd.DataFrame({
        "Metric": ["GRR", "NRR", "New ARR 2026", "New ARR 2027", "New ARR 2028",
                   "Gross Margin 2026", "Gross Margin 2027", "Gross Margin 2028",
                   "Net HC Adds 2026", "Net HC Adds 2027", "Net HC Adds 2028"],
        "Value": [
            f"{d['grr']:.0%}", f"{d['nrr']:.0%}",
            f"${d['new_arr'][0]}M", f"${d['new_arr'][1]}M", f"${d['new_arr'][2]}M",
            f"{d['gm'][0]:.0%}", f"{d['gm'][1]:.0%}", f"{d['gm'][2]:.0%}",
            str(d['hc_adds'][0]), str(d['hc_adds'][1]), str(d['hc_adds'][2]),
        ],
    })
    st.dataframe(assump, use_container_width=True, hide_index=True)

st.caption("Source: Profound operating model. Model assumptions are illustrative and based on case-provided metrics, public company context, and SaaS benchmarks.")
