# ============================================================
# DEMAND FORECASTING & INVENTORY OPTIMIZATION
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ================= LOAD DATA =================

def load_data(path):
    df = pd.read_csv(path)
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    return df

# ================= FORECAST =================

def forecast_demand(df):
    df['Date'] = pd.to_datetime(df['Date'])
    ts = df.set_index('Date')['Demand']

    model = SARIMAX(ts, order=(1,1,1), seasonal_order=(1,1,1,2))
    model_fit = model.fit(disp=False)

    forecast = model_fit.predict(len(ts), len(ts) + 9)
    return forecast, ts

# ================= OPTIMIZATION =================

def optimize_inventory(forecast):
    initial_inventory = 5500
    lead_time = 1
    service_level = 0.85

    z = np.abs(np.percentile(forecast, 100 * (1 - service_level)))

    order_quantity = int(np.ceil(forecast.mean() + z))
    reorder_point = forecast.mean() * lead_time + z
    safety_stock = reorder_point - forecast.mean() * lead_time

    holding_cost = 0.1
    stockout_cost = 10

    total_holding_cost = holding_cost * (initial_inventory + 0.5 * order_quantity)
    total_stockout_cost = stockout_cost * max(0, forecast.mean() * lead_time - initial_inventory)

    total_cost = total_holding_cost + total_stockout_cost

    return order_quantity, reorder_point, safety_stock, total_cost

# ================= COST COMPARISON =================

def cost_comparison(forecast):
    initial_inventory = 5500
    avg_demand = forecast.mean()

    holding_cost = 0.1
    stockout_cost = 10

    naive_cost = (
        holding_cost * initial_inventory +
        stockout_cost * max(0, avg_demand - initial_inventory)
    )

    _, _, _, optimized_cost = optimize_inventory(forecast)

    return naive_cost, optimized_cost

# ================= MAIN =================

def main():

    print("🔹 Loading data...")
    df = load_data("data/demand_inventory.csv")

    print("🔹 Forecasting demand...")
    forecast, ts = forecast_demand(df)

    # ===== GRAPH =====
    future_dates = pd.date_range(start=ts.index[-1] + pd.Timedelta(days=1), periods=len(forecast))

    plt.figure(figsize=(10,5))
    plt.plot(ts, label="Actual Demand")
    plt.plot(future_dates, forecast, '--', label="Forecast")
    plt.title("Demand Forecast")
    plt.legend()
    plt.show()

    print("\n🔹 Optimizing inventory...")
    oq, rp, ss, cost = optimize_inventory(forecast)

    print("\n===== RESULTS =====")
    print("Optimal Order Quantity:", oq)
    print("Reorder Point:", round(rp, 2))
    print("Safety Stock:", round(ss, 2))
    print("Total Cost:", round(cost, 2))

    # ===== COST COMPARISON =====
    naive_cost, optimized_cost = cost_comparison(forecast)

    print("\n===== COST COMPARISON =====")
    print("Before Optimization:", round(naive_cost, 2))
    print("After Optimization:", round(optimized_cost, 2))

    improvement = ((naive_cost - optimized_cost) / naive_cost) * 100
    print("Cost Reduction (%):", round(improvement, 2))


if __name__ == "__main__":
    main()