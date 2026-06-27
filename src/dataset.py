import pandas as pd
import glob
import os

url = "https://github.com/Tennismylife/TML-Database/blob/master/2025.csv"
df = pd.read_csv(url)

def player_stats(df, player_name):
    winner_df = df[df['winner_name'] == player_name]
    loser_df = df[df['loser_name'] == player_name]

    if len(winner_df) == 0 and len(loser_df) == 0:
        print(f"No data found for player: {player_name}")
        return 0.6, 0.3
    
    svpts_won = winner_df['w_1stWon'].sum() + winner_df['w_2ndWon'].sum() + loser_df['w_1stWon'].sum() + loser_df['w_2ndWon'].sum()
    rtpts_won = winner_df['l_svpt'].sum() - (winner_df['l_1stWon'].sum() + winner_df['l_2ndWon'].sum()) + loser_df['w_svpt'].sum() - (loser_df['w_1stWon'].sum() + loser_df['w_2ndWon'].sum())
    total_svpts = winner_df['w_svpt'].sum() + loser_df['l_svpt'].sum()
    total_rtpts = winner_df['l_svpt'].sum() + loser_df['w_svpt'].sum()

    return svpts_won / total_svpts, rtpts_won / total_rtpts

Jannik_Sinner_Stats = player_stats(df, "Jannik Sinner")
print("Jannik Sinner Stats:", Jannik_Sinner_Stats)