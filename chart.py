import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv("AllMidgameData.csv")
default = data.groupby("Piece").mean(["Value %"])
pu = default[default.index == "pawn"].values[0][0]
rating_ranges = data["Rating range"].unique()
game_types = data["Game type"].unique()
pieces = data["Piece"].unique()
colours = data["Colour"].unique()
criteria = {"Game type" : game_types,
            "Rating range" : rating_ranges,
            "Colour" : colours}
# print(rating_ranges)
# print(pu)
# print(game_types)
# print(pieces)
print(colours)

unicode_mappings = {
    "king" : "$\u265A$",
    "queen": "$\u265B$",
    "rook": "$\u265C$",
    "bishop": "$\u265D$",
    "knight": "$\u265E$",
    "pawn":"$\u265F$"}

color_mappings = {
    "king" : "black",
    "queen": "black",
    "rook": "black",
    "bishop": "black",
    "knight": "black",
    "pawn":"black"}

# for (i ,rating_range) in enumerate(rating_ranges):
#     data_t = data[(data["Game type"] == "Classical") & (data["Rating range"] == rating_range)].groupby("Piece").mean(["Value %"])
#     filtered = data_t/default[default.index == "pawn"].values[0][0]
#     for piece in ["pawn", "knight", "bishop", "rook", "queen"]:
#         plt.plot(i + (0.25 if piece == "bishop" else 0),
#                  filtered[filtered.index==piece].values[0][0], '.', markersize=15, marker=unicode_mappings[piece],
#                  color=color_mappings[piece])

def RatingNonWeighted():
    for (i ,rating_range) in enumerate(rating_ranges):
        data_t = data[(data["Rating range"] == rating_range)].groupby("Piece").mean(["Value %"])
        filtered = data_t/default[default.index == "pawn"].values[0][0]
        for piece in ["pawn", "knight", "bishop", "rook", "queen"]:
            plt.plot(i + (0.25 if piece == "bishop" else 0),
                     filtered[filtered.index==piece].values[0][0], '.', markersize=15, marker=unicode_mappings[piece],
                     color=color_mappings[piece])
    plt.ylim(0, 14)
    plt.title("Piece values by varying amateur ratings (non-weighted)")
    plt.xlabel("Rating range")
    plt.ylabel("Piece value / pu")
    plt.xticks(list(range(len(rating_ranges))), rating_ranges)
    print(default)
    plt.show()


def GameTypesNonWeighted():
    for [i, game_type] in enumerate(game_types):
        data_table = data[data["Game type"] == game_type].groupby("Piece").mean(["Value %"])
        filtered = data_table/pu
        for piece in pieces:
            plt.plot(i + (0.25 if piece == "bishop" else 0),
                     filtered[filtered.index==piece].values[0][0], ".", markersize = 15, marker=unicode_mappings[piece],
                      color=color_mappings[piece])
    plt.ylim(0, 14)
    plt.title("Piece values by varying game types (non-weighted)")
    plt.xlabel("Game type")
    plt.ylabel("Piece value / pu")
    plt.xticks(list(range(len(game_types))), game_types)
    print(default)
    plt.show()

def ColourNonWeighted():
    for [i, colour] in enumerate(colours):
        data_table = data[data["Colour"] == colour].groupby("Piece").mean(["Value %"])
        filtered = data_table/pu
        for piece in pieces:
            plt.plot(i + (0.25 if piece == "bishop" else 0),
                     filtered[filtered.index==piece].values[0][0], ".", markersize = 15, marker=unicode_mappings[piece],
                      color=color_mappings[piece])
    plt.ylim(0, 14)
    plt.title("Piece values by varying piece colours (non-weighted)")
    plt.xlabel("Colour")
    plt.ylabel("Piece value / pu")
    plt.xticks(list(range(len(colours))),colours)
    print(default)
    plt.show()

def Weghted(criterium):
    filtered = pd.read_csv(f"Weighted_{criterium}.csv")
    for piece in pieces:
        for i in range(len(criteria[criterium])):
            plt.plot(i + (0.25 if piece == "bishop" else 0),
                    filtered[filtered["Piece"] == piece].values[0][2], ".", markersize = 5, marker = unicode_mappings[piece],
                        color = color_mappings[piece])
    plt.ylim(0, 14)
    plt.title(f"Piece values by varying {criterium}s (weighted)")
    plt.xlabel(criterium)
    plt.ylabel("Piece value / pu")
    plt.xticks(list(range(len(criteria[criterium]))), criteria[criterium])
    print(default)
    plt.show()

Weghted("Rating range")
# GameTypesNonWeighted()