import pandas as pd
import numpy as np

def clean_data(input_file="myntra_bags_raw.csv", output_file="myntra_bags_cleaned.csv"):
    """
    Cleans the raw scraped data and prepares it for analysis.
    """
    df = pd.read_csv(input_file)
    print(f"Initial data shape: {df.shape}")

    # --- 1. Remove Duplicates ---
    df.drop_duplicates(subset=["URL"], inplace=True)
    print(f"Shape after dropping duplicates: {df.shape}")

    # --- 2. Handle Missing Values ---
    # For Rating and NumberOfReviews, NaN implies the product is not yet rated. We can fill with 0.
    df['Rating'].fillna(0, inplace=True)
    df['NumberOfReviews'].fillna('0', inplace=True)

    # --- 3. Convert Data Types ---
    # Prices: Remove 'Rs. ' and commas, then convert to numeric
    df['MRP'] = df['MRP'].str.replace('Rs. ', '').str.replace(',', '').astype(float)
    df['SalePrice'] = df['SalePrice'].str.replace('Rs. ', '').str.replace(',', '').astype(float)
    
    # Rating: Convert to numeric
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(0)

    # Number of Reviews: Handle 'k' for thousands
    def convert_reviews_to_int(review_str):
        if isinstance(review_str, str):
            review_str = review_str.lower()
            if 'k' in review_str:
                return int(float(review_str.replace('k', '')) * 1000)
            return int(review_str)
        return int(review_str)

    df['NumberOfReviews'] = df['NumberOfReviews'].apply(convert_reviews_to_int)

    # --- 4. Feature Engineering: Create Discount Percentage Column ---
    # Avoid division by zero where MRP is 0 or equal to sale price
    df['DiscountPercentage'] = np.where(
        df['MRP'] > 0,
        round(((df['MRP'] - df['SalePrice']) / df['MRP']) * 100, 2),
        0
    )

    # --- 5. Standardize Brand Names (Example) ---
    # This is a simple example; more complex cases might require regex or fuzzy matching.
    df['Brand'] = df['Brand'].str.strip().str.title()
    
    # Reorder columns for clarity
    df = df[[
        "Brand", "ProductName", "Category", "MRP", "SalePrice", 
        "DiscountPercentage", "Rating", "NumberOfReviews", "URL"
    ]]

    # --- Save Cleaned Data ---
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}. Final shape: {df.shape}")
    print("\nData Cleaning Complete. Sample of cleaned data:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    clean_data()