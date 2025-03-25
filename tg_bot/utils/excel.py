import os
import pandas as pd


async def save_payment_to_excel(client, payment_id, amount, status, description, file_name="payments.xlsx"):
    payment_data = {
        "Клиент": client.name,
        "Telegram ID": client.telegram_id,
        "ID платежа": payment_id,
        "Сумма": float(amount),
        "Статус": status,
        "Описание": description,
    }

    if os.path.exists(file_name):
        df = pd.read_excel(file_name, engine="openpyxl")
        df = df.append(payment_data, ignore_index=True)
    else:
        df = pd.DataFrame([payment_data])

    df.to_excel(file_name, index=False, engine="openpyxl")
