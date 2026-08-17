import json
import math
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


def fmt_mm(value, decimals=0):
    """Format $mm values with parentheses for negatives."""
    amount = abs(value)
    formatted = f"${amount:.{decimals}f}mm"
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
    st.subheader("EBITDA & EBITDA Margin")

    ebitda_vals = [rev * margin for rev, margin in zip(d["revenue"], d["ebitda_margin"])]
    ebitda_pct = [x * 100 for x in d["ebitda_margin"]]

    ebitda_floor = math.floor(min(ebitda_vals) / 5) * 5
    ebitda_ceil = math.ceil(max(ebitda_vals) / 5) * 5
    ebitda_ticks = list(range(int(ebitda_floor), int(ebitda_ceil) + 1, 5))
    ebitda_ticktext = [f"(${abs(v):.0f}mm)" if v < 0 else f"${v:.0f}mm" for v in ebitda_ticks]

    pct_floor = math.floor(min(ebitda_pct) / 10) * 10
    pct_ceil = math.ceil(max(ebitda_pct) / 10) * 10
    pct_ticks = list(range(int(pct_floor), int(pct_ceil) + 1, 10))
    pct_ticktext = [f"({abs(v):.0f}%)" if v < 0 else f"{v:.0f}%" for v in pct_ticks]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quarters,
        y=ebitda_vals,
        name="EBITDA",
        text=[fmt_mm(v) for v in ebitda_vals],
        textposition="outside",
        customdata=[fmt_mm(v) for v in ebitda_vals],
        hovertemplate="%{x}<br>EBITDA: %{customdata}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=quarters,
        y=ebitda_pct,
        mode="lines+markers+text",
        name="EBITDA Margin",
        yaxis="y2",
        text=[fmt_pct(x) for x in d["ebitda_margin"]],
        textposition="top center",
        customdata=[fmt_pct(x) for x in d["ebitda_margin"]],
        hovertemplate="%{x}<br>EBITDA Margin: %{customdata}<extra></extra>",
    ))
    fig.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis=dict(
            title="EBITDA ($mm)",
            tickmode="array",
            tickvals=ebitda_ticks,
            ticktext=ebitda_ticktext,
            zeroline=True,
        ),
        yaxis2=dict(
            title="EBITDA Margin (%)",
            overlaying="y",
            side="right",
            tickmode="array",
            tickvals=pct_ticks,
            ticktext=pct_ticktext,
            zeroline=True,
        ),
        legend=dict(orientation="h", y=1.15),
    )
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)

with left:
    st.subheader("Free Cash Flow ($mm)")
    fcf_vals = d["fcf"]
    fcf_floor = math.floor(min(fcf_vals) / 5) * 5
    fcf_ceil = math.ceil(max(fcf_vals) / 5) * 5
    fcf_ticks = list(range(int(fcf_floor), int(fcf_ceil) + 1, 5))
    fcf_ticktext = [f"(${abs(v):.0f}mm)" if v < 0 else f"${v:.0f}mm" for v in fcf_ticks]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=quarters,
        y=fcf_vals,
        name="FCF",
        text=[fmt_mm(v) for v in fcf_vals],
        textposition="outside",
        customdata=[fmt_mm(v) for v in fcf_vals],
        hovertemplate="%{x}<br>FCF: %{customdata}<extra></extra>",
    ))
    fig.update_layout(
        height=370,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis=dict(
            title="FCF ($mm)",
            tickmode="array",
            tickvals=fcf_ticks,
            ticktext=fcf_ticktext,
            zeroline=True,
        ),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
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
        hovertemplate="%{x}<br>Minimum Cash: $25mm<extra></extra>",
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
