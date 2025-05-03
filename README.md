# 🏆 Global IMC Prosperity Challenge: Finished in Top 2% 

**Global Rank 352** | **Country Rank 55**  

<img width="1439" alt="Screenshot 2025-05-03 at 7 30 22 AM" src="https://github.com/user-attachments/assets/dd00eb6d-34c0-4593-b335-74d427eae4be" />

This repository contains the solution developed for the **Global IMC Prosperity Challenge**, where We achieved a **Global Rank of 352**(Top 2% in 20000 ) and a **Country Rank of 55**(Top 1% 6000+). The challenge consisted of five rounds, each introducing new tradable products and algorithmic/manual trading tasks.The strategy adapts to evolving market conditions across multiple rounds, employing statistical arbitrage, mean reversion, and volatility-based approaches. Below is a detailed explanation of each round's problem statement and the solution implemented in the trading algorithm (`trader.py`).

## 🚀 Key Features

- **5 Independent Trading Engines** - Dedicated strategies per product class
- **Dynamic Risk Management** - Position limits, adverse selection filters
- **Quantitative Models** - VWAP/SMA arbitrage, Black-Scholes-inspired volatility surfaces
- **Sunlight-Sensitive Pricing** - CSI threshold detection for macarons
- **Multi-Product Arbitrage** - Picnic basket component optimization

## 📈 Round-by-Round Breakdown

### Round 1: Foundational Strategies
| Product          | Strategy                          | Key Innovation                     |
|------------------|-----------------------------------|------------------------------------|
| 🌿 Rainforest Resin | Market Making                    | Fixed fair value (10,000 shells)   |
| 🌊 Kelp           | Mean Reversion (β=-0.229)        | Elasticity-adjusted pricing        |
| 🦑 Squid Ink      | Volatility Filtering             | Adverse volume detection           |

**Problem Statement**:  
Three tradable products were introduced: **Rainforest Resin**, **Kelp**, and **Squid Ink**, each with a position limit of 50.  
- **Rainforest Resin**: Stable value over time.  
- **Kelp**: Prices fluctuate up and down.  
- **Squid Ink**: Volatile with large price swings but exhibits short-term price reversion.  
A hint suggested tracking deviations from recent averages to exploit Squid Ink's reversion tendencies.

**Solution**:  
The trading algorithm implemented a multi-strategy approach:  
- **Rainforest Resin**: Used a fair value of 10,000 SeaShells and employed market-making with a fixed spread. Orders were placed to buy below and sell above the fair value, with position management to avoid exceeding a soft limit of 30.  
- **Kelp**: Applied a mean-reversion strategy based on the reversion beta (-0.229). The fair value was calculated using the mid-price adjusted by predicted returns from the previous price change.  
- **Squid Ink**: The algorithm focused on safer products to avoid adverse price movements.  
The algorithm used functions like `take_orders`, `clear_orders`, and `make_orders` to execute trades, manage positions, and prevent adverse selections by filtering large orders.

```python
# Kelp Mean Reversion Core Logic
pred_returns = last_returns * reversion_beta
fair_value = mid_price + (mid_price * pred_returns)
```
### Manual Challenge
**Problem Statement**:  
Participants converted SeaShells into foreign currencies and back, aiming to maximize SeaShells through a series of trades.

**Solution**
We use optimization technique to maximize profit.

### Round 2: Basket Arbitrage Mastery
![Basket Arbitrage Diagram](https://example.com/basket-arb.jpg)  
*Component spread trading framework*

**Key Components:**
- 🥐 Croissant VWAP Tracking
- 🧺 Basket 1/2 Spread Analysis
- 🔢 Z-Score Thresholding (1.5σ)
  
**Problem Statement**:  
Two new tradable products, **Picnic Basket1** and **Picnic Basket2**, were introduced alongside their components (**Croissants**, **Jams**, **Djembes**).  
- **Picnic Basket1**: 6 Croissants, 3 Jams, 1 Djembes (position limit: 60).  
- **Picnic Basket2**: 4 Croissants, 2 Jams (position limit: 100).  
- Component limits: Croissants (250), Jams (350), Djembes (60).  
The challenge involved trading baskets and components to exploit pricing inefficiencies.

**Solution**:  
The algorithm implemented:  
- **Djembes and Picnic Basket1**: Mean-reversion strategies using log-price histories. Fair values were calculated with a rolling window (200 timestamps) and adjusted using a mean-reversion parameter (theta: 0.005 for Djembes, 0.02 for Picnic Basket1). Orders were placed to buy undervalued and sell overvalued assets.  
- **Croissants**: A VWAP-based strategy. The algorithm calculated the volume-weighted average price (VWAP) and placed buy orders below a threshold (0.995 * VWAP) and sell orders above (1.005 * VWAP). It also supported conversions to unwind short positions when profitable.  
- **Picnic Basket2 and Jams**: Mean-reversion trading based on VWAP and simple moving averages (SMA). The algorithm entered positions when the z-score exceeded ±1.5 and the price deviated from the SMA, exiting when profit targets (1%) were met. Market-making was used in low-volatility conditions.  
The algorithm managed position limits and used adverse volume filters to avoid large, risky trades.

### Manual Challenge
**Problem Statement**:  
Participants chose up to two shipping containers with treasures (base treasure: 10,000 SeaShells, multiplier up to 90). The first container was free, but the second cost SeaShells. Profits were divided by the number of inhabitants choosing the same container and the container's selection percentage.

**Solution**:  
We had the option to choose two containers, but we chose only one, as the second container required a fee of 50,000 seashells and we knew there was a very low probability of making a profit from it. In the end, we made a good profit by avoiding the second container and choosing the first, more optimal one.

### Round 3: Volcanic Derivatives
**Volcanic Rock Voucher Strategy Matrix**

| Strike Price | Position Strategy          | Exit Trigger                |
|--------------|----------------------------|-----------------------------|
| 9,500        | Aggressive Shorts          | 75th Percentile Cross       |
| 10,000       | Balanced Portfolio Anchor  | Dual Percentile Trapping    |
| 10,500       | Volatility Plays           | Momentum Fade               |

**Problem Statement**:  
**Volcanic Rock** and five **Volcanic Rock Vouchers** (strike prices: 9,500, 9,750, 10,000, 10,250, 10,500 SeaShells) were introduced. Vouchers had a 7-day expiration and position limits of 200 (Volcanic Rock: 400). A hint suggested using a Black-Scholes implied volatility model and plotting it against a normalized metric to identify trading opportunities.

**Solution**:  
The algorithm implemented a percentile-based trading strategy for Volcanic Rock and its vouchers:  
- **Volcanic Rock and Vouchers**: Maintained a trade history (window: 2000 timestamps) to calculate the 50th and 75th percentiles of mid-prices.  
  - **Long Entry**: Bought when the mid-price crossed above the 50th percentile from below.  
  - **Long Exit**: Sold when the mid-price crossed above the 75th percentile.  
  - **Short Entry**: Sold when the mid-price crossed below the 75th percentile from above.  
  - **Short Exit**: Bought back when the mid-price crossed below the 50th percentile.  
The algorithm tracked positions and ensured compliance with limits, logging trades for transparency. The Black-Scholes hint was not directly implemented, possibly due to complexity, but the percentile strategy captured price momentum and reversions effectively.

### Manual Challenge
**Problem Statement**:  
Participants placed two bids to buy **Flippers** from Sea Turtles, with reserve prices uniformly distributed (160–200, 250–320 SeaShells, excluding 200–250). The second bid needed to exceed the average of all second bids, or profits were scaled by a probability factor. Flippers could be sold for 320 SeaShells each.

**Solution**:  
The manual strategy optimized bids to balance cost and acceptance probability. For the first bid, a value around 200 maximized acceptance in the lower range. For the second bid, a value slightly above the expected average (e.g., 270–280) ensured high acceptance while minimizing cost. 

### Round 4: Sunlight-Driven Macarons
**Problem Statement**:  
**Magnificent Macarons** were introduced (position limit: 75, conversion limit: 10). Prices depended on sunlight index, sugar prices, transport fees, and tariffs. A hint suggested a **Critical Sunlight Index (CSI)** below which Macaron prices increased significantly.

**Solution**:  
The algorithm implemented a sunlight-index-adjusted trading strategy:  
- **Magnificent Macarons**: Calculated fair value as the mid-price of bid/ask quotes from Pristine Cuisine. If the sunlight index fell below the CSI (initially 45, dynamically updated), fair value was adjusted upward (1.1x for buying, 0.9x for selling).  
- **Trading Logic**: Bought when market ask prices were below the adjusted fair value or Pristine Cuisine’s ask price (with fees). Sold when market bid prices exceeded the adjusted fair value or Pristine Cuisine’s bid price (with fees).  
- **Conversions**: Executed conversions to unwind positions when market prices were favorable compared to Pristine Cuisine’s quotes, respecting the conversion limit.  
- **CSI Update**: Dynamically adjusted the CSI based on recent trade data, increasing it when fair values consistently exceeded sugar prices by 10%.  
The algorithm also accounted for storage costs (0.1 SeaShells per unit per timestamp for long positions).

### Manual Challenge
**Problem Statement**:  
Participants chose up to three suitcases with prizes (base treasure: 10,000 SeaShells, multiplier up to 100). The first suitcase was free, but the second and third cost SeaShells. Profits were divided by inhabitants and selection percentage, similar to Round 2.

**Solution**:  
The manual strategy used Round 2’s player choice distribution to select suitcases with high multipliers and low expected competition. The algorithm’s risk-averse trading approach aligned with this strategy, focusing on high-probability outcomes.

### Round 5: Final Optimization
- Counterparty analysis integration
- Cross-product correlation hedging
- Transaction cost-aware execution

  **Problem Statement**:  
No new products were introduced, but the exchange disclosed counterparties for trades (`counter_party` in `OwnTrade`). The challenge was to leverage this information to enhance profitability.

**Solution**:  
- **All Products**: Maintained existing strategies (e.g., mean-reversion for Kelp, Picnic Basket2, Jams; percentile-based for Volcanic Rock/Vouchers; sunlight-adjusted for Macarons).  
- **Optimization**: Fine-tuned parameters (e.g., order sizes, thresholds) to maximize profitability while respecting position limits.  
The lack of counterparty utilization suggests the algorithm prioritized robust, generalizable strategies over counterparty-specific tactics.

### Manual Challenge
**Problem Statement**:  
Participants traded foreign goods on the West Archipelago exchange for one day, using news from “Goldberg.” Trading costs increased with volume.

**Solution**:  
The manual strategy involved analyzing Goldberg’s news to predict price movements and trading optimally to balance volume and cost. The algorithm’s focus on fair value and market-making aligned with this, ensuring trades were placed at advantageous prices.


## 🏗️ Code Architecture

```mermaid
graph TD
    A[Market Data] --> B{Strategy Router}
    B --> C[Mean Reversion Engine]
    B --> D[Statistical Arbitrage]
    B --> E[Volatility Trader]
    C --> F[Kelp/Djembes]
    D --> G[Picnic Baskets]
    E --> H[Volcanic Derivatives]
```
---

**Crafted with ❤️ by Dharmraj Dhaker**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](www.linkedin.com/in/dharmraj-dhaker-a436b4250)
```

