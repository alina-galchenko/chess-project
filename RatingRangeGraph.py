import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

data = pd.read_csv("AllMidgameData.csv")
default = data.groupby("Piece").mean(["Value %"])
pu = default[default.index == "pawn"].values[0][0]
rating_ranges = data["Rating range"].unique()
game_types = data["Game type"].unique()
pieces = data["Piece"].unique()
colours = data["Colour"].unique()
criteria = {"Game type" : ["Bullet", "Blitz", "Classical", "Correspondence"],
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
    "rook": "blue",
    "bishop": "red",
    "knight": "purple",
    "pawn":"green"}

# for (i ,rating_range) in enumerate(rating_ranges):
#     data_t = data[(data["Game type"] == "Classical") & (data["Rating range"] == rating_range)].groupby("Piece").mean(["Value %"])
#     filtered = data_t/default[default.index == "pawn"].values[0][0]
#     for piece in ["pawn", "knight", "bishop", "rook", "queen"]:
#         plt.plot(i + (0.25 if piece == "bishop" else 0),
#                  filtered[filtered.index==piece].values[0][0], '.', markersize=15, marker=unicode_mappings[piece],
#                  color=color_mappings[piece])

def RatingRangeGraph():
    criterium = "Rating range"
    filtered = pd.read_csv(f"Weighted_{criterium}.csv")
    for i in range(0, len(filtered[criterium]), 6):
        #print(i)
        #print(filtered["Game type"][i])
        PieceTemp = filtered["Piece"][i + 5]
        RatingRangeTemp = filtered["Rating range"][i + 5]
        CoefficientTemp = filtered["Coefficient"][i + 5]
        print(PieceTemp, RatingRangeTemp, CoefficientTemp)
        for j in range(4, -1, -1):
            filtered["Piece"][i + j + 1] = filtered["Piece"][i + j]
            filtered["Rating range"][i + j + 1] = filtered["Rating range"][i + j]
            filtered["Coefficient"][i + j + 1] = filtered["Coefficient"][i + j]
        filtered["Piece"][i] = PieceTemp
        filtered["Rating range"][i] = RatingRangeTemp
        filtered["Coefficient"][i] = CoefficientTemp
    for piece in pieces:
        for i in range(len(criteria[criterium])):
            plt.plot(i + (0.25 if piece == "bishop" else 0),
                    filtered[filtered["Piece"] == piece].values[i][2], ".", markersize = 5, marker = unicode_mappings[piece],
                        color = color_mappings[piece])
            print(i)
            print(piece)
            print(filtered[filtered["Piece"] == piece].values[i][2])
    ax = plt.subplot(111)
    plt.ylim(0, 14)
    plt.title("Piece values by player rating")
    plt.xlabel(criterium)
    plt.ylabel("Relative piece value")
    plt.xticks(list(range(len(criteria[criterium]))), criteria[criterium])
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 1, box.height])
    pawn_patch = mpatches.Patch(color = "green", label = "Pawn")
    knight_patch = mpatches.Patch(color = "purple", label = "Knight")
    bishop_patch = mpatches.Patch(color = "red", label = "Bishop")
    rook_patch = mpatches.Patch(color = "blue", label = "Rook")
    queen_patch = mpatches.Patch(color = "black", label = "Queen")

    ax.legend(handles = [pawn_patch, knight_patch, bishop_patch, rook_patch, queen_patch], loc='center left', bbox_to_anchor=(1, 0.5))
    print(default)
    plt.show()


RatingRangeGraph()
# GameTypesNonWeighted() 