from datamodel import OrderDepth, TradingState, Order
from typing import Dict, List
import jsonpickle
import numpy as np
from statistics import mean
import uuid

class Product:
    DJEMBES = "DJEMBES"
    PICNIC_BASKET1 = "PICNIC_BASKET1"
    KELP = "KELP"
    CROISSANTS = "CROISSANTS"
    PICNIC_BASKET2 = "PICNIC_BASKET2"
    JAMS = "JAMS"
    RAINFOREST_RESIN = "RAINFOREST_RESIN"
    MAGNIFICENT_MACARONS = "MAGNIFICENT_MACARONS"
    VOLCANIC_ROCK = "VOLCANIC_ROCK"
    VOLCANIC_ROCK_VOUCHER_9500 = "VOLCANIC_ROCK_VOUCHER_9500"
    VOLCANIC_ROCK_VOUCHER_9750 = "VOLCANIC_ROCK_VOUCHER_9750"
    VOLCANIC_ROCK_VOUCHER_10000 = "VOLCANIC_ROCK_VOUCHER_10000"
    VOLCANIC_ROCK_VOUCHER_10250 = "VOLCANIC_ROCK_VOUCHER_10250"
    VOLCANIC_ROCK_VOUCHER_10500 = "VOLCANIC_ROCK_VOUCHER_10500"

PARAMS = {
    Product.DJEMBES: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 10,
        "disregard_edge": 1,
        "join_edge": 0,
        "default_edge": 1,
        "rolling_window": 200
    },
    Product.PICNIC_BASKET1: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 10,
        "disregard_edge": 1,
        "join_edge": 0,
        "default_edge": 1,
        "rolling_window": 200
    },
    Product.KELP: {
        "take_width": 1,
        "clear_width": 0,
        "prevent_adverse": True,
        "adverse_volume": 15,
        "reversion_beta": -0.229,
        "disregard_edge": 1,
        "join_edge": 0,
        "default_edge": 1,
    },
    Product.CROISSANTS: {
        "spread": 1,
        "order_size": 20,
        "vwap_window": 100,
        "buy_threshold": 0.995,
        "sell_threshold": 1.005,
    },
    Product.PICNIC_BASKET2: {
        "vwap_window": 10,
        "sma_window": 10,
        "volatility_threshold": 70,
        "flat_market_threshold": 10,
        "z_threshold": 1.5,
        "trend_tolerance": 0.01,
        "profit_target": 0.01,
        "order_size": 30,
        "market_making_spread": 0.5,
    },
    Product.JAMS: {
        "vwap_window": 10,
        "sma_window": 10,
        "volatility_threshold": 70,
        "flat_market_threshold": 10,
        "z_threshold": 1.5,
        "trend_tolerance": 0.01,
        "profit_target": 0.01,
        "order_size": 50,
        "market_making_spread": 0.5,
    },
    Product.RAINFOREST_RESIN: {
        "fair_value": 10000,
        "take_width": 1,
        "clear_width": 0,
        "disregard_edge": 1,
        "join_edge": 2,
        "default_edge": 4,
        "soft_position_limit": 30,
    },
    Product.MAGNIFICENT_MACARONS: {
        "conversion_limit": 10,
        "storage_cost": 0.1,
        "csi_threshold": 45
    },
    Product.VOLCANIC_ROCK: {
        "window": 2000,
        "limit": 200
    },
    Product.VOLCANIC_ROCK_VOUCHER_9500: {
        "window": 2000,
        "limit": 200
    },
    Product.VOLCANIC_ROCK_VOUCHER_9750: {
        "window": 2000,
        "limit": 200
    },
    Product.VOLCANIC_ROCK_VOUCHER_10000: {
        "window": 2000,
        "limit": 200
    },
    Product.VOLCANIC_ROCK_VOUCHER_10250: {
        "window": 2000,
        "limit": 200
    },
    Product.VOLCANIC_ROCK_VOUCHER_10500: {
        "window": 2000,
        "limit": 200
    }
}

class Trader:
    def __init__(self, params=None):
        if params is None:
            params = PARAMS
        self.params = params
        self.LIMIT = {
            Product.DJEMBES: 60,
            Product.PICNIC_BASKET1: 60,
            Product.KELP: 50,
            Product.CROISSANTS: 250,
            Product.PICNIC_BASKET2: 100,
            Product.JAMS: 350,
            Product.RAINFOREST_RESIN: 50,
            Product.MAGNIFICENT_MACARONS: 75,
            Product.VOLCANIC_ROCK: 400,
            Product.VOLCANIC_ROCK_VOUCHER_9500: 200,
            Product.VOLCANIC_ROCK_VOUCHER_9750: 200,
            Product.VOLCANIC_ROCK_VOUCHER_10000: 200,
            Product.VOLCANIC_ROCK_VOUCHER_10250: 200,
            Product.VOLCANIC_ROCK_VOUCHER_10500: 200
        }
        self.state_data = {
            Product.PICNIC_BASKET2: {"vwap_prices": [], "sma_values": [], "entry_vwap": None, "position": 0},
            Product.JAMS: {"vwap_prices": [], "sma_values": [], "entry_vwap": None, "position": 0},
            Product.VOLCANIC_ROCK: {"trade_history": []},
            Product.VOLCANIC_ROCK_VOUCHER_9500: {"trade_history": []},
            Product.VOLCANIC_ROCK_VOUCHER_9750: {"trade_history": []},
            Product.VOLCANIC_ROCK_VOUCHER_10000: {"trade_history": []},
            Product.VOLCANIC_ROCK_VOUCHER_10250: {"trade_history": []},
            Product.VOLCANIC_ROCK_VOUCHER_10500: {"trade_history": []}
        }
        self.position = {
            Product.VOLCANIC_ROCK: 0,
            Product.VOLCANIC_ROCK_VOUCHER_9500: 0,
            Product.VOLCANIC_ROCK_VOUCHER_9750: 0,
            Product.VOLCANIC_ROCK_VOUCHER_10000: 0,
            Product.VOLCANIC_ROCK_VOUCHER_10250: 0,
            Product.VOLCANIC_ROCK_VOUCHER_10500: 0
        }

    def update_state(self, product: str, mid_price: float):
        self.state_data[product]["trade_history"].append(mid_price)
        window = self.params[product]["window"]
        if len(self.state_data[product]["trade_history"]) > window:
            self.state_data[product]["trade_history"].pop(0)
        if len(self.state_data[product]["trade_history"]) >= window:
            p50 = np.quantile(self.state_data[product]["trade_history"], 0.50)
            p75 = np.quantile(self.state_data[product]["trade_history"], 0.75)
        else:
            p50 = p75 = mid_price or 0
        prev_mid = self.state_data[product]["trade_history"][-2] if len(self.state_data[product]["trade_history"]) > 1 else mid_price
        return mid_price, prev_mid, p50, p75

    def take_best_orders(self, product: str, fair_value: float, take_width: float, orders: List[Order],
                        order_depth: OrderDepth, position: int, buy_order_volume: int, sell_order_volume: int,
                        prevent_adverse: bool = False, adverse_volume: int = 0) -> tuple[int, int]:
        position_limit = self.LIMIT[product]
        if len(order_depth.sell_orders) != 0:
            best_ask = min(order_depth.sell_orders.keys())
            best_ask_amount = -order_depth.sell_orders[best_ask]
            if not prevent_adverse or abs(best_ask_amount) <= adverse_volume:
                if best_ask <= fair_value - take_width:
                    quantity = min(best_ask_amount, position_limit - position)
                    if quantity > 0:
                        orders.append(Order(product, best_ask, quantity))
                        buy_order_volume += quantity
                        order_depth.sell_orders[best_ask] += quantity
                        if order_depth.sell_orders[best_ask] == 0:
                            del order_depth.sell_orders[best_ask]
        if len(order_depth.buy_orders) != 0:
            best_bid = max(order_depth.buy_orders.keys())
            best_bid_amount = order_depth.buy_orders[best_bid]
            if not prevent_adverse or abs(best_bid_amount) <= adverse_volume:
                if best_bid >= fair_value + take_width:
                    quantity = min(best_bid_amount, position_limit + position)
                    if quantity > 0:
                        orders.append(Order(product, best_bid, -quantity))
                        sell_order_volume += quantity
                        order_depth.buy_orders[best_bid] -= quantity
                        if order_depth.buy_orders[best_bid] == 0:
                            del order_depth.buy_orders[best_bid]
        return buy_order_volume, sell_order_volume

    def market_make(self, product: str, orders: List[Order], bid: int, ask: int,
                    position: int, buy_order_volume: int, sell_order_volume: int) -> tuple[int, int]:
        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        if buy_quantity > 0:
            orders.append(Order(product, round(bid), buy_quantity))
        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)
        if sell_quantity > 0:
            orders.append(Order(product, round(ask), -sell_quantity))
        return buy_order_volume, sell_order_volume

    def clear_position_order(self, product: str, fair_value: float, width: int, orders: List[Order],
                            order_depth: OrderDepth, position: int, buy_order_volume: int, sell_order_volume: int) -> tuple[int, int]:
        position_after_take = position + buy_order_volume - sell_order_volume
        fair_for_bid = round(fair_value - width)
        fair_for_ask = round(fair_value + width)
        buy_quantity = self.LIMIT[product] - (position + buy_order_volume)
        sell_quantity = self.LIMIT[product] + (position - sell_order_volume)
        if position_after_take > 0:
            clear_quantity = sum(volume for price, volume in order_depth.buy_orders.items() if price >= fair_for_ask)
            clear_quantity = min(clear_quantity, position_after_take)
            sent_quantity = min(sell_quantity, clear_quantity)
            if sent_quantity > 0:
                orders.append(Order(product, fair_for_ask, -abs(sent_quantity)))
                sell_order_volume += abs(sent_quantity)
        if position_after_take < 0:
            clear_quantity = sum(abs(volume) for price, volume in order_depth.sell_orders.items() if price <= fair_for_bid)
            clear_quantity = min(clear_quantity, abs(position_after_take))
            sent_quantity = min(buy_quantity, clear_quantity)
            if sent_quantity > 0:
                orders.append(Order(product, fair_for_bid, abs(sent_quantity)))
                buy_order_volume += abs(sent_quantity)
        return buy_order_volume, sell_order_volume

    def take_orders(self, product: str, order_depth: OrderDepth, fair_value: float, take_width: float,
                    position: int, prevent_adverse: bool = False, adverse_volume: int = 0) -> tuple[List[Order], int, int]:
        orders: List[Order] = []
        buy_order_volume = 0
        sell_order_volume = 0
        buy_order_volume, sell_order_volume = self.take_best_orders(
            product, fair_value, take_width, orders, order_depth, position,
            buy_order_volume, sell_order_volume, prevent_adverse, adverse_volume
        )
        return orders, buy_order_volume, sell_order_volume

    def clear_orders(self, product: str, order_depth: OrderDepth, fair_value: float, clear_width: int,
                     position: int, buy_order_volume: int, sell_order_volume: int) -> tuple[List[Order], int, int]:
        orders: List[Order] = []
        buy_order_volume, sell_order_volume = self.clear_position_order(
            product, fair_value, clear_width, orders, order_depth, position,
            buy_order_volume, sell_order_volume
        )
        return orders, buy_order_volume, sell_order_volume

    def make_orders(self, product: str, order_depth: OrderDepth, fair_value: float, position: int,
                    buy_order_volume: int, sell_order_volume: int, disregard_edge: float,
                    join_edge: float, default_edge: float, manage_position: bool = False,
                    soft_position_limit: int = 0) -> tuple[List[Order], int, int]:
        orders: List[Order] = []
        asks_above_fair = [price for price in order_depth.sell_orders.keys() if price > fair_value + disregard_edge]
        bids_below_fair = [price for price in order_depth.buy_orders.keys() if price < fair_value - disregard_edge]
        best_ask_above_fair = min(asks_above_fair) if asks_above_fair else None
        best_bid_below_fair = max(bids_below_fair) if bids_below_fair else None
        ask = round(fair_value + default_edge)
        if best_ask_above_fair is not None:
            if abs(best_ask_above_fair - fair_value) <= join_edge:
                ask = best_ask_above_fair
            else:
                ask = best_ask_above_fair - 1
        bid = round(fair_value - default_edge)
        if best_bid_below_fair is not None:
            if abs(fair_value - best_bid_below_fair) <= join_edge:
                bid = best_bid_below_fair
            else:
                bid = best_bid_below_fair + 1
        if manage_position:
            if position > soft_position_limit:
                ask -= 1
            elif position < -soft_position_limit:
                bid += 1
        buy_order_volume, sell_order_volume = self.market_make(
            product, orders, bid, ask, position, buy_order_volume, sell_order_volume
        )
        return orders, buy_order_volume, sell_order_volume

    def djembe_fair_value(self, order_depth: OrderDepth, trader_object: Dict) -> float:
        if order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [price for price in order_depth.sell_orders.keys() if abs(order_depth.sell_orders[price]) >= self.params[Product.DJEMBES]["adverse_volume"]]
            filtered_bid = [price for price in order_depth.buy_orders.keys() if abs(order_depth.buy_orders[price]) >= self.params[Product.DJEMBES]["adverse_volume"]]
            mm_ask = min(filtered_ask) if filtered_ask else None
            mm_bid = max(filtered_bid) if filtered_bid else None
            if mm_ask is None or mm_bid is None:
                if trader_object.get("DJEMBES_last_price") is None:
                    mid_price = (best_ask + best_bid) / 2
                else:
                    mid_price = trader_object["DJEMBES_last_price"]
            else:
                mid_price = (mm_ask + mm_bid) / 2
            log_Pt = np.log(mid_price)
            trader_object.setdefault("DJEMBES_log_price_history", []).append(log_Pt)
            price_history = trader_object["DJEMBES_log_price_history"]
            if len(price_history) > self.params[Product.DJEMBES]["rolling_window"]:
                price_history = price_history[-self.params[Product.DJEMBES]["rolling_window"]:]
            trader_object["DJEMBES_log_price_history"] = price_history
            mu = np.mean(price_history)
            theta = 0.005
            log_Pt1 = log_Pt + theta * (mu - log_Pt)
            fair = np.exp(log_Pt1)
            trader_object["DJEMBES_last_price"] = mid_price
            return fair
        return None

    def picnic_basket1_fair_value(self, order_depth: OrderDepth, trader_object: Dict) -> float:
        if order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [price for price in order_depth.sell_orders.keys() if abs(order_depth.sell_orders[price]) >= self.params[Product.PICNIC_BASKET1]["adverse_volume"]]
            filtered_bid = [price for price in order_depth.buy_orders.keys() if abs(order_depth.buy_orders[price]) >= self.params[Product.PICNIC_BASKET1]["adverse_volume"]]
            mm_ask = min(filtered_ask) if filtered_ask else None
            mm_bid = max(filtered_bid) if filtered_bid else None
            if mm_ask is None or mm_bid is None:
                if trader_object.get("PICNIC_BASKET1_last_price") is None:
                    mid_price = (best_ask + best_bid) / 2
                else:
                    mid_price = trader_object["PICNIC_BASKET1_last_price"]
            else:
                mid_price = (mm_ask + mm_bid) / 2
            log_Pt = np.log(mid_price)
            trader_object.setdefault("PICNIC_BASKET1_log_price_history", []).append(log_Pt)
            price_history = trader_object["PICNIC_BASKET1_log_price_history"]
            if len(price_history) > self.params[Product.PICNIC_BASKET1]["rolling_window"]:
                price_history = price_history[-self.params[Product.PICNIC_BASKET1]["rolling_window"]:]
            trader_object["PICNIC_BASKET1_log_price_history"] = price_history
            mu = np.mean(price_history)
            theta = 0.02
            log_Pt1 = log_Pt + theta * (mu - log_Pt)
            fair = np.exp(log_Pt1)
            trader_object["PICNIC_BASKET1_last_price"] = mid_price
            return fair
        return None

    def kelp_fair_value(self, order_depth: OrderDepth, trader_object: Dict) -> float:
        if order_depth.sell_orders and order_depth.buy_orders:
            best_ask = min(order_depth.sell_orders.keys())
            best_bid = max(order_depth.buy_orders.keys())
            filtered_ask = [price for price in order_depth.sell_orders.keys() if abs(order_depth.sell_orders[price]) >= self.params[Product.KELP]["adverse_volume"]]
            filtered_bid = [price for price in order_depth.buy_orders.keys() if abs(order_depth.buy_orders[price]) >= self.params[Product.KELP]["adverse_volume"]]
            mm_ask = min(filtered_ask) if filtered_ask else None
            mm_bid = max(filtered_bid) if filtered_bid else None
            if mm_ask is None or mm_bid is None:
                if trader_object.get("KELP_last_price") is None:
                    mmmid_price = (best_ask + best_bid) / 2
                else:
                    mmmid_price = trader_object["KELP_last_price"]
            else:
                mmmid_price = (mm_ask + mm_bid) / 2
            if trader_object.get("KELP_last_price") is not None:
                last_price = trader_object["KELP_last_price"]
                last_returns = (mmmid_price - last_price) / last_price
                pred_returns = last_returns * self.params[Product.KELP]["reversion_beta"]
                fair = mmmid_price + (mmmid_price * pred_returns)
            else:
                fair = mmmid_price
            trader_object["KELP_last_price"] = mmmid_price
            return fair
        return None

    def croissants_trading(self, product: str, order_depth: OrderDepth, position: int, trader_data_dict: Dict) -> List[Order]:
        orders: List[Order] = []
        pos_limit = self.LIMIT[product]
        buy_prices = list(order_depth.buy_orders.keys())
        sell_prices = list(order_depth.sell_orders.keys())
        buy_volumes = list(order_depth.buy_orders.values())
        sell_volumes = [-v for v in order_depth.sell_orders.values()]
        fair_value = None
        if buy_prices and sell_prices:
            best_bid = max(buy_prices)
            best_ask = min(sell_prices)
            mid_price = (best_bid + best_ask) / 2
            all_prices = buy_prices + sell_prices
            all_volumes = buy_volumes + sell_volumes
            if all_volumes and sum(all_volumes) != 0:
                vwap = np.average(all_prices, weights=all_volumes)
                fair_value = vwap
            else:
                fair_value = mid_price
        elif buy_prices:
            fair_value = max(buy_prices)
        elif sell_prices:
            fair_value = min(sell_prices)
        if fair_value is None:
            return orders
        trader_data_dict["vwap"].setdefault(product, []).append(fair_value)
        if len(trader_data_dict["vwap"][product]) > self.params[product]["vwap_window"]:
            trader_data_dict["vwap"][product].pop(0)
        if sell_prices:
            best_ask = min(sell_prices)
            best_ask_volume = -order_depth.sell_orders[best_ask]
            if best_ask < fair_value * self.params[product]["buy_threshold"]:
                max_buy_qty = min(best_ask_volume, pos_limit - position)
                if max_buy_qty > 0:
                    orders.append(Order(product, best_ask, max_buy_qty))
        if buy_prices:
            best_bid = max(buy_prices)
            best_bid_volume = order_depth.buy_orders[best_bid]
            if best_bid > fair_value * self.params[product]["sell_threshold"]:
                max_sell_qty = min(best_bid_volume, pos_limit + position)
                if max_sell_qty > 0:
                    orders.append(Order(product, best_bid, -max_sell_qty))
        if position < pos_limit - 10:
            buy_price = int(fair_value - self.params[product]["spread"])
            buy_qty = min(self.params[product]["order_size"], pos_limit - position)
            orders.append(Order(product, buy_price, buy_qty))
        if position > -pos_limit + 10:
            sell_price = int(fair_value + self.params[product]["spread"])
            sell_qty = min(self.params[product]["order_size"], pos_limit + position)
            orders.append(Order(product, sell_price, -sell_qty))
        return orders

    def croissants_conversion(self, product: str, position: int, conv_obs, trader_data_dict: Dict, fair_value: float) -> int:
        conversions = 0
        if position != 0:
            total_cost = conv_obs.transportFees + conv_obs.importTariff + conv_obs.exportTariff
            avg_vwap = mean(trader_data_dict["vwap"].get(product, [fair_value or 0]))
            if position < 0 and conv_obs.bidPrice > avg_vwap + total_cost:
                conv_qty = min(abs(position), 5)
                conversions += conv_qty
        return conversions

    def calculate_vwap(self, order_depth: OrderDepth) -> tuple[float, float, float]:
        bid_prices = sorted(order_depth.buy_orders.keys(), reverse=True)
        ask_prices = sorted(order_depth.sell_orders.keys())
        bid_vwap = 0
        bid_total_volume = 0
        for price in bid_prices:
            volume = order_depth.buy_orders[price]
            bid_vwap += price * volume
            bid_total_volume += volume
        ask_vwap = 0
        ask_total_volume = 0
        for price in ask_prices:
            volume = abs(order_depth.sell_orders[price])
            ask_vwap += price * volume
            ask_total_volume += volume
        bid_vwap = bid_vwap / bid_total_volume if bid_total_volume > 0 else 10000
        ask_vwap = ask_vwap / ask_total_volume if ask_total_volume > 0 else 10000
        vwap_mid = (bid_vwap + ask_vwap) / 2
        return vwap_mid, bid_vwap, ask_vwap

    def update_history(self, product: str, vwap: float):
        self.state_data[product]["vwap_prices"].append(vwap)
        self.state_data[product]["sma_values"].append(vwap)
        if len(self.state_data[product]["vwap_prices"]) > self.params[product]["vwap_window"]:
            self.state_data[product]["vwap_prices"].pop(0)
        if len(self.state_data[product]["sma_values"]) > self.params[product]["sma_window"]:
            self.state_data[product]["sma_values"].pop(0)

    def compute_z_score(self, product: str, prices: List[float], current_vwap: float) -> float:
        if len(prices) < self.params[product]["vwap_window"]:
            return 0.0
        vwap_mean = np.mean(prices)
        vwap_std = np.std(prices)
        return (current_vwap - vwap_mean) / vwap_std if vwap_std > 0 else 0.0

    def compute_sma(self, product: str, prices: List[float]) -> float:
        if len(prices) < self.params[product]["sma_window"]:
            return 0.0
        return np.mean(prices)

    def mean_reversion_trading(self, product: str, vwap_mid: float, vwap_bid: float, vwap_ask: float, position: int, state_position: int) -> List[Order]:
        orders = []
        prices = self.state_data[product]["vwap_prices"]
        sma_prices = self.state_data[product]["sma_values"]
        vwap_std = np.std(prices) if len(prices) >= self.params[product]["vwap_window"] else 0
        z_score = self.compute_z_score(product, prices, vwap_mid)
        sma = self.compute_sma(product, sma_prices)
        order_size = self.params[product]["order_size"]
        if (vwap_std > self.params[product]["volatility_threshold"] or 
            (max(prices[-self.params[product]["vwap_window"]:] or [0]) - 
             min(prices[-self.params[product]["vwap_window"]:] or [0])) < self.params[product]["flat_market_threshold"]):
            return orders
        if sma == 0:
            return orders
        buy_condition = vwap_mid > sma * (1 + self.params[product]["trend_tolerance"])
        sell_condition = vwap_mid < sma * (1 - self.params[product]["trend_tolerance"])
        if z_score > self.params[product]["z_threshold"] and sell_condition and position > -self.LIMIT[product]:
            if self.state_data[product]["entry_vwap"] and vwap_mid <= self.state_data[product]["entry_vwap"] * (1 - self.params[product]["profit_target"]):
                qty = min(order_size, self.LIMIT[product] + position)
                orders.append(Order(product, int(vwap_ask), -qty))
                self.state_data[product]["entry_vwap"] = None
            elif not self.state_data[product]["entry_vwap"]:
                self.state_data[product]["entry_vwap"] = vwap_mid
        elif z_score < -self.params[product]["z_threshold"] and buy_condition and position < self.LIMIT[product]:
            if self.state_data[product]["entry_vwap"] and vwap_mid >= self.state_data[product]["entry_vwap"] * (1 + self.params[product]["profit_target"]):
                qty = min(order_size, self.LIMIT[product] - position)
                orders.append(Order(product, int(vwap_bid), qty))
                self.state_data[product]["entry_vwap"] = None
            elif not self.state_data[product]["entry_vwap"]:
                self.state_data[product]["entry_vwap"] = vwap_mid
        self.state_data[product]["position"] = state_position + sum(o.quantity for o in orders if o.quantity > 0) - sum(-o.quantity for o in orders if o.quantity < 0)
        return orders

    def market_making(self, product: str, vwap_mid: float, position: int) -> List[Order]:
        orders = []
        order_size = self.params[product]["order_size"]
        spread = self.params[product]["market_making_spread"]
        if position < self.LIMIT[product]:
            qty = min(order_size, self.LIMIT[product] - position)
            orders.append(Order(product, int(vwap_mid - spread), qty))
        if position > -self.LIMIT[product]:
            qty = min(order_size, self.LIMIT[product] + position)
            orders.append(Order(product, int(vwap_mid + spread), -qty))
        return orders

    def magnificent_macarons_trading(self, product: str, order_depth: OrderDepth, position: int, trader_data: Dict, state: TradingState) -> List[Order]:
        orders = []
        max_buy_qty = self.LIMIT[product] - position
        max_sell_qty = self.LIMIT[product] + position

        conv_obs = state.observations.conversionObservations.get(product)
        sunlight_index = conv_obs.sunlightIndex if conv_obs else 45
        bid_price = conv_obs.bidPrice if conv_obs else 0
        ask_price = conv_obs.askPrice if conv_obs else float('inf')
        transport_fees = conv_obs.transportFees if conv_obs else 0
        import_tariff = conv_obs.importTariff if conv_obs else 0
        export_tariff = conv_obs.exportTariff if conv_obs else 0
        sugar_price = conv_obs.sugarPrice if conv_obs else 0

        fair_value = (bid_price + ask_price) / 2 if bid_price and ask_price else 10000
        if sunlight_index < trader_data["csi"]:
            fair_value *= 1.1

        fair_value1 = (bid_price + ask_price) / 2 if bid_price and ask_price else 10000
        if sunlight_index < trader_data["csi"]:
            fair_value1 *= 0.9

        fair_value2 = (bid_price + ask_price) / 2 if bid_price and ask_price else 10000
        if sunlight_index < trader_data["csi"]:
            fair_value2 *= 0.9

        if order_depth.sell_orders:
            best_ask, best_ask_qty = min(order_depth.sell_orders.items())
            if best_ask < min(fair_value1, (ask_price + transport_fees + import_tariff) * 0.9):
                qty = min(-best_ask_qty, max_buy_qty)
                if qty > 0:
                    orders.append(Order(product, best_ask, qty))
                    print(f"BUY {product}, {qty}x{best_ask}")

        if order_depth.buy_orders:
            best_bid, best_bid_qty = max(order_depth.buy_orders.items())
            if best_bid > max(fair_value2, -bid_price - transport_fees - export_tariff):
                qty = min(best_bid_qty, max_sell_qty)
                if qty > 0:
                    orders.append(Order(product, best_bid, -qty))
                    print(f"SELL {product}, {qty}x{best_bid}")

        trader_data["trade_history"].append({
            "timestamp": state.timestamp,
            "position": position,
            "sunlight_index": sunlight_index,
            "fair_value": fair_value,
            "fair_value1": fair_value1,
            "fair_value2": fair_value2,
            "sugar_price": sugar_price
        })

        if len(trader_data["trade_history"]) > 10:
            recent_trades = trader_data["trade_history"][-10:]
            average_sugar_price = np.mean([t["sugar_price"] for t in recent_trades])
            if any(t["fair_value"] > average_sugar_price * 1.1 for t in recent_trades):
                trader_data["csi"] = np.mean([t["sunlight_index"] for t in recent_trades])

        return orders

    def magnificent_macarons_conversion(self, product: str, position: int, conv_obs, order_depth: OrderDepth) -> int:
        conversions = 0
        if position > 0 and conv_obs and max(order_depth.buy_orders.items())[0] < conv_obs.bidPrice - conv_obs.transportFees - conv_obs.exportTariff:
            conversions = min(position, self.params[product]["conversion_limit"])
        elif position < 0 and conv_obs and min(order_depth.sell_orders.items())[0] > conv_obs.askPrice + conv_obs.transportFees - conv_obs.importTariff:
            conversions = min(-position, self.params[product]["conversion_limit"])
        return conversions

    def volcanic_rock_trading(self, product: str, order_depth: OrderDepth, position: int, current_mid: float, prev_mid: float, p50: float, p75: float) -> List[Order]:
        orders = []
        limit = self.LIMIT[product] - abs(position)
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else 0
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else float('inf')

        # SHORT ENTRY: cross below 75th percentile from above
        if (position == 0 and prev_mid > p75 and current_mid <= p75 and limit > 0 and 
            order_depth.sell_orders):
            qty = min(limit, -order_depth.sell_orders.get(best_ask, 1))
            if qty > 0:
                orders.append(Order(product, best_bid, -qty))  # Sell at bid
                self.position[product] -= qty
                print(f"Shorting {product} at {best_bid} (bid), qty {qty}")

        # SHORT EXIT: cross below 50th percentile
        elif position < 0 and prev_mid >= p50 and current_mid < p50 and order_depth.buy_orders:
            qty = min(abs(position), order_depth.buy_orders.get(best_bid, 1))
            if qty > 0:
                orders.append(Order(product, best_ask, qty))  # Buy back at ask
                self.position[product] += qty
                if self.position[product] == 0:
                    print(f"Squaring off {product} at {best_ask} (ask) - 50th Cross, qty {qty}")
                else:
                    print(f"Partially squaring off {product} at {best_ask} (ask), qty {qty}")

        # LONG ENTRY: cross above 50th percentile from below
        elif (position == 0 and prev_mid < p50 and current_mid >= p50 and limit > 0 and 
              order_depth.buy_orders):
            qty = min(limit, order_depth.buy_orders.get(best_bid, 1))
            if qty > 0:
                orders.append(Order(product, best_ask, qty))  # Buy at ask
                self.position[product] += qty
                print(f"Going long {product} at {best_ask} (ask), qty {qty}")

        # LONG EXIT: cross above 75th percentile
        elif position > 0 and prev_mid <= p75 and current_mid > p75 and order_depth.sell_orders:
            qty = min(position, -order_depth.sell_orders.get(best_ask, 1))
            if qty > 0:
                orders.append(Order(product, best_bid, -qty))  # Sell at bid
                self.position[product] -= qty
                if self.position[product] == 0:
                    print(f"Squaring off {product} at {best_bid} (bid) - 75th Cross, qty {qty}")
                else:
                    print(f"Partially squaring off {product} at {best_bid} (bid), qty {qty}")

        return orders

    def run(self, state: TradingState) -> tuple[Dict[str, List[Order]], int, str]:
        result = {}
        conversions = 0
        trader_object = {}
        trader_data_dict = {"vwap": {}, "trade_counts": {}}
        trader_data = {"csi": self.params[Product.MAGNIFICENT_MACARONS]["csi_threshold"], "trade_history": []}

        if state.traderData:
            try:
                decoded = jsonpickle.decode(state.traderData)
                if "trader_object" in decoded:
                    trader_object = decoded["trader_object"]
                    trader_data_dict = decoded["trader_data_dict"]
                    self.state_data.update(decoded.get("state_data", {}))
                    trader_data = decoded.get("trader_data", {"csi": self.params[Product.MAGNIFICENT_MACARONS]["csi_threshold"], "trade_history": []})
                elif "vwap" in decoded:
                    trader_data_dict = decoded
                else:
                    trader_object = decoded
            except:
                pass

        # DJEMBES trading
        if Product.DJEMBES in state.order_depths:
            position = state.position.get(Product.DJEMBES, 0)
            fair_value = self.djembe_fair_value(state.order_depths[Product.DJEMBES], trader_object)
            if fair_value is not None:
                take_orders, buy_volume, sell_volume = self.take_orders(
                    Product.DJEMBES, state.order_depths[Product.DJEMBES], fair_value,
                    self.params[Product.DJEMBES]["take_width"], position,
                    self.params[Product.DJEMBES]["prevent_adverse"], self.params[Product.DJEMBES]["adverse_volume"]
                )
                clear_orders, buy_volume, sell_volume = self.clear_orders(
                    Product.DJEMBES, state.order_depths[Product.DJEMBES], fair_value,
                    self.params[Product.DJEMBES]["clear_width"], position, buy_volume, sell_volume
                )
                make_orders, _, _ = self.make_orders(
                    Product.DJEMBES, state.order_depths[Product.DJEMBES], fair_value, position,
                    buy_volume, sell_volume, self.params[Product.DJEMBES]["disregard_edge"],
                    self.params[Product.DJEMBES]["join_edge"], self.params[Product.DJEMBES]["default_edge"]
                )
                result[Product.DJEMBES] = take_orders + clear_orders + make_orders
                conversions = max(conversions, 1)

        # PICNIC_BASKET1 trading
        if Product.PICNIC_BASKET1 in state.order_depths:
            position = state.position.get(Product.PICNIC_BASKET1, 0)
            fair_value = self.picnic_basket1_fair_value(state.order_depths[Product.PICNIC_BASKET1], trader_object)
            if fair_value is not None:
                take_orders, buy_volume, sell_volume = self.take_orders(
                    Product.PICNIC_BASKET1, state.order_depths[Product.PICNIC_BASKET1], fair_value,
                    self.params[Product.PICNIC_BASKET1]["take_width"], position,
                    self.params[Product.PICNIC_BASKET1]["prevent_adverse"], self.params[Product.PICNIC_BASKET1]["adverse_volume"]
                )
                clear_orders, buy_volume, sell_volume = self.clear_orders(
                    Product.PICNIC_BASKET1, state.order_depths[Product.PICNIC_BASKET1], fair_value,
                    self.params[Product.PICNIC_BASKET1]["clear_width"], position, buy_volume, sell_volume
                )
                make_orders, _, _ = self.make_orders(
                    Product.PICNIC_BASKET1, state.order_depths[Product.PICNIC_BASKET1], fair_value, position,
                    buy_volume, sell_volume, self.params[Product.PICNIC_BASKET1]["disregard_edge"],
                    self.params[Product.PICNIC_BASKET1]["join_edge"], self.params[Product.PICNIC_BASKET1]["default_edge"]
                )
                result[Product.PICNIC_BASKET1] = take_orders + clear_orders + make_orders
                conversions = max(conversions, 1)

        # KELP trading
        if Product.KELP in state.order_depths:
            position = state.position.get(Product.KELP, 0)
            fair_value = self.kelp_fair_value(state.order_depths[Product.KELP], trader_object)
            if fair_value is not None:
                take_orders, buy_volume, sell_volume = self.take_orders(
                    Product.KELP, state.order_depths[Product.KELP], fair_value,
                    self.params[Product.KELP]["take_width"], position,
                    self.params[Product.KELP]["prevent_adverse"], self.params[Product.KELP]["adverse_volume"]
                )
                clear_orders, buy_volume, sell_volume = self.clear_orders(
                    Product.KELP, state.order_depths[Product.KELP], fair_value,
                    self.params[Product.KELP]["clear_width"], position, buy_volume, sell_volume
                )
                make_orders, _, _ = self.make_orders(
                    Product.KELP, state.order_depths[Product.KELP], fair_value, position,
                    buy_volume, sell_volume, self.params[Product.KELP]["disregard_edge"],
                    self.params[Product.KELP]["join_edge"], self.params[Product.KELP]["default_edge"]
                )
                result[Product.KELP] = take_orders + clear_orders + make_orders
                conversions = max(conversions, 1)

        # CROISSANTS trading
        if Product.CROISSANTS in state.order_depths:
            position = state.position.get(Product.CROISSANTS, 0)
            orders = self.croissants_trading(Product.CROISSANTS, state.order_depths[Product.CROISSANTS], position, trader_data_dict)
            result[Product.CROISSANTS] = orders
            if Product.CROISSANTS in state.observations.conversionObservations:
                fair_value = mean(trader_data_dict["vwap"].get(Product.CROISSANTS, [0]))
                conversions += self.croissants_conversion(
                    Product.CROISSANTS, position, state.observations.conversionObservations[Product.CROISSANTS],
                    trader_data_dict, fair_value
                )

        # PICNIC_BASKET2 and JAMS trading
        for product in [Product.PICNIC_BASKET2, Product.JAMS]:
            if product in state.order_depths:
                order_depth = state.order_depths[product]
                vwap_mid, vwap_bid, vwap_ask = self.calculate_vwap(order_depth)
                self.update_history(product, vwap_mid)
                position = state.position.get(product, 0)
                orders = self.mean_reversion_trading(product, vwap_mid, vwap_bid, vwap_ask, position, position)
                if not orders and np.std(self.state_data[product]["vwap_prices"]) < self.params[product]["volatility_threshold"]:
                    orders = self.market_making(product, vwap_mid, position)
                result[product] = orders
                conversions = max(conversions, 1)

        # RAINFOREST_RESIN trading
        if Product.RAINFOREST_RESIN in state.order_depths:
            position = state.position.get(Product.RAINFOREST_RESIN, 0)
            fair_value = self.params[Product.RAINFOREST_RESIN]["fair_value"]
            take_orders, buy_volume, sell_volume = self.take_orders(
                Product.RAINFOREST_RESIN, state.order_depths[Product.RAINFOREST_RESIN], fair_value,
                self.params[Product.RAINFOREST_RESIN]["take_width"], position
            )
            clear_orders, buy_volume, sell_volume = self.clear_orders(
                Product.RAINFOREST_RESIN, state.order_depths[Product.RAINFOREST_RESIN], fair_value,
                self.params[Product.RAINFOREST_RESIN]["clear_width"], position, buy_volume, sell_volume
            )
            make_orders, _, _ = self.make_orders(
                Product.RAINFOREST_RESIN, state.order_depths[Product.RAINFOREST_RESIN], fair_value, position,
                buy_volume, sell_volume, self.params[Product.RAINFOREST_RESIN]["disregard_edge"],
                self.params[Product.RAINFOREST_RESIN]["join_edge"], self.params[Product.RAINFOREST_RESIN]["default_edge"],
                True, self.params[Product.RAINFOREST_RESIN]["soft_position_limit"]
            )
            result[Product.RAINFOREST_RESIN] = take_orders + clear_orders + make_orders
            conversions = max(conversions, 1)

        # MAGNIFICENT_MACARONS trading
        if Product.MAGNIFICENT_MACARONS in state.order_depths:
            position = state.position.get(Product.MAGNIFICENT_MACARONS, 0)
            orders = self.magnificent_macarons_trading(Product.MAGNIFICENT_MACARONS, state.order_depths[Product.MAGNIFICENT_MACARONS], position, trader_data, state)
            result[Product.MAGNIFICENT_MACARONS] = orders
            if Product.MAGNIFICENT_MACARONS in state.observations.conversionObservations:
                conversions += self.magnificent_macarons_conversion(
                    Product.MAGNIFICENT_MACARONS, position, state.observations.conversionObservations[Product.MAGNIFICENT_MACARONS], state.order_depths[Product.MAGNIFICENT_MACARONS]
                )

        # VOLCANIC_ROCK and VOUCHERS trading
        volcanic_products = [
            Product.VOLCANIC_ROCK,
            Product.VOLCANIC_ROCK_VOUCHER_9500,
            Product.VOLCANIC_ROCK_VOUCHER_9750,
            Product.VOLCANIC_ROCK_VOUCHER_10000,
            Product.VOLCANIC_ROCK_VOUCHER_10250,
            Product.VOLCANIC_ROCK_VOUCHER_10500
        ]
        for product in volcanic_products:
            if product in state.order_depths:
                order_depth = state.order_depths[product]
                mid_price = None
                if order_depth.sell_orders and order_depth.buy_orders:
                    mid_price = (min(order_depth.sell_orders.keys()) + max(order_depth.buy_orders.keys())) / 2
                elif order_depth.sell_orders:
                    mid_price = min(order_depth.sell_orders.keys())
                elif order_depth.buy_orders:
                    mid_price = max(order_depth.buy_orders.keys())
                if mid_price:
                    current_mid, prev_mid, p50, p75 = self.update_state(product, mid_price)
                    position = state.position.get(product, 0)
                    orders = self.volcanic_rock_trading(product, order_depth, position, current_mid, prev_mid, p50, p75)
                    result[product] = orders
                    conversions = max(conversions, 1)

        trader_data_encoded = ""
        return result, conversions, trader_data_encoded