import os
import logging
import requests
import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import ta

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def analizar_btc():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCEUR&interval=1m&limit=100"
    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close",
        "volume", "close_time", "quote_asset_volume",
        "number_of_trades", "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume", "ignore"
    ])
    df["close"] = df["close"].astype(float)

    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
    macd = ta.trend.MACD(close=df["close"])
    df["macd"] = macd.macd_diff()

    rsi = df["rsi"].iloc[-1]
    macd_val = df["macd"].iloc[-1]
    current_price = df["close"].iloc[-1]

    if rsi > 70 and macd_val < 0:
        return f"🔻 Posible bajada\n💶 Precio actual: €{current_price:.2f}\n📊 RSI: {rsi:.2f} | MACD: {macd_val:.4f}"
    elif rsi < 30 and macd_val > 0:
        return f"📈 Posible subida\n💶 Precio actual: €{current_price:.2f}\n📊 RSI: {rsi:.2f} | MACD: {macd_val:.4f}"
    else:
        return f"📉 Mercado neutro o dudoso\n💶 Precio actual: €{current_price:.2f}\n📊 RSI: {rsi:.2f} | MACD: {macd_val:.4f}"

def analiza(update: Update, context: CallbackContext) -> None:
    analisis = analizar_btc()
    context.bot.send_message(chat_id=CHAT_ID, text=analisis)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("analiza", analiza))
    updater.start_polling()
    print("Bot arrancado y corriendo...")
    updater.idle()

if __name__ == "__main__":
    main()
