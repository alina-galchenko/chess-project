import pandas as pd

def WeightedValues(criterium):
    data = pd.read_csv("AllMidgameData.csv")
    if criterium == "Colour":
        default = data[data["Piece"]=="pawn"]

    default = data[(data["Piece"]=="pawn") & (data["Colour"]=="white")]
    full_total = default["Games' count"].sum()
    total_sum = default.groupby(criterium).sum()["Games' count"]
    data = data.join(total_sum, on=[criterium], rsuffix=' sum')
    double_pu = (data[data["Piece"]=="pawn"]["Games' count"]*data["Value (%)"]/full_total).sum()
    data["Weight"] = data["Games' count"]/data["Games' count sum"]
    data["Coefficient"] = data["Weight"]*data["Value (%)"]
    values_weighted = data[["Piece", criterium, "Coefficient"]].groupby(["Piece",criterium]).sum()
    values_weighted["Coefficient"] /= double_pu
    print(values_weighted)
    values_weighted.reset_index().to_csv(f"Weighted_{criterium}.csv", index=False)

WeightedValues("Colour")