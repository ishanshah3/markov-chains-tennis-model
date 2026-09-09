# markov-chains-tennis-model

This project aims to use adjusted Markov modeling to more accurately predict the results of both ATP and WTA singles tennis matches.

## Key Features

- Markov model based on serve and return % of players
- Includes historical data with point importance time decay with half-life of 180 days
- User friendly UI to predict H2H matches
- Data filtered by court surface to match performance on a specific surface
- Blended with tour data to make sure new players are more stable

## Mathematical Explanation

A Markov chain is a system that moves from one condition, or state, to another with a certain probability. For example, going from 0-0 to 15-0 in a tennis game has a certain probability p for player 1 (serving), which is their probability of winning the point.

### Base Markov Model

For games, there are 15 transition states, which can be organized in a 15 x 15 matrix (called Q in this project). In this first matrix, the serving player, player 1, wins a point with probability p, and loses with probability 1 - p = q. When a player wins the game, it goes to an absorption state in a separate 15 x 2 matrix, R. For example, if player 1 is winning 40 - 0, they move to the absorption state with probability p. This would look like R[6,0] = p, where state 6 is 40 - 0, and 0 is the column where player 1 wins.

Matrix Q is subtracted from the identity matrix I, and then the inverse is determined. This accounts for all possible, and repeated transitions between states, and gives the expected number of visits to a certain state starting from another state. This inverse, called N, is then multiplied with R to represent the probability of a player winning from each state. This can also be used to find the leverage, or importance, of a singular point.

The same is done with the set, but instead of only 15 states, it has 39. In this case, we use the previous probability calculated from the game and plug that in as the probability for moving states in this set matrix, which will, after the same process, eventually spit out the likelihood each player will have to win a set based on their adjusted serve win %, described below.

### Adjusted Player Serve Win %

This model includes their opponent's return strength and also weights it against the tour average return strength to give a more precise point win % on serve.

This model takes the geometric mean of the average serve and (1 - return) win probabilities and calls it W_1. W_2 is the geometric mean of (1 - the average serve) and the return win probabilities to have a good tour baseline for each surface.

For the exact equation, let s be the server's point win %, and r be the returner's point win %. The equation would look like s(1 - r)/W_1/(((s(1 - r))/W_1) + (1 - s)r/W_2). This just takes the serve win % and compares it with the opponent's return win % and the tour average to make a solid estimate for the server's chance to win a point.

### Data Decay

Over a 180-day period, the points a player plays have exactly half the value they would have today. This prioritizes recent matches and performance over past performance, but also does take into consideration all past history, even if it has a very low relative value.

The exact equation used is 0.5 ^ (days ago/180), so a point today has a value of 1, a point 180 days ago has value of 0.5, and a point 360 days ago has value of 0.25 points.

### Data Blending

Newer players or those with less tour data can have extreme stats due to a smaller sample size. To counter this, 100 points of tour average data is added to both the serve and return stats of every player per surface. This would be a major source of stats for beginning players, but negligible for players who have been playing for years. However, the point value decay makes past points worth much less, so when added up, the total points for a player is often significantly less than what the raw data suggests. Here, the model reamplifies the decayed totals to the raw totals for both serve and return on the specific surface, which maintains the ratio from the decay, but also the confidence and protection from blending to the tour average.

The exact equation used is (total service/return pts * % of pts won + 100 * tour % of pts won)/(total service/return pts + 100). If a player had 100 total service pts, 50% of their data would be from the tour average, but if another player had 10000 total service pts, less than 0.1% of their data would be from the tour average.

## Data

ATP and WTA databases use match data and statistics from [Tennis My Life](https://stats.tennismylife.org/tennis-match-database) (TML). TML is credited as the data source, and the TML data is available under the [MIT License](https://opensource.org/license/MIT).

Historical data is read from the local CSV files. The app refreshes current-year and ongoing ATP/WTA data from TML when it starts, using the local current-year files as fallbacks if TML is unavailable. Refreshed data is held in local memory and is not written back to the repository. Historical corrections require updating the local CSV files.

## Future Improvements/Goals

- Fix tiebreak logic due to changing servers
- Factor in momentum, pressure, and H2H results
- Analyze the serve to find the ideal aggressivenes and whether that changes based on the score
- Experiment with how single points or games can impact the chances for winning entire matches
- Create a live website that can predict matches at any given point from the live score between players

## How to Run

Go to the streamlit app:

https://markov-chains-tennis-model.streamlit.app/

## License

This project's original code is available under the [MIT License](https://opensource.org/license/MIT). The third-party TML data used by the project is also available under the [MIT License](https://opensource.org/license/MIT), with Tennis My Life credited as the source.