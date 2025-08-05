from telegram import Update, LabeledPrice, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, PreCheckoutQueryHandler

# Токены ботов
MAIN_BOT_TOKEN = '8136591859:AAF1AVKOkfPEp8omgRfev_O6G92iuSUEfIk'  # Токен для основного бота
SECOND_BOT_TOKEN = '6537497957:AAHnaAc1x5qesBdNxOU9gQI27JdHvJ8IOMk'  # Токен для второго бота


# Обработчик команды /start
async def start(update: Update, context: CallbackContext):
    query = context.args
    if query:
        try:
            # Разбираем параметры из строки "X_Y"
            part1, part2 = query[0].split('_')
            part1 = int(part1)  # Номер премиума или количество токенов
            part2 = int(part2)  # Количество звезд, которое нужно заплатить

            if part1 == 1 or part1 == 2:  # Премиум или Премиум+
                # Премиум и премиум+
                if part1 == 1:
                    title = "Покупка Премиума"
                    description = f"Получите Премиум за {part2} звезд"
                else:
                    title = "Покупка Премиум+"
                    description = f"Получите Премиум+ за {part2} звезд"

                # Стоимость в 'XTR' рассчитывается по тарифу 1 звезда = 1 единица XTR
                prices = [LabeledPrice(f"{title}", part2 * 1)]  # Стоимость в "XTR", если 1 звезда = 1 XTR
                await update.message.reply_invoice(
                    title=title,
                    description=description,
                    payload=f"premium_{part1}_{part2}",
                    provider_token=None,  # Не используется
                    currency="XTR",
                    prices=prices,
                    need_name=False,
                    need_phone_number=False,
                    need_email=False,
                    need_shipping_address=False,
                )
            elif part1 > 2:  # Токены
                # Создаем invoice для токенов
                title = "Покупка Токенов"
                description = f"Получите {part1} токенов за {part2} звезд"

                # Стоимость в 'XTR' рассчитывается по тарифу 1 звезда = 1 единица XTR
                prices = [LabeledPrice(f"Токены {part1}", part2 * 1)]  # Стоимость в "XTR"
                await update.message.reply_invoice(
                    title=title,
                    description=description,
                    payload=f"tokens_{part1}_{part2}",
                    provider_token=None,  # Не используется
                    currency="XTR",
                    prices=prices,
                    need_name=False,
                    need_phone_number=False,
                    need_email=False,
                    need_shipping_address=False,
                )
            else:
                await update.message.reply_text("Вход запрещен!")
        except ValueError:
            await update.message.reply_text("Вход запрещен!")
    else:
        await update.message.reply_text("Вход запрещен!")


# Обработчик подтверждения оплаты
async def precheckout_callback(update: Update, context: CallbackContext):
    query = update.pre_checkout_query
    if query.invoice_payload.startswith('premium') or query.invoice_payload.startswith(
            'tokens'):  # Проверяем payload для премиум или токенов
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Что-то пошло не так. Попробуйте снова.\nЕсли вы столкнулись с какой-то проблемой, то пишите нашему боту обратной связи : @Clickerstart_bot .")


# Обработчик успешной оплаты
async def successful_payment(update: Update, context: CallbackContext):
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    amount = int(payment.total_amount / 100)  # Количество звезд, которое заплатил пользователь

    # Получаем данные из payload (номер премиума, токенов и количество звезд)
    part1, part2 = payload.split('_')[1:3]
    part1 = int(part1)  # Номер премиума (1 или 2) или количество токенов
    part2 = int(part2)  # Количество звезд

    # Получаем chat_id пользователя, который совершил оплату
    chat_id = update.message.chat_id

    # Отправляем сообщение через второго бота
    second_bot = Application.builder().token(SECOND_BOT_TOKEN).build()

    if part1 == 1:
        text = f"Вы оплатили {part2} звезд. Получите Премиум!"
        button_text = "Забрать Премиум"
    elif part1 == 2:
        text = f"Вы оплатили {part2} звезд. Получите Премиум+!"
        button_text = "Забрать Премиум+"
    else:
        text = f"Вы оплатили {part2} звезд. Получите {part1} токенов!"
        button_text = f"Получить +{part1} токенов"

    keyboard = ReplyKeyboardMarkup([[KeyboardButton(button_text)]], resize_keyboard=True)

    await second_bot.bot.send_message(
        chat_id=chat_id,  # Отправляем сообщение пользователю, который оплатил
        text=text,
        reply_markup=keyboard
    )

    # Уведомляем пользователя в основном чате
    await update.message.reply_text(f"Оплата на {part2} звезд успешно выполнена!\nМы написали вам в боте @NickNaymesBot !")


# Запуск бота
def main():
    application = Application.builder().token(MAIN_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    application.run_polling()


if __name__ == "__main__":
    main()
