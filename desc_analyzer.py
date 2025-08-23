import pandas as pd

def perform_analysis(input_file="myntra_bags_cleaned.csv", output_file="myntra_analysis_report.csv"):
    
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        print("Please run the scraper and cleaner scripts first.")
        return

    # Open the file in write mode to save the report
    with open(output_file, 'w') as f:
        f.write("E-commerce Product Pricing Analysis \n\n")

        f.write("1. Descriptive Statistics for Prices and Ratings \n")
        stats = df[['SalePrice', 'MRP', 'Rating']].describe()
        stats.to_csv(f, mode='a') 
        f.write("\n") # Add a newline for spacing

        f.write("2. Top 5 Brands by Number of Products \n")
        top_5_brands_by_count = df['Brand'].value_counts().head(5).to_frame()
        top_5_brands_by_count.to_csv(f, mode='a')
        f.write("\n")

        
        f.write("3. Top 5 Brands by Highest Average Discount \n")
        avg_discount_by_brand = df.groupby('Brand')['DiscountPercentage'].mean().sort_values(ascending=False).head(5).round(2).to_frame()
        avg_discount_by_brand.to_csv(f, mode='a')
        f.write("\n")

        
        f.write("4. Pricing and Rating Trends by Top 5 Sub-Categories\n")
        
        df['SubCategory'] = df['ProductName'].apply(lambda x: x.split()[0].title() if isinstance(x, str) else 'Unknown')
        top_5_subcategories = df['SubCategory'].value_counts().head(5).index.tolist()
        top_cat_df = df[df['SubCategory'].isin(top_5_subcategories)]
        category_insights = top_cat_df.groupby('SubCategory').agg(
            NumberOfProducts=('ProductName', 'count'),
            AverageSalePrice=('SalePrice', 'mean'),
            AverageRating=('Rating', 'mean')
        ).sort_values(by='NumberOfProducts', ascending=False).round(2)
        category_insights.to_csv(f, mode='a')
        f.write("\n")
        
    print(f"Analysis complete. Report saved to '{output_file}'")

if __name__ == "__main__":
    perform_analysis()