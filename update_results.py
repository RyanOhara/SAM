import pandas as pd

if __name__ == "__main__":
    today = pd.read_csv('todays_projections.csv')
    today.to_csv('all_projections.csv', mode='a', index=False, header=False)