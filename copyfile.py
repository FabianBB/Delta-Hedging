
def dynamic_hedge_simulation_3(paths, K, r, sigma, T, dt, rehedge_interval, transaction_cost):
    N = paths.shape[1]
    n_steps = paths.shape[0] - 1
    B0 = 1  # Initial bond price

    portfolio_values = np.zeros_like(paths)
    relative_pnl = np.zeros(N)

    for j in range(N):  # Loop over each simulation path
        cash = 0
        stock_held = 0
        bond_held = B0
        initial_V_call = BS_CALL(paths[0, j], K, T, r, sigma)
        initial_V_put = BS_PUT(paths[0, j], K, T, r, sigma)
        cash += initial_V_call + initial_V_put  # initial proceeds from selling options

        for i in range(n_steps):
            if i % rehedge_interval != 0:
                continue
            S = paths[i, j]
            t = i * dt

            # Compute option prices and deltas
            # V_call = BS_CALL(S, K, T - t, r, sigma)
            delta_call = BS_delta(S, K, T - t, r, sigma)
            # V_put = BS_PUT(S, K, T - t, r, sigma)
            delta_put = BS_delta(S, K, T - t, r, sigma, option_type="put")

            # Adjusting stock position to match total delta
            desired_stock_position = delta_call + delta_put
            stock_to_buy = desired_stock_position - stock_held
            transaction_costs = np.abs(stock_to_buy * S) * transaction_cost
            cash -= (stock_to_buy * S + transaction_costs)
            stock_held = desired_stock_position

            # Bond balance update assuming continuous compounding
            bond_held *= np.exp(r * dt)
            cash *= np.exp(r * dt)

            # Update portfolio value
            portfolio_values[i, j] = stock_held * S + cash + bond_held * B0

        # Final step calculation
        ST = paths[-1, j]
        VT_call = BS_CALL(ST, K, 0, r, sigma)
        VT_put = BS_PUT(ST, K, 0, r, sigma)
        final_value = stock_held * ST + cash + bond_held * B0 - VT_call - VT_put
        portfolio_values[-1, j] = final_value
        relative_pnl[j] = np.exp(-r * T) * (final_value / (initial_V_call + initial_V_put))

    return portfolio_values, relative_pnl
