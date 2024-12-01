import chess
import chess.pgn
import chess.engine
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import time

# Path to Stockfish engine (update this to the correct path for your system)
STOCKFISH_PATH = r"" #Replace with stockfish path.

def analyze_game(game, suspicious_player):
    """Analyze a single game for engine match percentage, time usage, and move patterns."""
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    board = game.board()
    node = game  # Start from the root of the PGN game tree
    engine_match = 0
    brilliant_moves = 0
    blunders = 0
    brilliant_to_blunder = 0
    total_moves = 0
    move_times = []
    previous_time = None  # For tracking time spent per move

    # Extract player information
    white_player = game.headers.get("White", "Unknown")
    black_player = game.headers.get("Black", "Unknown")
    player_side = None

    if white_player == suspicious_player:
        player_side = chess.WHITE
    elif black_player == suspicious_player:
        player_side = chess.BLACK
    else:
        return None

    while node.variations:
        next_node = node.variation(0)
        move = next_node.move

        if board.turn == player_side:
            total_moves += 1

            # Extract clock data from comments
            comment = next_node.comment
            clock_match = re.search(r"\[%clk (\d+):(\d+):(\d+)\]", comment)  # Match hours:minutes:seconds
            if clock_match:
                hours, minutes, seconds = int(clock_match.group(1)), int(clock_match.group(2)), int(clock_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds  # Convert to total seconds
                if previous_time is not None:
                    move_time = previous_time - current_time
                    move_times.append(max(0, move_time))  # Ensure no negative times
                previous_time = current_time
            else:
                move_times.append(None)

            # Analyze the board position with Stockfish
            info = engine.analyse(board, chess.engine.Limit(depth=20))
            best_move = info["pv"][0]
            eval_before = info.get("score").relative.score(mate_score=10000) / 100.0 if info.get("score") else None
            board.push(move)  # Apply the move to get the new position
            new_info = engine.analyse(board, chess.engine.Limit(depth=20))
            eval_after = new_info.get("score").relative.score(mate_score=10000) / 100.0 if new_info.get("score") else None

            if move == best_move:
                engine_match += 1

            # Detect brilliance
            if eval_before is not None and eval_after is not None and (eval_after - eval_before) > 1.5:
                brilliant_moves += 1

            # Detect blunders
            if eval_before is not None and eval_after is not None and (eval_before - eval_after) > 1.5:
                blunders += 1
                # Check if the last move was brilliant
                if brilliant_moves > 0:
                    brilliant_to_blunder += 1

        else:
            board.push(move)

        node = next_node  # Move to the next node in the game tree

    engine.quit()

    # Calculate statistics
    engine_match_rate = (engine_match / total_moves) * 100 if total_moves > 0 else 0
    move_times_filtered = [t for t in move_times if t is not None]
    avg_move_time = sum(move_times_filtered) / len(move_times_filtered) if move_times_filtered else 0

    return {
        "GameID": game.headers.get("Event", "Unknown"),
        "EngineMatchRate": engine_match_rate,
        "TotalMoves": total_moves,
        "AverageMoveTime": avg_move_time,
        "MoveTimes": move_times,
        "BrilliantMoves": brilliant_moves,
        "Blunders": blunders,
        "BrilliantToBlunder": brilliant_to_blunder,
        "White": white_player,
        "Black": black_player,
        "SuspiciousPlayer": suspicious_player,
    }


def analyze_pgn(pgn_file_path, suspicious_player):
    """Analyze all games in a PGN file for the suspicious player with progress updates."""
    results = []
    total_games = sum(1 for _ in open(pgn_file_path) if "[Event" in _)
    print(f"Total games detected: {total_games}")
    
    start_time = time.time()  # Track the start time

    with open(pgn_file_path, "r") as pgn_file:
        game_number = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            game_number += 1

            # Display progress
            elapsed_time = time.time() - start_time
            avg_time_per_game = elapsed_time / game_number if game_number > 0 else 0
            time_remaining = avg_time_per_game * (total_games - game_number)
            print(
                f"Analyzing game {game_number} out of {total_games} "
                f"(Elapsed: {elapsed_time:.2f}s, Estimated: {time_remaining:.2f}s)..."
            )
            
            analysis = analyze_game(game, suspicious_player)
            if analysis:
                results.append(analysis)

    # Convert results to a DataFrame for better analysis
    df = pd.DataFrame(results)
    return df


def evaluate_cheating_probability(df):
    """Evaluate cheating probability based on robust patterns."""
    high_engine_match_games = df[df["EngineMatchRate"] > 65]
    avg_engine_match_rate = df["EngineMatchRate"].mean()
    avg_move_time = df["AverageMoveTime"].mean()
    brilliant_to_blunder = df["BrilliantToBlunder"].sum()
    
    probability = 0

    # Adjusted thresholds
    if avg_engine_match_rate > 65:
        probability += 30

    if len(high_engine_match_games) / len(df) > 0.2:
        probability += 30

    if brilliant_to_blunder > 2:  # More than 2 instances of brilliant-to-blunder patterns
        probability += 20

    return min(probability, 100)


def categorize_cheating(probability):
    """Categorize the cheating suspicion level based on probability."""
    if probability >= 70:
        return "Cheating"
    elif 40 <= probability < 70:
        return "Probably Cheating"
    else:
        return "Not at All Cheating"

def plot_time_graph(df):
    """Plot time usage per move for all games."""
    for index, row in df.iterrows():
        plt.plot(row["MoveTimes"], label=f"Game {index + 1}")
    plt.xlabel("Move Number")
    plt.ylabel("Time Spent (seconds)")
    plt.title("Time Spent per Move")
    plt.legend()
    plt.show()

def main():
    # Input handling
    pgn_file_path = input("Enter the path to the PGN file: ").strip()
    suspicious_player = input("Enter the username of the suspicious player: ").strip()
    
    if not os.path.exists(pgn_file_path):
        print(f"File not found: {pgn_file_path}")
        return

    df = analyze_pgn(pgn_file_path, suspicious_player)
    if df.empty:
        print(f"No games found for player: {suspicious_player}")
        return

    # Display analysis
    print("\nGame Analysis:")
    print(df)

    # Evaluate cheating probability
    probability = evaluate_cheating_probability(df)
    category = categorize_cheating(probability)
    print(f"\nCheating Probability for {suspicious_player}: {probability}% ({category})")

    # Plot time graph
    plot_time_graph(df)

if __name__ == "__main__":
    main()
