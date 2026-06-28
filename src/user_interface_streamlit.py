import streamlit as st
from markov_modeling import compute_player_probabilities

st.set_page_config(
    page_title="Tennis Match Probability Explorer",
    page_icon="🎾",
    layout="centered",
)

st.title("Tennis Match Probability Explorer")
st.markdown(
    "Use serve and return statistics to estimate the chance each player has to win a point, a game, and a set."
)

with st.sidebar:
    st.header("Player Inputs")
    player1_name = st.text_input("Player 1 name", value="Carlos Alcaraz")
    player2_name = st.text_input("Player 2 name", value="Jannik Sinner")
    surface = st.selectbox("Surface", ["Clay", "Hard", "Grass"], index=0)
    st.markdown(
        "---\n" 
        "Enter two players and choose a surface. The model pulls historical serve/return estimates from the dataset and uses a Markov chain to compute win probabilities."
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
        col1, col2 = st.columns(2)
        col1.metric("Player 1", p1["name"])
        col2.metric("Player 2", p2["name"])

        st.markdown("### Win Probabilities")
        score_cols = st.columns(3)
        score_cols[0].metric("Point Win %", f"{p1['point_win_pct'] * 100:.1f}%", delta=f"{(p1['point_win_pct'] - p2['point_win_pct']) * 100:+.1f}%")
        score_cols[1].metric("Game Win %", f"{p1['game_win_pct'] * 100:.1f}%", delta=f"{(p1['game_win_pct'] - p2['game_win_pct']) * 100:+.1f}%")
        score_cols[2].metric("Set Win % if serves first", f"{p1['set_win_pct_if_serves_first'] * 100:.1f}%", delta=f"{(p1['set_win_pct_if_serves_first'] - p2['set_win_pct_if_serves_first']) * 100:+.1f}%")

        st.markdown("#### Player 1 breakdown")
        st.write(
            f"Serve win %: {p1['serve_pct'] * 100:.1f}%  "
            f"Return win %: {p1['return_pct'] * 100:.1f}%"
        )
        st.progress(min(max(p1['game_win_pct'], 0.0), 1.0))

        st.markdown("#### Player 2 breakdown")
        st.write(
            f"Serve win %: {p2['serve_pct'] * 100:.1f}%  "
            f"Return win %: {p2['return_pct'] * 100:.1f}%"
        )
        st.progress(min(max(p2['game_win_pct'], 0.0), 1.0))

        st.markdown(
            "---\n"
            "### How to view this app\n"
            "Run this command from the repository root: `streamlit run src/user_interface_streamlit.py`\n"
            "Then open `http://localhost:8501` in your browser."
        )