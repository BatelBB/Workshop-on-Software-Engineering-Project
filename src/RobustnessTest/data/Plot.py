import pandas as pd
import matplotlib.pyplot as plt


def plot(dataframe_path, title):

    df = pd.read_csv(dataframe_path, dtype={'Threads': int, 'Runtime': float})
    fig, ax = plt.subplots(1, 1)
    xs, ys = list(), list()

    for index, row in df.iterrows():
        xs.append(row['Threads'])
        ys.append(row['Runtime'])

    ax.plot(xs, ys, linewidth=2)
    ax.set_xlabel('Number Of Threads')
    ax.set_ylabel('Runtime(s)')
    ax.set_title(title)
    plt.savefig(f'{title}.png', dpi=720)
    plt.show()

if __name__ == '__main__':
    plot('purchase_shopping_cart_with_different_carts.data', "Purchase-Shopping-Cart-with-Different-Cart")
