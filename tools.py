import os
import requests
import pandas as pd
from eod import EodHistoricalData

# Ticker symbols of companies in the US need to be followed by .US : "AAPL" -> "AAPL.US"

key = os.environ["API_EOD"]  # gathering the API-Key for EODhistoricaldata, stored in an environment variable
client = EodHistoricalData(key)  # setting up the client for downloading the fundamental data


def get_market(symbol: str, exchange: str):
    """
    Returns a list of all stock symbols within the same industry of a given exchange
    :param symbol: requires one
    single ticker symbol as a string
    :param exchange: requires the symbol of an exchange for example "NASDAQ" or "NYSE". Here is
    a full list of all exchanges available: https://eodhistoricaldata.com/financial-apis/list-supported-exchanges/
    :return: list
    """
    market_symbols = []
    us_exchange = False

    if ".US" in symbol:
        symbol = symbol.replace(".US", "")
        us_exchange = True

    initial_resp = requests.get(f'https://eodhistoricaldata.com/api/screener?api_token={key}&'
                                f'filters=['
                                f'["exchange","=","{exchange}"],'
                                f'["code","=","{symbol}"]'
                                f']&limit=500&offset=0')

    stock_industry = initial_resp.json()["data"][0]["industry"]

    market_resp = requests.get(f'https://eodhistoricaldata.com/api/screener?api_token={key}'
                               f'&filters=['
                               f'["industry","=","{stock_industry}"],'
                               f'["exchange","=","NASDAQ"]]&limit=500&offset=0')

    for i in market_resp.json()["data"]:
        if us_exchange:
            market_symbols.append(i["code"] + ".US")
        else:
            market_symbols.append(i["code"])

    market_symbols.remove(symbol)

    return market_symbols


def get_statement(element, statement_type="Balance_Sheet"):
    """
    Returns all recorded historical statements depending on the statement type and the ticker symbol as a DataFrame

    :param element: requires one ticker symbol or a list of ticker symbols
    :param statement_type: optional parameter. Possible input: Balance_Sheet, Income_Statement, Cash_Flow
    :return: DataFrame
    """

    resp = []

    # downloading multiple datasets if a list of symbols is given or one if only one symbol is given
    if isinstance(element, list):
        for i in element:
            series = client.get_fundamental_equity(i)
            resp.append(series)
    else:
        series = client.get_fundamental_equity(element)
        resp.append(series)

    # filtering the dataset - quarterly was chosen, as the annual frequency is included
    data = pd.DataFrame(
        pd.DataFrame(resp)["Financials"]
        .iloc[0][statement_type]["quarterly"]
    )

    return data


def get_highlights(element):
    """
    Returns the fundamentals section "Highlights" of EODhistoricaldata as a DataFrame for every stock/stocks given

    :param element: requires one ticker symbol or a list of ticker symbols
    :return: DataFrame
    """

    resp = []

    if isinstance(element, list):
        for i in element:
            series = client.get_fundamental_equity(i)
            resp.append(series)
    else:
        series = client.get_fundamental_equity(element)
        resp.append(series)

    data = pd.DataFrame(
        pd.DataFrame(resp)["Highlights"].iloc[0],
        index=[0]
    )

    return data


def market_overview(elements: list):
    """
    Provides an overview about different KPIs for all stock tickers given as a list
    The highlights can be adjusted, or a list of the highlights visit:

    https://eodhistoricaldata.com/financial-apis/stock-etfs-fundamental-data-feeds/#Equities_Fundamentals_Data_API

    :param elements: must be a list containing one or more stock tickers that should be compared
    :return: DataFrame
    """
    kpis = {}
    for element in elements:
        highlights = get_highlights(element)
        kpis[str(element)] = [
            highlights["EarningsShare"].iloc[0],
            highlights["EPSEstimateCurrentYear"].iloc[0],
            highlights["ProfitMargin"].iloc[0],
            highlights["OperatingMarginTTM"].iloc[0],
            highlights["ReturnOnAssetsTTM"].iloc[0],
            highlights["QuarterlyRevenueGrowthYOY"].iloc[0],
            highlights["QuarterlyEarningsGrowthYOY"].iloc[0]]
    df = pd.DataFrame(kpis, index=["EarningsShare",
                                   "EPSEstimateCurrentYear",
                                   "ProfitMargin",
                                   "OperatingMarginTTM",
                                   "ReturnOnAssetsTTM",
                                   "QuarterlyRevenueGrowthYOY",
                                   "QuarterlyEarningsGrowthYOY"])

    return df


def get_average(equity: str, market):  # Builds upon the market_overview function
    """
    returns a DataFrame containing different KPIs of one stock and the average of its market given as a separate list
    The market of the stock has to be provided manually as a list

    Example:

    df = market_overview(["BCOR.US", "BSIG.US", "RILY.US", "VRTS.US", "WETF.US"])  # Creating the DataFrame of a market
    df1 = get_average("BCOR.US",df)  # Comparing the stock and the average of its market according to our stock market index

    :param equity: Ticker symbol of the stock that ought to be compared
    :param market: DataFrame created by the
    market_overview function with symbols of the competitors you want to derive an avarage of - Including the symbol
    of the stock you want to compare to its market
    :return: DataFrame
    """

    index = market.index
    data = {}
    market_average = []
    for row in index:
        average = market.loc[row].mean()
        market_average.append(average)
    data[str(equity)] = market[equity]
    data["Market"] = market_average
    df = pd.DataFrame(data, index=["EarningsShare",
                                   "EPSEstimateCurrentYear",
                                   "ProfitMargin",
                                   "OperatingMarginTTM",
                                   "ReturnOnAssetsTTM",
                                   "QuarterlyRevenueGrowthYOY",
                                   "QuarterlyEarningsGrowthYOY"])

    return df
