import os
import pandas as pd
from eod import EodHistoricalData

# Ticker symbols of companies in the US need to be followed by .US : "AAPL" -> "AAPL.US"

# an Excel file (.xlsx) of a stock market index with the ticker symbols of the constituents including their industries (GICS Sector) is required
# The list has to be in a similar format as the list given in the folder "resources"
constituents_list = "./resources/s&p600.xlsx"

key = os.environ["API_EOD"]  # gathering the API-Key for EODhistoricaldata, stored in an environment variable
client = EodHistoricalData(key)  # setting up the client for downloading the fundamental data


def get_competitors(symbol: str, industry):
    """
    Gathers all the ticker symbols of its competitors in a list - competitors: defined as other companies part of the same industry

    :param symbol: The ticker symbol for the stock of interest as a string
    :param industry: The corresponding industry according to the stock market index given 
    """

    df = pd.read_excel(constituents_list)  # importing the list of constituents of the stock market index
    industries = df.set_index("GICS Sector")

    # filtering the industries DataFrame by the relevant industry and creating a list of symbols
    competitors = industries.loc[industry]["Ticker symbol"].to_list()

    return competitors


def get_statement(element, statement_type = "Balance_Sheet"):
    """
    Returns all recorded historical statements depending on the statement type and the ticker symbol as a DataFrame

    :param element: One ticker symbol or a list of ticker symbols
    :param statement_type: Optional parameter. Possible input: Balance_Sheet, Income_Statement, Cash_Flow
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

    # filtering the dataset - quartely was chosen, as the annual frequency is included
    data = pd.DataFrame(
        pd.DataFrame(resp)["Financials"]
        .iloc[0][statement_type]["quarterly"]
    )

    return data


def get_highlights(element: str):
    """
    Returns the fundamentals section "Highlights" of EODhistoricaldata as a DataFrame for every stock/stocks given

    :param element: One ticker symbol or a list of ticker symbols
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

    :param elements: Must be a list containing one or more stock tickers that should be compared
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
    :param market: DataFrame created by the market_overview function with symbols of the competitors you want to derive an avarage of - Including the symbol of the stock you want to compare to its market
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
