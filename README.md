# EODhistoricaldata API Interface and Analysis Tool

This tool provides a Python interface for querying and analyzing financial data from EODhistoricaldata API. The primary functions allow users to retrieve stocks within the same industry, access financial statements, and highlight key financial metrics.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python Version**: Python 3.x
- **Python Libraries**:
  - `os`
  - `requests`
  - `pandas`
  - `matplotlib`
- **API Access**: An access key for EODhistoricaldata.

## Environment Variable Setup

Set your EODhistoricaldata API key in an environment variable named `API_EOD`.

## Features

1. **get_market**: Given a stock ticker, it identifies all relevant stocks within the same industry. User input might be required.
2. **get_statement**: Fetches financial statements such as Balance Sheet, Income Statement, or Cash Flow for the provided stock ticker(s).
3. **get_highlights**: Provides key financial metrics for the specified stock ticker(s) aggregated in the "Highlights" of the fundamentals data.
4. **analysis**: Performs analysis by comparing the given ticker's key financial metrics with the market average or another specific ticker.
5. **plot_position**: Visualizes the historical trend of a specific financial metric.

## Usage

### Access Relevant Stocks in the same Industry
```python
tickers = get_market("AAPL.US", limit_per_exchange=5)
print(tickers)
```

### Fetch all available Financial Statements for a stock
```python
balance_sheet = get_statement("AAPL.US", statement_type="Balance_Sheet")
print(balance_sheet)
```

### Access Key Financial Metrics
```python
highlights = get_highlights(["AAPL.US", "MSFT.US"])
print(highlights)
```

### Compare Key Financial Metrics of a stock with its competitors
```python
output = analysis("AAPL.US", ["MSFT.US", "GOOGL.US"])
print(output)
```

### Visualize the developement of a Statement position
```python
statement = get_statement("AAPL.US", statement_type="Balance_Sheet")
plot_position("totalAssets", statement)
```

## Notes
- When using the get_market function, the tool initially checks the provided stock's listing across major exchanges (Xetra, US, LSE, HK). In the case of a stock listed on multiple exchanges, a warning is provided to the user.
- In the event that company names sound similar, the user will be prompted to make a selection, ensuring that accurate and relevant data is retrieved.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

Ensure you comply with the terms of use of EODhistoricaldata API when using this tool. The tool and its functions were designed for educational purposes and may require further refinement for production use.


