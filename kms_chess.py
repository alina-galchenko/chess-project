import chess
import chess.pgn
import bz2
import sqlite3 #not used yet

import pandas
import requests
import wget
import os
import zstandard
import io
import itertools
import tqdm
import collections
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


PIECE_SYMBOLS = [chess.Piece.from_symbol(p) for p in "pnbrqPNBRQ"]


def download_game_files(number_of_files = 1, folder = "games", prefix = "temp"):
    urls = requests.get("https://database.lichess.org/standard/list.txt").text.split("\n")
    for url in urls[::-1][:number_of_files]:
        dir_size = sum(os.path.getsize("games/"+f) for f in os.listdir('./games') if os.path.isfile("games/"+f)) / 1e9
        if  dir_size > 50:
            raise Exception("Too much data downloaded")
        month = url.split("rated_")[1].split(".")[0]
        filename = f"{folder}/{prefix}{month}.bz2"
        if os.path.exists(filename):
            continue
        wget.download(url, filename)
        
        
def get_details_from_game(game, max_moves, number_of_ply_without_capture):
    # get the material count as a list from each game
    rows = []
    board = game.board()
    try:
        leading = [game.headers["Event"], game.headers["Result"], int(game.headers["WhiteElo"]), int(game.headers["BlackElo"]), game.headers["Site"].split("/")[-1]]
    except:
        return rows
    for (ii, move) in enumerate(itertools.islice(game.mainline_moves(), 2*max_moves)):
        board.push(move)
        piece_count = collections.Counter(board.piece_map().values())
        rows.append(leading + [ii] + [piece_count.get(p,0) for p in PIECE_SYMBOLS])
    return [row[0] for row in zip(rows, rows[number_of_ply_without_capture:]) if row[0][-10:] == row[1][-10:]]


def games_generator(folder = "games"):
    # lopp over all the months downloaded
    # loop over the file for each month, reading lines into one pgn blob
    # read the game using the python-chess library
    for filename in os.listdir(folder)[:]:
        if ".bz2" not in filename:
            continue
        with open(os.path.join(folder, filename), 'rb') as fh:
            dctx = zstandard.ZstdDecompressor()
            stream_reader = dctx.stream_reader(fh)
            text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
            i = 0
            rows = []
            pgn = ""
            row_estimate = int(os.path.getsize(os.path.join(folder, filename)) / 8.4 )
            for line in text_stream:
                if line.startswith('[Event'):
                    if len(pgn):
                        game = chess.pgn.read_game(io.StringIO(pgn))
                        yield game
                    pgn = ""
                pgn += line

def SetDatabase(allDetails):
    DF = pandas.DataFrame(sum(allDetails, []), columns=["Event", "Result", "WhiteElo", "BlackElo", "Site", "Move", "p", "n", "b", "r", "q", "P", "N", "B", "R", "Q"])
    # DF.to_csv("database13.csv", index= False)
    #Piece_Imbalance(DF, details)
    return DF

def Piece_Imbalance(allDetails):
    df = pandas.DataFrame([details[len(details)-1] for details in allDetails if len(details) > 0], columns=["Event", "Result", "WhiteElo", "BlackElo", "Site", "Move", "p", "n", "b", "r", "q", "P", "N", "B", "R", "Q"])
    piece_types = [("pawn", "p"), ("knight", "n"), ("bishop", "b"), ("rook", "r"), ("queen", "q")]
    for (piece_name, p) in piece_types:
        df[f"{piece_name}_difference"] = df[p.upper()] - df[p]
    #OUTPUT = DF[DF.Move == (details[len(details)-1][5] for details in AllDetails)][[f"{p}_difference" for (p, _) in piece_types]]
    out = df[["Event", "Result", "WhiteElo", "BlackElo"]+[f"{p}_difference" for (p, _) in piece_types]]
    out.to_csv("database13_diff.csv", index=False)
    return out

def PieceImbalanceValue(dfDifference, game_type, colour, piece, ELO_range):
    MIN_ELO = 0
    MAX_ELO = 1
    # ELO_range indices
    df_filtered = dfDifference[(dfDifference.Event.str.contains(game_type)) & (dfDifference.WhiteElo.between(ELO_range[MIN_ELO], ELO_range[MAX_ELO])) &
                               (dfDifference.BlackElo.between(ELO_range[MIN_ELO], ELO_range[MAX_ELO]))][["Result", f"{piece}_difference"]]
    #rename piece difference column into just difference
    MaxImbalance = 0
    if piece == 'pawn': MaxImbalance = 8
    elif piece == 'knight' or piece == 'rook' or piece == 'bishop': MaxImbalance = 2
    elif piece == 'queen': MaxImbalance = 1
    Win = 0
    if colour == 'white':
        Win = '1-0'
    elif colour == 'black':
        Win = '0-1'
    prev_percentage = None
    allPercDifferences = 0
    Result_Win_Rows = df_filtered[df_filtered.Result == Win].shape[0]
    for imbalance in range(-MaxImbalance, MaxImbalance + 1):
        percentage = df_filtered[(df_filtered.Result == Win) & (df_filtered[f"{piece}_difference"] == imbalance)].shape[0]/Result_Win_Rows*100
        if prev_percentage is None:
            prev_percentage = percentage
        else:
            curr_percentage = percentage
            percDifference = abs(curr_percentage - prev_percentage)
            prev_percentage = percentage
            allPercDifferences += percDifference
    return allPercDifferences / (MaxImbalance*2)

#download_game_files()
#SetDatabase(details).to_csv("imbalance.csv", index= False)
#print(SetDatabase(details))


gameGen = games_generator()
allDetails = []
for game in gameGen:
    game_length_half = len(get_details_from_game(game,75,0))
    game_length_ply = 0
    if game_length_half % 2 == 0: game_length_ply = game_length_half//2
    else: game_length_ply = game_length_half//2 + 1
    details = get_details_from_game(game,round(game_length_ply*0.6),6)
    allDetails += [details]
    # if len(allDetails) > 100:
    #     break
    if len(allDetails) % 1000 == 0:
        print("processed: ", len(allDetails))

piece_types = ["pawn","knight", "bishop", "rook", "queen"]
SetDatabase(allDetails)
dfDifference = Piece_Imbalance(allDetails)
for piece in piece_types:
    print(piece)
    for colour in ['white', 'black']:
        print(colour)
        print(PieceImbalanceValue(dfDifference,"Classical",colour,piece,[1400,1700]))