

def get_mean_open_close(data_df):
    price = data_df.copy()
    price['price'] = price.open
    return price