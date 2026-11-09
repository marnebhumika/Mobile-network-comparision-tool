import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------
# 1. PAGE SETUP
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Mobile Network Comparison Tool",
    page_icon="📡",
    layout="wide"
)

# Small CSS touch-ups: hide Streamlit's menu and footer, and use
# less empty space on the sides so phones show more content.
st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        @media (max-width: 640px) {
            .block-container {padding-left: 1rem; padding-right: 1rem;}
            h1 {font-size: 1.6rem !important;}
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------------
# 2. DATA AND SETTINGS (written once, used everywhere)
# ------------------------------------------------------------------
network_data = {
    "GSM": {"rate": 0.014, "latency": 500},
    "GPRS": {"rate": 0.114, "latency": 300},
    "WCDMA": {"rate": 2, "latency": 100},
    "LTE": {"rate": 100, "latency": 40},
    "WiMAX": {"rate": 70, "latency": 50}
}

# One fixed colour per network, so LTE is the same colour in every graph.
NETWORK_COLORS = {
    "GSM": "#6366F1",
    "GPRS": "#14B8A6",
    "WCDMA": "#F59E0B",
    "LTE": "#EF4444",
    "WiMAX": "#3B82F6"
}

# Locks every graph: no toolbar, no zoom, no drag, no disappearing.
CHART_CONFIG = {
    "displayModeBar": False,
    "staticPlot": True
}

# Reference values for the score: the best rate and best latency
# among ALL five networks (so the score is a fair comparison).
BEST_RATE = max(v["rate"] for v in network_data.values())
BEST_LATENCY = min(v["latency"] for v in network_data.values())


# ------------------------------------------------------------------
# 3. HELPER FUNCTIONS (write once, reuse many times)
# ------------------------------------------------------------------
def make_bar_chart(df, y_column, title):
    """Builds one clean, locked, professional bar chart."""
    fig = px.bar(
        df,
        x="Network",
        y=y_column,
        color="Network",
        color_discrete_map=NETWORK_COLORS,
        text=y_column
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0
    )
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16)),
        showlegend=False,
        height=340,
        margin=dict(l=10, r=10, t=60, b=10),
        dragmode=False,
        bargap=0.35,
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(
        fixedrange=True,
        range=[0, max(df[y_column].max() * 1.25, 1)],
        showgrid=True,
        gridcolor="rgba(128,128,128,0.2)"
    )
    return fig


def show_chart(fig, key):
    """Shows a chart with the locked settings."""
    st.plotly_chart(fig, config=CHART_CONFIG, key=key)


def signal_card(value):
    """Shows ONE good-looking signal strength card."""
    if value >= 80:
        color, label, message = "#16A34A", "Strong Signal 🟢", "Excellent signal strength."
    elif value >= 50:
        color, label, message = "#D97706", "Moderate Signal 🟡", "Signal strength is acceptable."
    else:
        color, label, message = "#DC2626", "Weak Signal 🔴", "Signal strength is low."

    st.markdown(
        f"""
        <div style="border-left: 6px solid {color};
                    background: {color}22;
                    padding: 14px 18px;
                    border-radius: 10px;
                    margin-top: 6px;">
            <div style="font-size: 14px; opacity: 0.8;">Current Signal Strength</div>
            <div style="font-size: 42px; font-weight: 700;
                        color: {color}; line-height: 1.1;">{value}%</div>
            <div style="font-weight: 600; margin-top: 4px;">{label}</div>
            <div style="opacity: 0.8;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ------------------------------------------------------------------
# 4. TITLE
# ------------------------------------------------------------------
st.title("📡 Mobile Communication Network Comparison Tool")

st.write("This tool compares GSM, GPRS, WCDMA, LTE, and WiMAX networks.")

st.info(
    "Educational simulation: results are based on simplified models, "
    "not live mobile network measurements."
)

# ------------------------------------------------------------------
# 5. SELECT NETWORKS
# ------------------------------------------------------------------
st.subheader("Select Networks")

networks = st.multiselect(
    "Choose the networks you want to compare:",
    list(network_data.keys()),
    default=["GSM", "LTE", "WiMAX"]
)

# If nothing is selected, show a message and stop here,
# because every section below needs at least one network.
if not networks:
    st.warning("Please select at least one network.")
    st.stop()

# ------------------------------------------------------------------
# 6. NETWORK COMPARISON (typical values)
# ------------------------------------------------------------------
data = pd.DataFrame({
    "Network": list(network_data.keys()),
    "Typical Data Rate (Mbps)": [v["rate"] for v in network_data.values()],
    "Illustrative Latency (ms)": [v["latency"] for v in network_data.values()]
})

comparison = data[data["Network"].isin(networks)]

st.subheader("Network Comparison")
st.dataframe(comparison, hide_index=True)

st.subheader("Data Rate Comparison")
show_chart(
    make_bar_chart(
        comparison,
        "Typical Data Rate (Mbps)",
        "Illustrative Data Rate by Network (Mbps)"
    ),
    key="chart_rate"
)

st.subheader("Latency Comparison")
show_chart(
    make_bar_chart(
        comparison,
        "Illustrative Latency (ms)",
        "Illustrative Latency by Network (ms)"
    ),
    key="chart_latency"
)

# ------------------------------------------------------------------
# 7. SIGNAL STRENGTH SIMULATOR
# ------------------------------------------------------------------
st.subheader("📶 Signal Strength Simulator")

signal_strength = st.slider(
    "Adjust Signal Strength (%)",
    min_value=10,
    max_value=100,
    value=80,
    step=5
)

signal_card(signal_strength)

st.caption(
    "Educational simulation only. This is not a real mobile signal measurement."
)

# ------------------------------------------------------------------
# 8. SIMULATED NETWORK PERFORMANCE
# ------------------------------------------------------------------
st.subheader("📊 Simulated Network Performance")

signal_factor = signal_strength / 100

results = []

for network in networks:
    base_rate = network_data[network]["rate"]
    base_latency = network_data[network]["latency"]

    simulated_rate = base_rate * signal_factor
    simulated_latency = base_latency / signal_factor
    packet_loss = (100 - signal_strength) * 0.1

    results.append({
        "Network": network,
        "Data Rate (Mbps)": round(simulated_rate, 3),
        "Latency (ms)": round(simulated_latency, 1),
        "Packet Loss (%)": round(packet_loss, 1)
    })

performance = pd.DataFrame(results)

st.dataframe(performance, hide_index=True)

st.subheader("⚡ Data Rate")
show_chart(
    make_bar_chart(performance, "Data Rate (Mbps)", "Simulated Data Rate (Mbps)"),
    key="chart_sim_rate"
)

st.subheader("⏱️ Latency")
show_chart(
    make_bar_chart(performance, "Latency (ms)", "Simulated Latency (ms)"),
    key="chart_sim_latency"
)

st.subheader("📉 Packet Loss")
show_chart(
    make_bar_chart(performance, "Packet Loss (%)", "Simulated Packet Loss (%)"),
    key="chart_sim_loss"
)

# ------------------------------------------------------------------
# 9. BEST NETWORK RECOMMENDATION
# ------------------------------------------------------------------
st.subheader("🏆 Best Network Recommendation")

best_network = max(results, key=lambda item: item["Data Rate (Mbps)"])

st.success(f"Recommended Network: {best_network['Network']}")

col1, col2 = st.columns(2)
col1.metric("Simulated Data Rate", f"{best_network['Data Rate (Mbps)']} Mbps")
col2.metric("Simulated Latency", f"{best_network['Latency (ms)']} ms")

st.info(
    "Recommendation is based on simulated data rate only. "
    "Real network performance may differ."
)

# ------------------------------------------------------------------
# 10. NETWORK PERFORMANCE SCORE
# ------------------------------------------------------------------
st.subheader("⭐ Network Performance Score")

scores = []

for item in results:
    rate_score = (item["Data Rate (Mbps)"] / BEST_RATE) * 50
    latency_score = (BEST_LATENCY / item["Latency (ms)"]) * 50

    scores.append({
        "Network": item["Network"],
        "Performance Score": round(rate_score + latency_score)
    })

score_df = pd.DataFrame(scores)

st.dataframe(score_df, hide_index=True)

show_chart(
    make_bar_chart(score_df, "Performance Score", "Performance Score (out of 100)"),
    key="chart_score"
)

st.caption(
    "Score is an illustrative educational score based on simulated "
    "data rate and latency, not a real-world benchmark."
)