# Vize projektu: Multiplayer šachy (klient-server)

## Zvolené téma

Desktopová šachová aplikace v jazyce Java (≥ 21) s využitím JavaFX a Maven. Důraz je kladen na klient-server architekturu, práci s více vlákny a objektový model s polymorfismem pro logiku figurek.

## Manažerské shrnutí

Výsledkem bude plně funkční šachová hra pro dva hráče přes síť (TCP sockety). Klíčovým architektonickým principem je oddělení herní logiky od prezentační vrstvy a implementace serveru, který spravuje libovolný počet souběžných herních relací.

Projekt ukazuje pokročilou práci s vlákny (každá relace ve vlastním vlákně, JavaFX `Task` / `Service` pro asynchronní síťovou komunikaci na klientovi), návrhové vzory (Strategy, Observer, Factory) a principy OOP – abstrakci a polymorfismus při návrhu figurek. GUI je vytvořeno v JavaFX programaticky (bez Scene Builderu).

---

## Funkcionalita

### 1. Pravidla hry

Hra implementuje kompletní pravidla FIDE šachů:

| Pravidlo | Popis |
|---|---|
| Standardní tahy | Každá figurka se pohybuje podle svých pravidel (viz sekce Figurky) |
| Rošáda | Krátká i dlouhá; zakázána pokud král nebo věž již táhly, pole jsou napadena, nebo mezi nimi stojí figurka |
| En passant | Braní mimochodem pěšce, který v předchozím tahu postoupil o dvě pole |
| Proměna pěšce | Pěšec na poslední řadě se promění v dámu, věž, střelce nebo koně (hráč volí v dialogu) |
| Šach | Detekce, zda je král napaden; hráč musí šach odvrátit |
| Mat | Král je v šachu a neexistuje legální tah → konec hry |
| Pat | Hráč na tahu nemá legální tah, ale není v šachu → remíza |
| Remíza dohodou | Hráč může nabídnout remízu, soupeř přijme nebo odmítne |
| Vzdání | Hráč se může kdykoli vzdát |
| Pravidlo 50 tahů | Automatická remíza po 50 tazích bez braní a bez tahu pěšcem |
| Nedostatečný materiál | Remíza pokud ani jeden hráč nemá dost materiálu k matu (K vs K, K+S vs K, K+J vs K) |

### 2. Herní režimy

#### 2.1 Multiplayer (hlavní režim)

- Klient se připojuje na server zadáním IP adresy a portu.
- Server páruje dva připojené hráče do jedné herní relace (`GameSession`).
- Každá relace běží ve vlastním vlákně na serveru.
- Komunikace probíhá přes Java Sockets přenosem serializovaných zpráv (vlastní protokol):
  - **Klient → Server:** `MoveMessage` (tah), `ResignMessage` (vzdání), `DrawOfferMessage` (nabídka remízy), `DrawResponseMessage` (odpověď na remízu)
  - **Server → Klient:** `GameStateMessage` (stav šachovnice po validovaném tahu), `GameOverMessage` (výsledek), `ErrorMessage` (neplatný tah), `DrawOfferReceivedMessage`

#### 2.2 Lokální hra (hot-seat)

- Dva hráči u jednoho počítače, střídají se po tazích.
- Nevyžaduje síťové připojení, logika běží lokálně.
- Slouží především k testování a pro případ, kdy není server dostupný.

### 3. Šachové hodiny (volitelné)

- Při zakládání hry na serveru lze zvolit časový limit (např. 5, 10, 15 minut na hráče).
- Hodiny běží na server-side a jsou synchronizovány s klientem.
- Po vypršení času hráč prohrává.
- Hodiny jsou realizovány pomocí `ScheduledExecutorService` na serveru a `AnimationTimer` nebo `Timeline` v JavaFX na klientovi pro plynulé zobrazení.

### 4. Figurky

Abstraktní třída `Piece` definuje společné vlastnosti a interface pro generování tahů. Konkrétní figurky dědí z `Piece` a implementují vlastní logiku pohybu:

| Figurka | Třída | Pohyb |
|---|---|---|
| Král | `King` | 1 pole libovolným směrem + rošáda |
| Dáma | `Queen` | Libovolný počet polí vodorovně, svisle nebo diagonálně |
| Věž | `Rook` | Libovolný počet polí vodorovně nebo svisle |
| Střelec | `Bishop` | Libovolný počet polí diagonálně |
| Kůň | `Knight` | Skok do tvaru "L" (2+1 pole), přeskakuje figurky |
| Pěšec | `Pawn` | 1 pole vpřed (2 z výchozí pozice), braní diagonálně + en passant + proměna |

Každá figurka:
- Zná svou barvu (`Color.WHITE` / `Color.BLACK`) a aktuální pozici.
- Poskytuje metodu `getLegalMoves(Board board)` vracející seznam legálních tahů (s ohledem na šach).
- Poskytuje metodu `getPseudoLegalMoves(Board board)` pro tahy bez kontroly šachu (pro interní výpočty).
- Má příznak `hasMoved` pro rošádu a pravidla pěšce.

### 5. Šachovnice a herní logika

- `Board` – reprezentace jako 2D pole `Piece[8][8]` (null = prázdné pole).
- `GameLogic` – validace tahů, detekce šachu/matu/patu, provádění tahů, undo (pro interní výpočty).
- `Move` – datová třída: zdrojové pole, cílové pole, typ tahu (normální, rošáda, en passant, proměna), braná figurka.
- `MoveHistory` – seznam provedených tahů s podporou algebraické notace (např. `Nf3`, `O-O`, `exd5`).

---

## GUI (JavaFX)

### Hlavní herní obrazovka

Okno aplikace je rozděleno na dvě části:

```
┌─────────────────────────────────────────────┐
│           CHESS - Multiplayer                │
├─────────────────────┬───────────────────────-┤
│                     │  Hráč: bílý (vy)       │
│                     │  Čas: 09:42            │
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
│     ♚  CHESS  ♚               │
│                                │
│   [ Lokální hra ]              │
│   [ Připojit se k serveru ]    │
│   [ Nastavení ]                │
│                                │
│   ┌────────────────────────┐   │
│   │ IP:   [192.168.1.1  ]  │   │
│   │ Port: [12345        ]  │   │
│   │ Jméno:[Martin       ]  │   │
│   │ [   Připojit   ]      │   │
│   └────────────────────────┘   │
│                                │
└────────────────────────────────┘
```

### Popis GUI prvků

- **Šachovnice** – vytvořena programaticky jako `GridPane` se střídajícími se barvami polí. Figurky jsou zobrazeny jako Unicode znaky nebo SVG obrázky. Pole reagují na kliknutí myší.
- **Zvýraznění tahů** – po kliknutí na figurku se legální cílová pole zvýrazní (zeleným kruhem pro volná pole, červeným rámečkem pro braní).
- **Animace tahu** – figurka se plynule přesune na cílové pole (`TranslateTransition`).
- **Dialog proměny pěšce** – modální okno s výběrem figurky (dáma, věž, střelec, kůň).
- **Vedlejší panel** – zobrazuje informace o hráčích, hodiny, historii tahů v algebraické notaci a tlačítka pro vzdání / nabídku remízy.
- **Stavový řádek** – zobrazuje aktuální stav hry (na tahu, šach, mat, remíza, odpojení soupeře).

### Ovládání

| Akce | Ovládání |
|---|---|
| Výběr figurky | Kliknutí levým tlačítkem myši na figurku |
| Provedení tahu | Kliknutí na zvýrazněné cílové pole |
| Zrušení výběru | Kliknutí na jiné pole / pravé tlačítko myši |
| Vzdání | Kliknutí na tlačítko "Vzdát" + potvrzení dialogem |
| Nabídka remízy | Kliknutí na tlačítko "Remíza" |

---

## Síťová architektura

### Server

- Hlavní vlákno naslouchá na zadaném portu (`ServerSocket`).
- Po připojení dvou klientů vytvoří novou `GameSession` v novém vlákně.
- `GameSession` drží referenci na `Board`, oba hráče a řídí průběh hry.
- Server validuje tahy – klient je "tenký" (nemůže podvádět).
- Server podporuje více souběžných her (každá ve vlastním vlákně).

### Klient

- Po připojení běží na pozadí `ReaderThread` (nebo JavaFX `Task`), který naslouchá zprávám ze serveru.
- UI vlákno (JavaFX Application Thread) zobrazuje stav hry.
- Komunikace mezi síťovým vláknem a UI vláknem probíhá pomocí `Platform.runLater()`.

### Protokol komunikace

Zprávy jsou serializované Java objekty implementující rozhraní `Message`:

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

---

## Ukládání a načítání

- Stav rozehrané hry (lokální režim) lze uložit do souboru ve formátu JSON.
- Uloženy budou:
  - Pozice všech figurek na šachovnici
  - Hráč na tahu
  - Příznaky rošády a en passant
  - Historie tahů
  - Zbývající čas (pokud jsou hodiny aktivní)
- Soubor se ukládá do zvoleného umístění přes `FileChooser` dialog.
- Při spuštění aplikace lze načíst uloženou hru a pokračovat.
- Pro multiplayer: server může ukládat dokončené hry do logu (výsledek, seznam tahů) ve formátu JSON.

---

## Vlákna a souběžnost

Projekt aktivně využívá vláknový model:

| Vlákno | Technologie | Účel |
|---|---|---|
| JavaFX Application Thread | JavaFX | Vykreslování GUI, reakce na uživatelský vstup |
| Síťový listener (klient) | `javafx.concurrent.Task` | Naslouchání zprávám ze serveru |
| Server accept loop | `Thread` | Přijímání nových připojení |
| GameSession vlákno | `Thread` / `ExecutorService` | Řízení jedné herní relace |
| Šachové hodiny | `ScheduledExecutorService` | Odpočítávání času hráčů |

Synchronizace UI: veškeré aktualizace GUI z jiných vláken probíhají přes `Platform.runLater()`.

---

## Logování

- Použit framework **SLF4J** s implementací **Logback**.
- Logy zahrnují: připojení/odpojení hráčů, provedené tahy, chyby validace, výjimky.
- Úroveň logování se ovládá:
  - **Parametrem při spuštění:** `-Dlog.level=DEBUG` (nebo `INFO`, `WARN`, `ERROR`)
  - **V GUI:** přepínač v nastavení umožní zapnout/vypnout podrobné logování za běhu (změna úrovně Logback programaticky).
- Logy se zapisují do konzole a volitelně do souboru `chess.log`.

---

## Testování

- Testovací framework: **JUnit 5**.
- Pokryté oblasti:
  - **Validace tahů** – testy pro každý typ figurky (legální/nelegální tahy, speciální tahy).
  - **Detekce šachu, matu, patu** – ověření na konkrétních pozicích.
  - **Rošáda a en passant** – edge-case testy.
  - **Proměna pěšce** – test proměny na všechny typy figurek.
  - **Serializace/deserializace** – uložení a načtení stavu hry.
  - **Pravidlo 50 tahů a nedostatečný materiál** – testy remízových podmínek.
- Testy se spouští příkazem `mvn test`.

---

## Co projekt NEBUDE obsahovat

- **AI soupeř** – hra je čistě pro dva lidské hráče (human vs human).
- **Online žebříček / ELO rating** – není implementován systém hodnocení hráčů.
- **Databáze** – ukládání probíhá výhradně do souborů (JSON).
- **Registrace a autentizace** – hráč se identifikuje pouze přezdívkou.
- **Chat** – komunikace mezi hráči není součástí projektu.
- **Podpora jiných her** – aplikace je specializovaná výhradně na šachy.
- **3D grafika** – šachovnice je pouze 2D.
- **Replay / přehrávání her** – uložené hry nelze krokovat zpět (pouze načíst a pokračovat).

---

## Technologie a nástroje

| Technologie | Použití |
|---|---|
| Java ≥ 21 | Jazyk projektu |
| Maven | Správa závislostí a build |
| JavaFX | GUI framework |
| Java Sockets | Síťová komunikace |
| SLF4J + Logback | Logování |
| JUnit 5 | Unit testy |
| JSON (Gson/Jackson) | Serializace stavu hry |
| Git + GitLab | Verzování kódu |

---

## Shrnutí požadavků vs. odevzdání

| Požadavek | Jak je splněn |
|---|---|
| Java ≥ 21, Maven | Ano |
| Git progress | Průběžné commity obou členů |
| JavaFX GUI (programaticky) | Šachovnice (`GridPane`) bez Scene Builderu |
| Vlákna | `Task`/`Service`, `ExecutorService`, `ScheduledExecutorService` |
| Unit testy | JUnit 5 – validace tahů, herní logika |
| Loggery | SLF4J + Logback, přepínatelné parametrem a v GUI |
| Ukládání stavu | JSON soubor přes `FileChooser` |
| Javadoc | Všechny netriviální public prvky |
| Komentáře a jazyk | Kód a komentáře v angličtině |
| Dokumentace | Wiki – uživatelský manuál + technická dokumentace |