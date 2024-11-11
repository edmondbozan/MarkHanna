# utils/order.py

from ibapi.order import Order

def place_bracket_order(app, contract, action, quantity, take_profit_price, stop_loss_price):
    # Parent Order - Entry Order
    parent = Order()
    parent.orderId = app.nextOrderId
    parent.action = action  # 'BUY' or 'SELL'
    parent.orderType = 'MKT'  # Market order for immediate execution
    parent.totalQuantity = quantity
    parent.transmit = False  # Delay transmission until child orders are attached

    # Take Profit Order - Limit Order
    take_profit = Order()
    take_profit.orderId = parent.orderId + 1
    take_profit.action = 'SELL' if action == 'BUY' else 'BUY'  # Opposite action to close the position
    take_profit.orderType = 'LMT'  # Limit order to take profit
    take_profit.totalQuantity = quantity
    take_profit.lmtPrice = round(take_profit_price, 2)  # Desired take profit price
    take_profit.parentId = parent.orderId  # Link to parent order
    take_profit.transmit = False  # Will transmit with the stop loss order

    # Stop Loss Order - Stop Order
    stop_loss = Order()
    stop_loss.orderId = parent.orderId + 2
    stop_loss.action = 'SELL' if action == 'BUY' else 'BUY'  # Opposite action to close the position
    stop_loss.orderType = 'STP'  # Stop order for stop loss
    stop_loss.totalQuantity = quantity
    stop_loss.auxPrice = round(stop_loss_price, 2)  # Desired stop loss price
    stop_loss.parentId = parent.orderId  # Link to parent order
    stop_loss.transmit = True  # Transmit all orders together

    # Place the orders with IB
    app.placeOrder(parent.orderId, contract, parent)
    app.placeOrder(take_profit.orderId, contract, take_profit)
    app.placeOrder(stop_loss.orderId, contract, stop_loss)

    # Update the nextOrderId for future orders
    app.nextOrderId += 3
