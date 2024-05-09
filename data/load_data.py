from api.api_clients import fetch_market_data, fetch_top_investors_data, fetch_news_data, fetch_social_media_data
from features.feature_engineering import FeatureEngineeringPipeline 
from joblib import Parallel, delayed
import numpy as np
import pandas as pd

def process_individual_data(data, key):
    """Attempt to convert raw data to DataFrame and mark its source."""
    try:
        df = pd.DataFrame(data)
        df['source'] = key
        return df
    except ValueError:
        print(f"Error processing data from source {key}. Skipping...")
        return pd.DataFrame()

def clean_and_normalize_data(data_frames):
    """Clean and normalize a list of DataFrames."""
    combined_df = pd.concat(data_frames, ignore_index=True, sort=False)
    combined_df.dropna(axis=0, thresh=int(0.5 * combined_df.shape[1]), inplace=True)
    combined_df.fillna(method='ffill', inplace=True)
    numerical_cols = combined_df.select_dtypes(include=np.number).columns
    combined_df[numerical_cols] = (combined_df[numerical_cols] - combined_df[numerical_cols].mean()) / combined_df[numerical_cols].std()
    return combined_df

def load_historical_data(start_year):
    # Assuming data filenames are formatted as 'historical/stock_data_{start_year}_to_{end_year}.csv'
    filename = f'historical/stock_data_{start_year}_to_2024.csv'
    data = pd.read_csv(filename)
    
    cleaned_data = clean_and_normalize_data(data)
    return cleaned_data

def load_real_time_data():
    """Fetch and process real-time data using similar sources as historical data."""
    # Assuming the same sources have real-time equivalents
    real_time_market_data = fetch_market_data(real_time=True)
    real_time_news_data = fetch_news_data(real_time=True)
    
    raw_data = {
        'real_time_market': real_time_market_data,
        'real_time_news': real_time_news_data
    }
    
    data_frames = Parallel(n_jobs=-1)(delayed(process_individual_data)(data, key) for key, data in raw_data.items())
    cleaned_data = clean_and_normalize_data(data_frames)
    return cleaned_data

def get_features_and_targets(data):
    """Extract features and targets using feature engineering pipeline."""
    pipeline = FeatureEngineeringPipeline()
    features, targets = pipeline.fit_transform(data)
    return features, targets

if __name__ == '__main__':
    # Example usage
    historical_data = load_historical_data()
    features, targets = get_features_and_targets(historical_data)
    print("Features and Targets from Historical Data:", features, targets)

    real_time_data = load_real_time_data()
    real_time_features, real_time_targets = get_features_and_targets(real_time_data)
    print("Features and Targets from Real-Time Data:", real_time_features, real_time_targets)

