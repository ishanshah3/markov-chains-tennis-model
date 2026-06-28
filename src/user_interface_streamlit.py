import streamlit as st
from markov_modeling import compute_player_probabilities

st.set_page_config(
    page_title="Tennis Match Probability Explorer",
    page_icon="🎾",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero {
        background: linear-gradient(135deg, #0b3d91 0%, #2d7ecb 45%, #4fb3ff 100%);
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 24px rgba(11, 61, 145, 0.22);
        border: 1px solid rgba(255,255,255,0.16);
        position: relative;
        overflow: hidden;
    }
    .panel {
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        border: 1px solid #d8e8f6;
        border-radius: 16px;
        padding: 0.95rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 12px 24px rgba(15, 39, 66, 0.08);
        color: #0f172a;
    }
    .summary-panel {
        min-height: 54px;
        margin-bottom: 0.35rem;
        padding: 0.55rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: #ffffff;
        position: relative;
        overflow: hidden;
        border-radius: 16px;
    }
    .summary-panel div {
        min-width: 0;
    }
    .summary-panel strong { font-weight: 600; }
    .metric-card {
        min-height: 220px;
        height: 220px;
        margin-top: -0.3rem;
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #eef6ff;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 1.3rem 1.3rem;
        box-shadow: 0 16px 32px rgba(8, 22, 47, 0.22);
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
    }
    .metric-card::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 8px;
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        opacity: 0.2;
    }
    .metric-card h4 {
        margin-bottom: 0.9rem;
        color: #ffffff;
        font-size: 1.26rem;
        line-height: 1.35;
    }
    .metric-card .metric-label {
        display: inline-block;
        white-space: nowrap;
    }
    .metric-body {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 0.9rem;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-height: 1.8rem;
    }
    .metric-row strong {
        color: #0f172a;
        font-weight: 600;
        font-size: 1.04rem;
        line-height: 1.45;
    }
    .metric-value {
        color: #155fbf;
        font-weight: 700;
        font-size: 1.04rem;
        line-height: 1.45;
    }
    .metric-row span {
        white-space: nowrap;
    }
    .player-card {
        min-height: 230px;
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        border-left: 5px solid #2c7bdd;
        color: #eef6ff;
        position: relative;
        overflow: hidden;
        padding: 1.25rem 1.25rem;
        box-shadow: 0 16px 32px rgba(8, 22, 47, 0.22);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        gap: 1rem;
    }
    .player-card .player-content {
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
    }
    .player-bar {
        height: 14px;
        width: 100%;
        background: rgba(255,255,255,0.06);
        border-radius: 999px;
        margin-top: 1rem;
        overflow: hidden;
        box-shadow: inset 0 1px 2px rgba(255,255,255,0.08);
    }
    .player-fill {
        height: 100%;
        width: 0;
        border-radius: 999px;
        background: linear-gradient(135deg, #0b2a4a 0%, #173e6d 50%, #22679f 100%);
        box-shadow: inset 0 0 10px rgba(74,158,255,0.3);
        transition: width 0.6s ease;
    }
    .player-card h4 { margin-bottom: 0.8rem; color: #ffffff; font-size: 1.22rem; line-height: 1.35; }
    .player-card p { margin: 0; color: rgba(238,246,255,0.92); font-size: 1.04rem; line-height: 1.55; }
    .player-card strong { color: #ffffff; font-weight: 600; }
    .panel h4 { margin-bottom: 0.35rem; color: #0f172a; }
    .subtle { color: #607080; font-size: 0.95rem; }
    @media (prefers-color-scheme: dark) {
        .panel {
            background: #162535;
            border-color: #3b5371;
            color: #f8fbff;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
        }
        .panel h4, .panel p, .panel strong, .subtle {
            color: #f8fbff !important;
        }
        .subtle { color: #d6e4f2; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h2 style="margin-bottom: 0.25rem;">🎾 Tennis Match Probability Explorer</h2>
        <p style="margin-bottom: 0; font-size: 1rem;">Estimate how each player might perform in a match using serve and return statistics.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Player Inputs")
    player1_name = st.text_input("Player 1 name", value="Carlos Alcaraz")
    player2_name = st.text_input("Player 2 name", value="Jannik Sinner")
    surface = st.selectbox("Surface", ["Hard", "Clay", "Grass"], index=0)
    st.markdown(
        "<div class='subtle'>Choose two players and a surface to compare their projected chances across points, games, and sets.</div>",
        unsafe_allow_html=True,
    )

if st.button("Compute probabilities"):
    if not player1_name.strip() or not player2_name.strip():
        st.warning("Please enter names for both players.")
    elif player1_name.strip().lower() == player2_name.strip().lower():
        st.warning("Please enter two different player names.")
    else:
        with st.spinner("Calculating probabilities..."):
            results = compute_player_probabilities(
                player1_name.strip(), player2_name.strip(), surface
            )

        p1 = results["player1"]
        p2 = results["player2"]

        if not p1["found"]:
            st.info(f"No data found for {p1['name']} on {surface}. Using default estimates.")
        if not p2["found"]:
            st.info(f"No data found for {p2['name']} on {surface}. Using default estimates.")

        st.subheader("Prediction Summary")
        st.markdown(
            f"<div class='panel summary-panel'><div><strong>Surface:</strong> {surface}</div><div><strong>Players:</strong> {p1['name']} vs {p2['name']}</div></div>",
            unsafe_allow_html=True,
        )

        summary_cols = st.columns(3, gap="medium")
        for idx, (label, value1, value2) in enumerate(
            [
                ("Service Point Win %", p1["point_win_pct"], p2["point_win_pct"]),
                ("Service Game Win %", p1["game_win_pct"], p2["game_win_pct"]),
                ("Set Win %", p1["set_win_pct_if_serves_first"], p2["set_win_pct_if_serves_first"]),
            ]
        ):
            with summary_cols[idx]:
                st.markdown(
                    f"""
                    <div class="metric-card" style="height: 100%;">
                        <h4><span class="metric-label">{label}</span></h4>
                        <div class="metric-body">
                            <div class="metric-row"><strong>{p1['name']}</strong><span class="metric-value">{value1 * 100:.2f}%</span></div>
                            <div class="metric-row"><strong>{p2['name']}</strong><span class="metric-value">{value2 * 100:.2f}%</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        breakdown_cols = st.columns(2, gap="medium")
        with breakdown_cols[0]:
            st.markdown(
                f"""
                <div class="panel player-card">
                    <div>
                        <h4>{p1['name']}</h4>
                        <p style="margin: 0.2rem 0;"><strong>Serve win %:</strong> {p1['serve_pct'] * 100:.2f}%</p>
                        <p style="margin: 0.2rem 0;"><strong>Return win %:</strong> {p1['return_pct'] * 100:.2f}%</p>
                    </div>
                    <div class="player-bar"><div class="player-fill" style="width: {p1['game_win_pct'] * 100:.0f}%;"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with breakdown_cols[1]:
            st.markdown(
                f"""
                <div class="panel player-card">
                    <div>
                        <h4>{p2['name']}</h4>
                        <p style="margin: 0.2rem 0;"><strong>Serve win %:</strong> {p2['serve_pct'] * 100:.2f}%</p>
                        <p style="margin: 0.2rem 0;"><strong>Return win %:</strong> {p2['return_pct'] * 100:.2f}%</p>
                    </div>
                    <div class="player-bar"><div class="player-fill" style="width: {p2['game_win_pct'] * 100:.0f}%;"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )