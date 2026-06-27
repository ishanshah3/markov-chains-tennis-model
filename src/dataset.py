import pandas as pd

url = "https://raw.githubusercontent.com/Tennismylife/TML-Database/refs/heads/master/2025.csv"
df = pd.read_csv(url)

def player_stats(df, player_name, surface="Clay"):
    player_name_lower = player_name.strip().lower()
    surface_df = df[df['surface'] == surface]
    winner_df = surface_df[surface_df['winner_name'].astype(str).str.lower() == player_name_lower]
    loser_df = surface_df[surface_df['loser_name'].astype(str).str.lower() == player_name_lower]

    if surface_df.shape[0] == 0:
        print(f"No data found for {player_name} on {surface}.")
        return 0.6, 0.3

    if len(winner_df) == 0 and len(loser_df) == 0:
        print(f"No data found for {player_name} on {surface}.")
        return 0.6, 0.3

    svpts_won = winner_df['w_1stWon'].sum() + winner_df['w_2ndWon'].sum() + loser_df['w_1stWon'].sum() + loser_df['w_2ndWon'].sum()
    rtpts_won = winner_df['l_svpt'].sum() - (winner_df['l_1stWon'].sum() + winner_df['l_2ndWon'].sum()) + loser_df['w_svpt'].sum() - (loser_df['w_1stWon'].sum() + loser_df['w_2ndWon'].sum())
    total_svpts = winner_df['w_svpt'].sum() + loser_df['l_svpt'].sum()
    total_rtpts = winner_df['l_svpt'].sum() + loser_df['w_svpt'].sum()

    return svpts_won / total_svpts, rtpts_won / total_rtpts

serve1, return1 = player_stats(df, "Carlos Alcaraz", "Clay")
serve2, return2 = player_stats(df, "Jannik Sinner", "Clay")
print(f"Player 1 - Serve: {serve1}, Return: {return1}")
print(f"Player 2 - Serve: {serve2}, Return: {return2}")