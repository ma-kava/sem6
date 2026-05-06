# CP1: Vize projektu – Online šachy
## Zvolené téma práce

Vývoj desktopové aplikace pro klasickou strategickou deskovou hru Šachy v jazyce Java s využitím frameworku JavaFX, s důrazem na implementaci klient-server architektury a využití polymorfismu v návrhu herní logiky.

## Manažerské shrnutí

Cílem tohoto projektu je vytvořit plně hratelnou digitální adaptaci populární deskové hry Šachy. Aplikace nabídne uživateli možnost hrát proti dalšímu hráči na stejném zařízení (lokální hot-seat mód), nebo po síti proti jinému uživateli. Hlavní přidanou hodnotou projektu po programátorské stránce bude objektový návrh umožňující snadné řízení hry pomocí `GameControlleru`, využití polymorfismu pro tahy jednotlivých figurek a vícevláknová síťová architektura, kde server dokáže spravovat více herních relací (`GameSession`) současně. Hra bude obsahovat přehledné grafické uživatelské rozhraní, které intuitivně provede hráče celým zápasem.

## Podrobný popis funkcionalit
### Průběh a cíl hry

Hraje se na čtvercové desce o velikosti 8x8 polí. Hra plně implementuje standardní pravidla FIDE:

- **Standardní tahy**: Každá figurka se pohybuje podle svých specifických pravidel.

- **Rošáda**: Krátká i dlouhá, zakázána pokud král nebo věž již táhly, nebo pokud jsou dotčená pole napadena.

- **Proměna pěšce**: Pěšec na poslední řadě se promění v dámu, věž, střelce nebo koně dle volby hráče.

- **Šach a Mat**: Detekce napadení krále a znemožnění tahů, které by krále ohrozily. Mat ukončuje hru.

- **Remíza a Pat**: Automatická detekce patu (hráč nemá legální tah, ale není v šachu) a možnost nabídnout/přijmout remízu soupeřem.

*(Pozn.: Pravidlo En passant a pravidlo 50 tahů budou implementována pouze v případě dostatku času).*

### Síť a herní módy

- Multiplayer (hlavní režim)
- Klient se připojuje na server pomocí IP adresy a portu
- Server páruje hráče do jedné herní relace (`GameSession`)
- Každá relace běží odděleně → využití více vláken

#### Komunikace a její protokol:

- Java Sockets
- Přenos objektů jako např. tahy, stav hry

```
[Klient]                        [Server]
   |--- ConnectMessage --------->|
   |<-- WaitingForOpponent ------|
   |                             | (druhý hráč se připojí)
   |<-- GameStartMessage --------|
   |                             |
   |--- MoveMessage ------------>|
   |<-- GameStateMessage --------|  (nebo ErrorMessage)
   |<-- GameStateMessage --------|  (tah soupeře)
   |                             |
   |--- ResignMessage ---------->|
   |<-- GameOverMessage ---------|
```

### Herní módy a vlastnosti hráčů

Aplikace poběží ve dvou základních režimech:

- **Multiplayer (Klient-Server)**: Jeden hráč založí server (`ChessServer`), který běží na pozadí a přijímá připojení. Po připojení dvou klientů (`NetworkClient`) se vytvoří izolovaná `GameSession`, která komunikuje s hráči pomocí třídy `ClientHandler` a posílá jim zprávy (`Message`) o stavu hry.

- **Lokální hra**: Dva hráči (`Player`) hrají na jednom počítači, střídají se po tazích a řídí je přímo lokální instance `GameControlleru`.

### Herní deska a prvky

Základním prvkem je `Board` představující mřížku obsahující instance figurek. Všechny figurky dědí z abstraktní třídy `Piece` a implementují vlastní metodu `getLegalMoves()`:

- **Král (`King`)**: 1 pole libovolným směrem + rošáda.

- **Dáma (`Queen`)**: Libovolný počet polí vodorovně, svisle nebo diagonálně.

- **Věž (`Rook`)**: Libovolný počet polí vodorovně nebo svisle.

- **Střelec (`Bishop`)**: Libovolný počet polí diagonálně.

- **Kůň (`Knight`)**: Skok do tvaru "L".

- **Pěšec (`Pawn`)**: 1 pole vpřed, braní diagonálně + proměna.

### Způsob načítání a ukládání

Uživatel bude moci lokální hru kdykoliv pozastavit a její stav uložit na disk do formátu JSON. Do souboru se bude ukládat aktuální rozložení všech figurek na desce, historie tahů a aktuální stav, kdo je na tahu. Při spuštění aplikace půjde uložený soubor vybrat přes nativní `FileChooser` a rozehranou partii načíst.

## Ovládání a UI (JavaFX)

### Hlavní herní obrazovka

Hlavní okno (`ChessApp`) bude rozděleno na dvě části:

- **Levá/Hlavní část (`BoardView`)**: Samotná herní deska. Po kliknutí na vlastní figurku hra graficky zvýrazní všechna cílová pole, na která lze v daném kole platně táhnout (vizualizace `Move`).

- **Pravý panel**: Bude zobrazovat, kdo je aktuálně na tahu, historii tahů, stav hry (`GameStatus`) a tlačítka pro vzdání se nebo nabídku remízy:

```
┌──────────────────────────────────────────────┐
│           CHESS - Multiplayer                │
├─────────────────────┬───────────────────────-┤
│                     │  Hráč: bílý (vy)       │
│                     │                        │
│                     │───────────────────────-│
│    Šachovnice       │  Historie tahů:        │
│    8x8              │  1. e4  e5             │
│    (interaktivní)   │  2. Nf3 Nc6            │
│                     │  3. Bb5 ...            │
│                     │───────────────────────-│
│                     │  [Vzdát]  [Remíza]     │
│                     │  Soupeř: černý         │
│                     │  Čas: 08:15            │
├─────────────────────┴───────────────────────-┤
│  Status: Na tahu je bílý                     │
└─────────────────────────────────────────────-┘
```

### Úvodní obrazovka / Lobby

```
┌────────────────────────────────┐
│     ♚  CHESS  ♚                │
│                                │
│   [ Lokální hra ]              │
│   [ Připojit se k serveru ]    │
│   [ Nastavení ]                │
│                                │
│   ┌────────────────────────┐   │
│   │ IP:   [192.168.1.1  ]  │   │
│   │ Port: [12345        ]  │   │
│   │ Jméno:[Martin       ]  │   │
│   │ [   Připojit   ]       │   │
│   └────────────────────────┘   │
│                                │
└────────────────────────────────┘
```