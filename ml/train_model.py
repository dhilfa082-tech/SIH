import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# =========================================================
# AGRILINK AI
# MARKET PRICE PREDICTION MODEL
# =========================================================

print("=" * 70)
print("AGRILINK AI - MARKET PRICE MODEL TRAINING")
print("=" * 70)

# ---------------------------------------------------------
# 1. Load cleaned dataset
# ---------------------------------------------------------

file_path = Path("cleaned_market_data.csv")

df = pd.read_csv(file_path)

print("\nDataset loaded successfully!")
print("Dataset shape:", df.shape)

# ---------------------------------------------------------
# 2. Define input features and target
# ---------------------------------------------------------

features = [
    "Year",
    "Month",
    "Day",
    "Arrival Quantity",
    "Min Price",
    "Max Price",
    "Previous_Modal_Price"
]

target = "Modal Price"

X = df[features]
y = df[target]

print("\nInput Features:")
print(features)

print("\nTarget:")
print(target)

# ---------------------------------------------------------
# 3. Time-based train/test split
# ---------------------------------------------------------
# We do NOT randomly shuffle historical data.
# Earlier data is used for training and later data for testing.

split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# ---------------------------------------------------------
# 4. Train Random Forest Model
# ---------------------------------------------------------

print("\nTraining Random Forest model...")

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("Model training completed!")

# ---------------------------------------------------------
# 5. Make predictions
# ---------------------------------------------------------

predictions = model.predict(X_test)

# ---------------------------------------------------------
# 6. Evaluate the model
# ---------------------------------------------------------

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
rmse = mse ** 0.5
r2 = r2_score(y_test, predictions)

print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print(f"\nMAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R² Score : {r2:.4f}")

# ---------------------------------------------------------
# 7. Show sample predictions
# ---------------------------------------------------------

results = pd.DataFrame({
    "Actual Price": y_test.values,
    "Predicted Price": predictions
})

print("\n" + "=" * 70)
print("SAMPLE PREDICTIONS")
print("=" * 70)

print(results.head(10).to_string(index=False))

# ---------------------------------------------------------
# 8. Save model
# ---------------------------------------------------------

model_path = Path("agrilink_price_model.pkl")

joblib.dump(model, model_path)

print("\n" + "=" * 70)
print("MODEL SAVED SUCCESSFULLY")
print("=" * 70)

print("\nModel location:")
print(model_path.resolve())

print("\nAgriLink AI ML model training completed successfully!")