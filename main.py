import requests
from discord_webhook import DiscordWebhook
from datetime import date


HEADERS = {
    'x-rapidapi-key': "74400d4644msh9b6c6f4b8df7174p1ff35ajsnfdd4d55500af",
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

YAHOO_FINANCE_API = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/"

BULLET_POINT = '\u2022'


def format_ticker_data(ticker_list):

    formatted_string = 'Top Gainers for Trading Session Ending {date}:\n \n'\
        .format(date=date.today().strftime("%B %d, %Y"))

    for ticker in ticker_list:
        formatted_string += \
            '__Symbol: {symbol}__ \n' \
            '{bullet_point} **Price:** ${price:,.2f} ({percent_change}) \n' \
            '{bullet_point} **Daily Volume:** {daily_volume:,} \n' \
            '{bullet_point} **10 Day Volume:** {volume_10_day:,} ({volume_10_day_percent_increase:,.2f}% increase)\n' \
            '{bullet_point} **30 Day Volume:** {volume_30_day:,} ({volume_30_day_percent_increase:,.2f}% increase)\n' \
            '{bullet_point} **50 Day MA:** {moving_average_50_day:,.2f} | **200 Day MA:** {moving_average_200_day:,.2f}\n'\
            '{bullet_point} **Percent 50 Day MA above or below 200 MA:** {percent_50_above_200_MA:,.2f}%\n\n'\
            .format(
                symbol=ticker['symbol'],
                price=ticker['price'],
                percent_change=str(ticker['percent_change']),
                daily_volume=ticker['volume_1_day_average'],
                volume_10_day=ticker['volume_10_day_average'],
                volume_10_day_percent_increase=ticker['10_day_volume_percent_increase'],
                volume_30_day=ticker['volume_30_day_average'],
                volume_30_day_percent_increase=ticker['30_day_volume_percent_increase'],
                moving_average_50_day=ticker['50_day_moving_average'],
                moving_average_200_day=ticker['200_day_moving_average'],
                percent_50_above_200_MA=ticker['percent_50_above_200_MA'],
                bullet_point=BULLET_POINT
            )

    return formatted_string


if __name__ == '__main__':

    top_movers_url = YAHOO_FINANCE_API + "market/v2/get-movers"
    top_movers_querystring = {"region": "US", "lang": "en-US", "start": "0", "count": "10"}

    top_movers_data = requests.request("GET", top_movers_url, headers=HEADERS, params=top_movers_querystring).json()

    top_gainers = top_movers_data['finance']['result'][0]
    top_losers = top_movers_data['finance']['result'][1]

    top_gainers_data = []
    top_losers_data = []

    for gainer in top_gainers['quotes']:

        gainer_details_url = YAHOO_FINANCE_API + "stock/v2/get-statistics"
        gainer_details_querystring = {"symbol": gainer['symbol'], "region": "US"}

        gainer_details_response = requests.request("GET", gainer_details_url, headers=HEADERS, params=gainer_details_querystring)
        gainer_details_data = gainer_details_response.json()

        price = gainer_details_data['quoteData'][gainer['symbol']]['regularMarketPrice']['raw']
        percent_change = gainer_details_data['quoteData'][gainer['symbol']]['regularMarketChangePercent']['fmt']

        volume_30_day_average = gainer_details_data['price']['averageDailyVolume3Month']['raw']
        volume_10_day_average = gainer_details_data['price']['averageDailyVolume10Day']['raw']
        volume_1_day_average = gainer_details_data['price']['regularMarketVolume']['raw']

        moving_average_50_day = gainer_details_data['summaryDetail']['fiftyDayAverage']['raw']
        moving_average_200_day = gainer_details_data['summaryDetail']['twoHundredDayAverage']['raw']

        top_gainers_data.append({
            'symbol': gainer['symbol'],
            'price': price,
            'percent_change': percent_change,

            'volume_1_day_average': volume_1_day_average,
            'volume_10_day_average': volume_10_day_average,
            'volume_30_day_average': volume_30_day_average,
            '10_day_volume_percent_increase': (volume_1_day_average - volume_10_day_average) * 100.00 / volume_10_day_average if volume_10_day_average != 0 else 0,
            '30_day_volume_percent_increase': (volume_1_day_average - volume_30_day_average) * 100.00 / volume_30_day_average if volume_30_day_average != 0 else 0,

            '50_day_moving_average': moving_average_50_day,
            '200_day_moving_average': moving_average_200_day,
            'percent_50_above_200_MA': (moving_average_50_day - moving_average_200_day) * 100.00 / moving_average_50_day if moving_average_50_day != 0 else 0,
        })

    formatted_top_gainers = format_ticker_data(top_gainers_data)

    # TODO: losers financial analysis
    for loser in top_losers['quotes']:
        top_losers_data.append({
            'symbol': gainer['symbol']
        })

    discord_webhook_url = "https://discord.com/api/webhooks/788252234906599455/W8JOomQFhvhBl7WXwAuOAi4Tr8i53dxECwZs5umZ7JGKY8TVH1vBakLWmW5wv5amOxGU"
    webhook = DiscordWebhook(url=discord_webhook_url, content=formatted_top_gainers)
    response = webhook.execute()



