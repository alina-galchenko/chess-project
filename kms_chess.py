import chess
import chess.pgn
import bz2
import sqlite3 #not used yet
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
def SetDatabase(details):
    # details1 = []
    # for i in range(202): details1 += details
    DF = pandas.DataFrame(details, columns=["Event", "Result", "WhiteElo", "BlackElo", "Site", "Move", "p", "n", "b", "r", "q", "P", "N", "B", "R", "Q"])
    DF.to_csv("database13.csv", index= False)
    for (piece_name, p) in [("pawn", "p"), ("knight", "n"), ("bishop", "b"), ("rook", "r"), ("queen", "q")]:
        DF[f"{piece_name}_difference"] = DF[p.upper()] - DF[p]
    piece_types = [("pawn", "p"), ("knight", "n"), ("bishop", "b"), ("rook", "r"), ("queen", "q")]
    OUTPUT = DF[DF.Move == (details_i[len(details_i)-1][5] for details_i in details)][[f"{p}_difference" for (p, _) in piece_types]]
    return OUTPUT

def PieceImbalanceValue(game_type, piece_losses, colour, piece, imbalance, ELO_range):

    return 0

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
    allDetails += details
    if len(allDetails) % 1000 == 0: print("processed: ", len(allDetails))

print(SetDatabase(allDetails))
