def run_app():
    app = IBApp()
    app.connect('127.0.0.1', 7497, clientId=1)

    # Start the API in a separate thread
    api_thread = threading.Thread(target=app.run, daemon=True)
    api_thread.start()

    # Wait for the connection to establish
    time.sleep(1)  # Give it a moment to connect

    # Create a contract object for the instrument you want to get data for
    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"

    # Request historical data
    app.reqHistoricalData(
        reqId=1,
        contract=contract,
        endDateTime='',
        durationStr='2 D',
        barSizeSetting='5 mins',
        whatToShow='TRADES',
        useRTH=0,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )

    # Wait until data is received or timeout
    timeout = 10  # seconds
    start_time = time.time()
    while not app.data_received and time.time() - start_time < timeout:
        time.sleep(1)

    if app.data_received:
        print("Data received successfully.")
        print(app.df)
    else:
        print("Failed to receive data.")

    # Disconnect from IB
    app.disconnect()
    api_thread.join()

if __name__ == "__main__":
    run_app()
