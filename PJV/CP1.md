# CP1: Project Vision – Online Chess
## Chosen Project Topic

Development of a desktop application for the classic strategic board game Chess in Java using the JavaFX framework, with an emphasis on implementing a client-server architecture and utilizing polymorphism in the game logic design.

## Executive Summary

The goal of this project is to create a fully playable digital adaptation of the Chess. The application will offer the user the ability to play against another player on the same device (local), or over the network against another user. The main programming added value of the project will be the easy game management using a `GameController`, the use of polymorphism for the moves of individual pieces, and a multi-threaded architecture where the server can manage multiple game sessions (`GameSession`) simultaneously. The game will feature a clear graphical user interface that intuitively guides players through the entire match.

## Detailed Description of Features
### Game Flow and Objective

The game is played on a square 8x8 board. The game fully implements standard FIDE rules:

- **Standard moves**: Each piece moves according to its specific rules.

- **Castling**: Short and long, prohibited if the king or rook has already moved, or if the involved squares are under attack.

- **Pawn promotion**: A pawn reaching the last rank is promoted to a queen, rook, bishop, or knight, based on the player's choice.

- **Check and Checkmate**: Detection of threats to the king and prevention of moves that would endanger the king. Checkmate ends the game.

- **Draw and Stalemate**: Automatic detection of stalemate (the player has no legal moves but is not in check) and the option to offer/accept a draw from the opponent.

*(Note: The En passant rule and the 50-move rule will be implemented only if time permits).*

### Network and Game Modes

- Multiplayer (main mode)

- Client connects to the server using an IP address and port

- Server pairs players into a single game session (`GameSession`)

- Each session runs separately → utilization of multiple threads

#### Communication and its Protocol:

- Java Sockets

- Transfer of objects such as moves, game state

```
[Client]                        [Server]
   |--- ConnectMessage --------->|
   |<-- WaitingForOpponent ------|
   |                             | (second player connects)
   |<-- GameStartMessage --------|
   |                             |
   |--- MoveMessage ------------>|
   |<-- GameStateMessage --------|  (or ErrorMessage)
   |<-- GameStateMessage --------|  (opponent's move)
   |                             |
   |--- ResignMessage ---------->|
   |<-- GameOverMessage ---------|
```

#### Game Modes and Player Characteristics

The application will run in two basic modes:

- **Multiplayer (Client-Server)**: One player hosts a server (`ChessServer`), which runs in the background and accepts connections. Once two clients (`NetworkClient`) connect, an isolated `GameSession` is created, which communicates with players via the `ClientHandler` class and sends them messages (`Message`) about the game state.

- **Local game**: Two players (`Player`) play on a single computer, taking turns, managed directly by a local instance of `GameController`.

### Game Board and Elements

The fundamental element is the `Board` representing a grid containing instances of pieces. All pieces inherit from the abstract class `Piece` and implement their own `getLegalMoves()` method:

- **King (`King`)**: 1 square in any direction + castling.

- **Queen (`Queen`)**: Any number of squares horizontally, vertically, or diagonally.

- **Rook (`Rook`)**: Any number of squares horizontally or vertically.

- **Bishop (`Bishop`)**: Any number of squares diagonally.

- **Knight (`Knight`)**: Moves in an "L" shape.

- **Pawn (`Pawn`)**: 1 square forward, captures diagonally + promotion.

### Loading and Saving Mechanism

The user will be able to pause a local game at any time and save its state to disk in JSON format. The file will store the current layout of all pieces on the board, move history, and the current turn state. Upon launching the application, the saved file can be selected via a native `FileChooser` to resume the game in progress.

### Controls and UI (JavaFX)
#### Main Game Screen

The main window (`ChessApp`) will be divided into two parts:

- **Left/Main Section (`BoardView`)**: The game board itself. Upon clicking a player's own piece, the game will graphically highlight all target squares to which a valid move can be made in that turn (visualization of Move).

- **Right Panel**: Will display whose turn it is, move history, game state (`GameStatus`), and buttons to resign or offer a draw:

```
┌──────────────────────────────────────────────┐
│           CHESS - Multiplayer                │
├─────────────────────┬────────────────────────┤
│                     │  Player: White (You)   │
│                     │                        │
│                     │────────────────────────│
│    Chessboard       │  Move History:         │
│    8x8              │  1. e4  e5             │
│    (interactive)    │  2. Nf3 Nc6            │
│                     │  3. Bb5 ...            │
│                     │────────────────────────│
│                     │  [Resign]  [Draw]      │
│                     │  Opponent: Black       │
│                     │  Time: 08:15           │
├─────────────────────┴────────────────────────┤
│  Status: White's turn                        │
└──────────────────────────────────────────────┘
```

#### Start Screen/ Lobbby

```
┌────────────────────────────────┐
│     ♚  CHESS  ♚                │
│                                │
│   [ Local Game ]               │
│   [ Connect to Server ]        │
│   [ Settings ]                 │
│                                │
│   ┌────────────────────────┐   │
│   │ IP:   [192.168.1.1  ]  │   │
│   │ Port: [12345        ]  │   │
│   │ Name: [Martin       ]  │   │
│   │ [   Connect    ]       │   │
│   └────────────────────────┘   │
│                                │
└────────────────────────────────┘
```
