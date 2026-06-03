# =============================================================================
#          File: passes_map.py
#        Author: Andre Brener
#   Description: Plot the average pitch position of each player and the pass
#                distribution between them for a single game.
# =============================================================================
import os

import matplotlib.pyplot as plt
import pandas as pd

plt.style.use('fivethirtyeight')


def get_football_field(x_boundaries, y_boundaries, x_small_area, x_big_area,
                        y_small_area, y_big_area):
    # Left & Right boundaries
    for x in x_boundaries:
        plt.plot([x, x], [y_boundaries[0], y_boundaries[1]], color='k', lw=2)
    for y in y_boundaries:
        plt.plot([x_boundaries[0], x_boundaries[1]], [y, y], color='k', lw=2)
    # Half
    y_half = (y_boundaries[0] + y_boundaries[1]) / 2
    plt.plot([x_boundaries[0], x_boundaries[1]], [y_half, y_half], color='k', lw=2)
    # Small Area
    for x in x_small_area:
        plt.plot([x, x], [y_boundaries[0], y_small_area[0]], color='k', lw=2)
        plt.plot([x, x], [y_boundaries[1], y_small_area[1]], color='k', lw=2)
    for y in y_small_area:
        plt.plot([x_small_area[0], x_small_area[1]], [y, y], color='k', lw=2)
    # Big Area
    for x in x_big_area:
        plt.plot([x, x], [y_boundaries[0], y_big_area[0]], color='k', lw=2)
        plt.plot([x, x], [y_boundaries[1], y_big_area[1]], color='k', lw=2)
    for y in y_big_area:
        plt.plot([x_big_area[0], x_big_area[1]], [y, y], color='k', lw=2)

def main(csv_path):
    table = pd.read_csv(csv_path, sep=';', index_col=0)

    players = table['nombre_apellido'].tolist()
    x = table['y_promedio'].tolist()
    y = table['x_promedio'].tolist()
    touches_raw = table['pases'].tolist()

    touches = [20 * item for item in touches_raw]

    passes = {}
    for row in table.iterrows():
        index, data = row
        temp = []
        player = data[0]
        for n in range(4, len(data)):
            temp.append(data[n])
        passes[player] = temp

    x_boundaries = [-35, 35]
    y_boundaries = [0, 110]
    x_small_area = [-8, 8]
    x_big_area = [17.5, -17.5]
    y_small_area = [5, 105]
    y_big_area = [16, 94]

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.scatter(x, y, s=touches, color='red')
    get_football_field(x_boundaries, y_boundaries, x_small_area, x_big_area,
                       y_small_area, y_big_area)
    ax.annotate('Líneas: pases. Grosor indica cantidad de pases', xy=(-15, 89), size=10, ha="center", color='0.3')
    ax.annotate('Tamaño del Círculo: pases totales completados', xy=(-15, 86), size=10, ha="center", color='0.3')
    ax.annotate('Posición del Círculo: posición promedio', xy=(-15, 83), size=10, ha="center", color='0.3')
    ax.annotate('Líneas para 5+ passes', xy=(-15, 80), size=10, ha="center", color='0.3')
    ax.annotate('Solamente jugadores titulares', xy=(-15, 77), size=10, ha="center", color='0.3')
    plt.title('River Plate vs Independiente del Valle', fontsize=16, weight='bold')
    for i, player in enumerate(players):
        ax.annotate(player, xy=(x[i], y[i]), xytext=(x[i], y[i] - 5.5), size=13, ha="center")
        for n in range(len(players)):
            player_passes = passes[player][n]
            width = player_passes / 25
            if player_passes > 4:
                x_start = x[i]
                x_length = x[n] - x[i]
                y_start = y[i]
                y_length = y[n] - y[i]
                if x_length > 0:
                    x_start = x[i] + 1
                    x_length = x[n] - x[i] - 1
                else:
                    x_start = x[i] - 1
                    x_length = x[n] - x[i] + 1.5
                if y_length > 0:
                    y_start = y[i] + 1.5
                    y_length = y[n] - y[i] - 2
                else:
                    y_start = y[i] - 1.5
                    y_length = y[n] - y[i] + 2

                plt.arrow(x_start, y_start, x_length, y_length,
                          head_length=2, color='0.15', alpha=0.7, width=width,
                          head_width=1.5, length_includes_head=True)
    ax.grid(False)
    ax.axis('off')

    plt.show()


if __name__ == '__main__':
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'river_valle.csv')
    main(csv_path)
