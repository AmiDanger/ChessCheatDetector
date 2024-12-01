# ChessCheatDetector

![Chess Analysis](https://img.shields.io/badge/Chess-Analysis-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**ChessCheatDetector** is a Python-based tool designed to detect suspicious play in chess games. It leverages the Stockfish engine to analyze PGN files, evaluating patterns like engine match rates, brilliant-to-blunder sequences, critical move accuracy, and move times. The tool categorizes behavior into **Cheating**, **Probably Cheating**, or **Not at All Cheating** based on a robust probability-based detection algorithm.

---

## **Features**

- **Engine Match Analysis**: Measures how closely a player's moves align with Stockfish's recommendations.
- **Brilliant and Blunder Patterns**: Detects alternating sequences of brilliance and sudden blunders.
- **Critical Move Accuracy**: Tracks performance in key positions (checks, captures, tactical situations).
- **Move Time Analysis**: Identifies suspiciously fast or uniform move times.
- **Progress Tracker**: Displays real-time progress and estimated time remaining during analysis.
- **Visualization**: Generates a move time graph for better insights.

---

## **Requirements**

### **Software**
- Python 3.8 or higher
- Stockfish Chess Engine

### **Python Libraries**
Install the required Python libraries using pip:
```bash
pip install python-chess pandas matplotlib
