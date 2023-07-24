import os
import requests
import matplotlib.pyplot as plt
import pandas as pd
from eod import EodHistoricalData


key = os.environ["API_EOD"]  # gathering the API-Key for EODhistoricaldata, stored in an environment variable
client = EodHistoricalData(key)  # setting up the client for downloading the fundamental data


def get_group(symbol, limit_per_exchange=5):
    """
    Access all relevant stocks within a certain industry, determined by the symbol given
    :param symbol: requires one single ticker symbol as a string
    :type symbol: str
    :param limit_per_exchange: number of stocks to be downloaded per exchange
    :type limit_per_exchange: int (default: 5)
    :return: list of all stock symbols within the same industry of the most relevant exchanges
    """
    group_symbols = set()
    tickers = []
    relevant_exchanges = ['Xetra', 'US', 'LSE', 'HK']  # List of what I found to be the most relevant exchanges

    if ".US" in symbol:
        symbol = symbol.replace(".US", "")

    # Searching the stock symbol on the most relevant exchanges
    for exchange in relevant_exchanges:

        initial_resp = requests.get(f'https://eodhistoricaldata.com/api/screener?api_token={key}&filters=['
                                    f'["code","=","{symbol}"],'
                                    f'["exchange","=","{exchange}"]'
                                    f']&limit={limit_per_exchange}&offset=0')

        if len(initial_resp.json()["data"]) > 0:
            tickers.append(initial_resp.json()["data"][0])

    # Check if the stock is listed on several Exchanges with the same symbol
    if len(tickers) > 1:
        print("ATTENTION: Stock is listed on different exchanges. "
              "First one is taken as the basis for the industry.")
    stock_industry = tickers[0]["industry"]
    tickers.clear()

    # Searching for all the stocks within the same industry on all different exchanges
    for exchange in relevant_exchanges:

        market_resp = requests.get(f'https://eodhistoricaldata.com/api/screener?api_token={key}'
                                   '&sort=market_capitalization.desc&filters=['
                                   f'["industry","=","{stock_industry}"],'
                                   f'["exchange","=","{exchange}"]'
                                   f']&limit={limit_per_exchange}&offset=0')

        if len(market_resp.json()["data"]) > 1:
            for element in market_resp.json()["data"]:
                tickers.append((element["code"], element["name"]))

    firms = [firm[1] for firm in tickers]  # List of all company names
    black_list = set()

    # Check to avoid redundancies
    for i in tickers:  # Set of all symbols that shall be excluded
        for t in firms:
            # Check if the company name is similar to another company name
            # and if the company name is not in the black list or the group symbols
            # and if the company name is more than once in the list
            if i[1] == t and\
                    i[0] not in black_list and i[0] not in group_symbols and\
                    firms.count(i[1]) > 1:

                print("ATTENTION: Some companies sound similar")

                filtered_tickers = [ticker for ticker in tickers if ticker != i]
                other_ticker = [x for x in filtered_tickers if x[1] == t][0]

                print(i[1], f"is {firms.count(i[1])} times in the list")
                print(i[1], f"({i[0]})", "and", t, f"({other_ticker[0]})", "sound similar")

                answer = input(f"Should I add\n"
                               f"1) {i[1]} ({i[0]})\n"
                               f"2) {t} ({other_ticker[0]})\n"
                               f"3) None ? (1/2/3)\n"
                               f":")

                # Check if the answer is valid
                while answer not in ["1", "2", "3"]:
                    answer = input("Please enter '1', '2' or '3':\n:")

                # Check if the answer is yes or no
                if answer == "1":
                    group_symbols.add(i[0])
                    black_list.add(other_ticker[0])
                    continue
                elif answer == "2":
                    black_list.add(i[0])
                    group_symbols.add(other_ticker[0])
                    continue
                elif answer == "3":
                    black_list.add(i[0])
                    black_list.add(other_ticker[0])
        continue

    return list(group_symbols)


def get_statement(element, statement_type="Balance_Sheet"):
    """
    :param element: ticker symbol or multiple symbol of the company
    :type element: str or list
    :param statement_type: "Balance_Sheet" or "Income_Statement" or "Cash_Flow"
    :type statement_type: str, optional
    :return: DataFrame of all recorded historical statements depending on the statement type and the ticker symbol
    """
    resp = []

    # downloading multiple datasets if a list of symbols is given or one dataset if only one symbol is given
    if isinstance(element, list):
        for i in element:
            series = client.get_fundamental_equity(i)
            resp.append(series)
    else:
        series = client.get_fundamental_equity(element)
        resp.append(series)

    # filtering the dataset
    data = pd.DataFrame(
        pd.DataFrame(resp)["Financials"]
        .iloc[0][statement_type]["quarterly"]
    )

    return data


def get_highlights(element):
    """
    Access the fundamental highlights of a ticker given by EODhistoricaldata

    :param element: ticker symbol or multiple symbol of the company
    :type element: str or list
    :return: DataFrame of the fundamental "Highlights" via EODhistoricaldata as a DataFrame for every stock given
    """
    resp = []
    multiple_resp = {}
    num = 0
    biggest_index = [0]

    # Check if data is requested for several stocks all at once
    if isinstance(element, list):
        for i in element:
            # Excluding stocks where no fundamental data is provided
            try:
                series = client.get_fundamental_equity(i)
            except requests.exceptions.HTTPError:
                continue  # Skipping the stock if there is no server response
            if "Highlights" not in series.keys():  # Sometimes no Highlights are provided
                continue

            # transforming the data of the series variable into a DataFrame
            frame = pd.DataFrame(series["Highlights"], index=[str(i)])

            # Check if the index is bigger than the biggest index
            if len(frame.transpose().index) > len(biggest_index):
                biggest_index = frame.transpose().index

            # The Highlights are standardised therefore positional the possibility of positional changes can be excluded
            multiple_resp[i] = frame.transpose()

            num += 1
            total = len(element)
            print(f"...Working on it: {num}/{total}")

        data = pd.concat(multiple_resp.values(), axis=1)
        delta = total - num

        print(f"\n{delta} values were not available")

    # Handling the case if data is requested for one stock only
    else:
        series = client.get_fundamental_equity(element)
        resp.append(series)

        data = pd.DataFrame(
            pd.DataFrame(resp)["Highlights"].iloc[0],
            index=[str(element)]
        ).transpose()

    return data


def group_overview(equity_ticker, group_ticker):

    if ".US" in equity_ticker:
        equity_ticker = equity_ticker.replace(".US", "")

    # Getting the Highlights of the group
    highlights = get_highlights(group_ticker)
    highlights_filter = highlights[highlights.columns].applymap(lambda x: isinstance(x, (float, int))).all(axis=1)
    cleaned_highlights = highlights[highlights_filter]  # Cleaning the DataFrame

    # Calculating the average of the group
    cleaned_highlights["Average"] = cleaned_highlights.drop(columns=[equity_ticker]).mean(axis=1)
    output_df = cleaned_highlights[[equity_ticker, "Average"]]

    return output_df


def plot_position(statement_position, statement):
    """
    View the development of a statement position over time
    :param statement_position: Value of the row in the statement you want to plot
    :type statement_position: str
    :param statement: statement from the get_statements function
    :type statement: pd.DataFrame
    """
    statement.loc[statement_position].astype(float)[::-1]\
        .plot(figsize=(10, 5), grid=True)\
        .margins(x=0)
    plt.title(statement_position)
    plt.xlabel('Time')
    plt.ylabel('Amount')
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])
    plt.show()
