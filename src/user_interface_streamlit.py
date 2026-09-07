import streamlit as st
from concurrent.futures import ThreadPoolExecutor

from dataset import load_dataset
from adjusted_markov_model import compute_player_probabilities


st.set_page_config(
    page_title="Adjusted Markov Model | Tennis Predictions",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)


def percentage(value):
    return f"{value * 100:.1f}%"


default_players = {
    "ATP": ("Carlos Alcaraz", "Jannik Sinner"),
    "WTA": ("Aryna Sabalenka", "Iga Swiatek"),
}


def save_player_inputs():
    tour = st.session_state.tour
    st.session_state.players_by_tour[tour] = (
        st.session_state.player1_name,
        st.session_state.player2_name,
    )


def switch_tour():
    tour = st.session_state.tour
    player1_name, player2_name = st.session_state.players_by_tour[tour]
    st.session_state.player1_name = player1_name
    st.session_state.player2_name = player2_name


def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode


def start_dataset_warmup():
    executor = ThreadPoolExecutor(max_workers=1)
    st.session_state.dataset_warmup_executor = executor
    st.session_state.dataset_warmup = {
        tour: executor.submit(load_dataset, tour) for tour in ("ATP", "WTA")
    }


def player_names_for_tour(tour):
    dataset = st.session_state.dataset_warmup[tour].result()
    winner_stats = dataset[["w_svpt", "w_1stWon", "w_2ndWon"]]
    loser_stats = dataset[["l_svpt", "l_1stWon", "l_2ndWon"]]
    valid_winner_stats = winner_stats.notna().all(axis=1) & (
        winner_stats["w_1stWon"] + winner_stats["w_2ndWon"]
        <= winner_stats["w_svpt"]
    )
    valid_loser_stats = loser_stats.notna().all(axis=1) & (
        loser_stats["l_1stWon"] + loser_stats["l_2ndWon"]
        <= loser_stats["l_svpt"]
    )
    serve_names = set(dataset.loc[valid_winner_stats, "winner_name"].dropna()) | set(
        dataset.loc[valid_loser_stats, "loser_name"].dropna()
    )
    return_names = set(dataset.loc[valid_loser_stats, "winner_name"].dropna()) | set(
        dataset.loc[valid_winner_stats, "loser_name"].dropna()
    )
    names = serve_names & return_names
    normalized_names = {str(name).strip() for name in names if str(name).strip()}
    return sorted(
        name
        for name in normalized_names
        if "." not in name or name.lower().endswith((" jr.", " sr."))
    )


if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "tour" not in st.session_state:
    st.session_state.tour = "ATP"
if "players_by_tour" not in st.session_state:
    st.session_state.players_by_tour = default_players.copy()
if "player1_name" not in st.session_state:
    st.session_state.player1_name = st.session_state.players_by_tour[st.session_state.tour][0]
if "player2_name" not in st.session_state:
    st.session_state.player2_name = st.session_state.players_by_tour[st.session_state.tour][1]
if "dataset_warmup" not in st.session_state:
    start_dataset_warmup()

dark_mode = st.session_state.dark_mode
theme_class = "theme-dark" if dark_mode else "theme-light"

st.markdown(
    f"""
    <style>
    :root {{
        --ink: #17221d;
        --muted: #4d5f54;
        --paper: #f5f6f0;
        --surface: #ffffff;
        --line: #dfe5dc;
        --court: #1d6b54;
        --court-dark: #104638;
        --accent: #ee7659;
        --accent-soft: #fff0eb;
        --shadow: 0 18px 45px rgba(30, 53, 41, 0.10);
    }}
    .stApp:has(.theme-dark) {{
        --ink: #edf5ee;
        --muted: #c0d0c4;
        --paper: #111a16;
        --surface: #1a2821;
        --line: #304238;
        --court: #3da17d;
        --court-dark: #173d30;
        --accent: #ff9477;
        --accent-soft: #3a2721;
        --shadow: 0 18px 45px rgba(0, 0, 0, 0.20);
    }}
    .stApp {{ background: var(--paper); color: var(--ink); color-scheme: light !important; }}
    .stApp:has(.theme-dark) {{ color-scheme: dark !important; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stDecoration"],
    #MainMenu {{ display: none !important; visibility: hidden !important; }}
    [data-testid="stToolbar"] {{ display: flex !important; visibility: visible !important; opacity: 1 !important; }}
    [data-testid="stToolbar"] button[aria-label*="settings" i],
    [data-testid="stToolbar"] button[aria-label*="options" i],
    [data-testid="stToolbar"] button[title*="settings" i],
    [data-testid="stToolbar"] button[title*="options" i] {{ display: none !important; }}
    [data-testid="stHeader"] button[aria-label="Settings"],
    [data-testid="stToolbar"] button[aria-label="Settings"],
    [data-testid="stToolbar"] button[title="Settings"] {{ display: none !important; }}
    [data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--line); }}
    [data-testid="stSidebar"] * {{ color: var(--ink); }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color: var(--muted) !important; }}
    input, textarea {{ background: var(--surface) !important; color: var(--ink) !important; border-color: var(--line) !important; caret-color: var(--accent); }}
    input::placeholder, textarea::placeholder {{ color: var(--muted) !important; opacity: 1; }}
    [data-baseweb="select"] > div {{ background: var(--surface) !important; border: 2px solid var(--court) !important; border-radius: 9px; box-shadow: 0 2px 0 var(--line); color: var(--ink) !important; min-height: 2.8rem; }}
    [data-baseweb="select"] > div:hover, [data-baseweb="select"] > div:focus-within {{ border-color: var(--accent) !important; box-shadow: 0 0 0 3px var(--accent-soft); }}
    [data-baseweb="select"] svg, [data-baseweb="select"] svg path {{ color: var(--accent) !important; fill: var(--accent) !important; stroke: var(--accent) !important; filter: invert(52%) sepia(76%) saturate(1052%) hue-rotate(324deg) brightness(101%) contrast(96%) drop-shadow(0 1px 1px rgba(0,0,0,.25)); }}
    [data-baseweb="select"] [data-testid="stMarkdownContainer"], [data-baseweb="select"] span {{ color: var(--ink) !important; }}
    [data-baseweb="popover"], [role="listbox"], [role="option"] {{ background: var(--surface) !important; color: var(--ink) !important; }}
    [role="option"]:hover, [role="option"][aria-selected="true"] {{ background: var(--accent-soft) !important; color: var(--ink) !important; }}
    .block-container {{ max-width: 1380px; padding: 3.5rem 3rem 4rem; }}
    h1, h2, h3, h4, p, label {{ color: var(--ink) !important; }}
    h1 {{ font-size: clamp(2.5rem, 5vw, 4.7rem) !important; line-height: .95 !important; letter-spacing: -0.06em; margin: 0 !important; }}
    h2 {{ letter-spacing: -0.035em; }}
    .eyebrow {{ color: var(--accent); font-size: .75rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; margin-bottom: 1rem; }}
    .lede {{ color: var(--muted) !important; font-size: 1.08rem; line-height: 1.6; max-width: 620px; margin: 1.25rem 0 0; }}
    .hero {{ display: flex; justify-content: space-between; gap: 2rem; align-items: end; padding-bottom: 2.8rem; border-bottom: 1px solid var(--line); margin-bottom: 2rem; }}
    .hero-mark {{ color: var(--court); font-size: 5rem; line-height: 1; transform: rotate(-18deg); opacity: .85; }}
    .section-label {{ color: var(--muted); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin: 2rem 0 .8rem; }}
    .context {{ background: var(--court-dark); border-radius: 14px; color: #f4fff8; padding: 1rem 1.25rem; display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap; box-shadow: var(--shadow); }}
    .context span {{ color: #a8d5bd; font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }}
    .context strong {{ color: #ffffff; display: block; font-size: 1.05rem; margin-top: .25rem; }}
    .metric {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 1.25rem; min-height: 156px; box-shadow: var(--shadow); }}
    .metric-title {{ color: var(--muted); font-size: .78rem; font-weight: 800; letter-spacing: .04em; text-transform: uppercase; }}
    .metric-value {{ color: var(--court); font-size: 2rem; font-weight: 800; letter-spacing: -.04em; margin-top: 1rem; }}
    .metric-name {{ color: var(--ink); font-size: .9rem; margin-top: .15rem; overflow-wrap: anywhere; }}
    .player {{ background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 1.4rem; box-shadow: var(--shadow); height: 100%; }}
    .player-header {{ align-items: center; display: flex; gap: .8rem; margin-bottom: 1.4rem; }}
    .player-badge {{ align-items: center; background: var(--accent-soft); border-radius: 50%; color: var(--accent); display: flex; font-size: 1rem; font-weight: 900; height: 2.4rem; justify-content: center; width: 2.4rem; }}
    .player-name {{ color: var(--ink); font-size: 1.3rem; font-weight: 800; overflow-wrap: anywhere; }}
    .stat-row {{ border-top: 1px solid var(--line); display: flex; justify-content: space-between; padding: .85rem 0; }}
    .stat-row span {{ color: var(--muted); }}
    .stat-row strong {{ color: var(--ink); }}
    .stat-row.primary strong {{ color: var(--court); font-size: 1.15rem; }}
    .note {{ color: var(--muted); font-size: .85rem; margin-top: .8rem; }}
    .stButton > button {{ background: var(--accent) !important; border: 0 !important; border-radius: 8px; color: #ffffff !important; font-weight: 800; min-height: 3rem; width: 100%; }}
    .stButton > button:hover, .stButton > button:focus {{ background: #d75e45 !important; border: 0 !important; color: #ffffff !important; }}
    [data-testid="stExpander"] {{ background: var(--surface); border: 1px solid var(--line); }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p, [data-testid="stExpander"] svg {{ color: var(--ink) !important; fill: var(--ink) !important; }}
    [data-testid="stExpander"] summary:hover {{ background: var(--accent-soft); }}
    [data-testid="stSidebar"] button, [data-testid="stHeader"] button {{ color: var(--ink) !important; }}
    [data-testid="stSidebar"] button svg, [data-testid="stHeader"] button svg {{ fill: var(--ink) !important; stroke: var(--ink) !important; }}
    [data-testid="stSidebar"] [data-baseweb="checkbox"] label, [data-testid="stSidebar"] [data-baseweb="checkbox"] span {{ color: var(--ink) !important; }}
    [data-testid="stSidebar"] [role="switch"] {{ background: var(--line) !important; border: 2px solid var(--muted) !important; height: 1.5rem; width: 2.9rem; }}
    [data-testid="stSidebar"] [role="switch"] > div {{ background: var(--surface) !important; border: 1px solid var(--muted) !important; box-shadow: 0 1px 3px rgba(0,0,0,.35); }}
    [data-testid="stSidebar"] [role="switch"][aria-checked="true"] {{ background: var(--court) !important; border-color: var(--court) !important; }}
    [data-testid="stSidebar"] [data-testid="stToggle"] [role="switch"], [data-testid="stSidebar"] [data-testid="stCheckbox"] [role="switch"] {{ background: #eef2ed !important; border: 2px solid #185f4b !important; border-radius: 999px !important; box-sizing: border-box; }}
    [data-testid="stSidebar"] [data-testid="stToggle"] [role="switch"][aria-checked="true"], [data-testid="stSidebar"] [data-testid="stCheckbox"] [role="switch"][aria-checked="true"] {{ background: #258363 !important; border-color: #185f4b !important; }}
    [data-testid="stSidebar"] [data-testid="stToggle"] [role="switch"] > div, [data-testid="stSidebar"] [data-testid="stCheckbox"] [role="switch"] > div {{ background: #ffffff !important; border: 1px solid #185f4b !important; box-shadow: 0 1px 3px rgba(16, 70, 56, .35); }}
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label {{ align-items: center; background: var(--accent-soft); border: 1px solid var(--accent); border-radius: 9px; display: flex; gap: .7rem; padding: .7rem .8rem; }}
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label p {{ color: var(--ink) !important; font-size: .95rem; font-weight: 800; }}
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {{ display: block !important; opacity: 1 !important; visibility: visible !important; }}
    [data-testid="collapsedControl"] button, [data-testid="stSidebarCollapseButton"] button {{ background: var(--accent) !important; border: 2px solid var(--court) !important; border-radius: 10px !important; box-shadow: 0 4px 14px rgba(16, 70, 56, .28); color: #ffffff !important; min-height: 2.5rem; min-width: 2.5rem; }}
    [data-testid="collapsedControl"] button:hover, [data-testid="stSidebarCollapseButton"] button:hover {{ background: var(--court) !important; transform: translateY(-1px); }}
    [data-testid="collapsedControl"] button svg, [data-testid="collapsedControl"] button svg path, [data-testid="stSidebarCollapseButton"] button svg, [data-testid="stSidebarCollapseButton"] button svg path {{ color: #ffffff !important; fill: none !important; stroke: #ffffff !important; stroke-width: 2.5; }}
    .mode-button {{ background: var(--accent-soft); border: 2px solid var(--accent); border-radius: 10px; color: var(--ink); font-size: .9rem; font-weight: 800; padding: .7rem .85rem; text-align: center; }}
    @media (max-width: 700px) {{
        .block-container {{ padding: 2rem 1.1rem 3rem; }}
        .hero {{ align-items: start; padding-bottom: 2rem; }}
        .hero-mark {{ font-size: 3rem; }}
    }}
    </style>
    <div class="{theme_class}"></div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    mode_label = "Switch to light mode" if dark_mode else "Switch to dark mode"
    st.button(
        mode_label,
        key="mode_button",
        use_container_width=True,
        on_click=toggle_dark_mode,
    )
    st.markdown("## Match setup")
    st.caption("Choose a matchup and court surface to model the probabilities.")
    tour = st.selectbox("Tour", ["ATP", "WTA"], key="tour", on_change=switch_tour)
    player_names = player_names_for_tour(tour)
    for player_key, default_name in zip(
        ("player1_name", "player2_name"), default_players[tour]
    ):
        if st.session_state[player_key] not in player_names:
            st.session_state[player_key] = (
                default_name if default_name in player_names else player_names[0]
            )
    player1_name = st.selectbox(
        "Player 1", player_names, key="player1_name", on_change=save_player_inputs
    )
    player2_name = st.selectbox(
        "Player 2", player_names, key="player2_name", on_change=save_player_inputs
    )
    surface = st.selectbox("Surface", ["Hard", "Clay", "Grass"])
    st.markdown("---")
    st.caption("Rates are estimated from the match dataset. Unknown players use default estimates.")


st.markdown(
    """
    <div class="hero">
        <div>
            <div class="eyebrow">Adjusted Markov Model | Tennis Predictions</div>
            <h1>Adjusted Markov Chain<br>Tennis Model</h1>
            <p class="lede">How serve strength, return quality, and surface, based on historical point data shape the path from point to set.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Match configuration</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="context">
        <div><span>Tour</span><strong>{tour}</strong></div>
        <div><span>Surface</span><strong>{surface}</strong></div>
        <div><span>Player 1</span><strong>{player1_name.strip() or 'Not selected'}</strong></div>
        <div><span>Player 2</span><strong>{player2_name.strip() or 'Not selected'}</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("Calculate match probabilities", type="primary"):
    if not player1_name.strip() or not player2_name.strip():
        st.warning("Please enter names for both players.")
    elif player1_name.strip().lower() == player2_name.strip().lower():
        st.warning("Please enter two different player names.")
    else:
        with st.spinner("Running the point-to-set model..."):
            st.session_state.dataset_warmup[tour].result()
            results = compute_player_probabilities(
                player1_name.strip(), player2_name.strip(), surface, tour
            )

        p1, p2 = results["player1"], results["player2"]
        st.markdown('<div class="section-label">Projected win rates</div>', unsafe_allow_html=True)
        summary = [
            ("Service point", p1["point_win_pct"], p2["point_win_pct"]),
            ("Service game", p1["game_win_pct"], p2["game_win_pct"]),
            ("Set win %", p1["set_win_pct"], p2["set_win_pct"]),
        ]
        metric_cols = st.columns(3, gap="medium")
        for column, (label, p1_value, p2_value) in zip(metric_cols, summary):
            with column:
                st.markdown(
                    f"""
                    <div class="metric">
                        <div class="metric-title">{label}</div>
                        <div class="metric-value">{percentage(p1_value)}</div>
                        <div class="metric-name">{p1['name']}</div>
                        <div class="metric-value">{percentage(p2_value)}</div>
                        <div class="metric-name">{p2['name']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-label">Serve vs return profile</div>', unsafe_allow_html=True)
        player_cols = st.columns(2, gap="medium")
        for column, player, badge in zip(player_cols, (p1, p2), ("1", "2")):
            with column:
                source_note = "Dataset profile" if player["found"] else "Default estimate"
                st.markdown(
                    f"""
                    <div class="player">
                        <div class="player-header"><div class="player-badge">{badge}</div><div class="player-name">{player['name']}</div></div>
                        <div class="stat-row primary"><span>Win on serve</span><strong>{percentage(player['serve_pct'])}</strong></div>
                        <div class="stat-row primary"><span>Win on return</span><strong>{percentage(player['return_pct'])}</strong></div>
                        <div class="stat-row"><span>Service point win</span><strong>{percentage(player['point_win_pct'])}</strong></div>
                        <div class="stat-row"><span>Service game win</span><strong>{percentage(player['game_win_pct'])}</strong></div>
                        <div class="stat-row"><span>Set win %</span><strong>{percentage(player['set_win_pct'])}</strong></div>
                        <div class="note">{source_note} on {surface}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
