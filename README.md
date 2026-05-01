# Chesser
A chess game analyzer based on stockfish's analysis.


## Requirements

- Python3
- StockFish (https://stockfishchess.org/download)

## Installation

- `git clone git@github.com:rodrigo-svguedes/chesser.git && cd chesser`
- `export STOCKFISH_PATH="your_stockfish_path_here"`
- `make create-env`
- `make install`
- `make create-db`

It is also possible to set your own polyglot book by setting the environment variable: POLYGLOT_BOOK_PATH.  
By default, the polyglot book is the Performance.bin included on assets.

## Testing

- `make test`

## Running (development mode)

- `make run`

## Usage

- http://localhost:5000/board
