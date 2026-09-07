# markov-chains-tennis-simulation

This project aims to use altered markov chains to more accurately predict the results of both ATP and WTA singles tennis matches.

## Key Features

- Markov model based on serve and return % of players
- Includes all-time data with point importance time decay with half-life of 180 days
- User friendly UI to predict H2H matches
- Data filtered by court surface to match performance on a specific surface

## How It Works



## Data

ATP and WTA databases use match data and statistics from [Tennis My Life](https://stats.tennismylife.org/tennis-match-database) (TML) - [MIT License](https://opensource.org/license/MIT).

Historical data is read from the local CSV files. The app refreshes current-year and ongoing ATP/WTA data from TML when it starts, using the local current-year files as fallbacks if TML is unavailable. Refreshed data is held in local memory and is not written back to the repository. Historical corrections require updating the local CSV files.

## Future Improvements/Goals



## How to Run



## License

This project is under a [MIT License](https://opensource.org/license/MIT)