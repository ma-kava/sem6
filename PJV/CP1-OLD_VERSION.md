Zvolené téma práce
Vývoj desktopové aplikace pro klasickou strategickou deskovou hru Reversi v jazyce Java s využitím frameworku JavaFX, s důrazem na implementaci různých úrovní umělé inteligence.

Manažerské shrnutí
Cílem tohoto projektu je vytvořit plně hratelnou digitální adaptaci populární deskové hry Reversi. Aplikace nabídne uživateli možnost hrát proti počítači, případně proti dalšímu hráči na stejném zařízení. Hlavní přidanou hodnotou projektu po programátorské stránce bude objektový návrh umožňující snadné zapojení různých strategií umělé inteligence – od triviálních (náhodný tah) až po pokročilé algoritmy prohledávání stavového prostoru (Minimax s alfa-beta prořezáváním). Hra bude obsahovat přehledné grafické uživatelské rozhraní, které intuitivně provede hráče celým zápasem, včetně zobrazení statistik a možnosti hru uložit a později načíst.

Podrobný popis funkcionalit
Průběh a cíl hry
Hraje se na čtvercové desce o velikosti 8x8 polí.

Na začátku hry jsou ve středu desky křížem umístěny dva černé a dva bílé kameny. Černý hráč vždy začíná.

Hráč na tahu musí umístit svůj kámen na prázdné pole tak, aby v horizontálním, vertikálním nebo diagonálním směru "obklíčil" souvislou řadu soupeřových kamenů svými dvěma kameny (nově položeným a jedním již existujícím).

Všechny takto obklíčené soupeřovy kameny se otočí na barvu hráče, který tah provedl.

Pokud hráč nemá žádný platný tah, automaticky tah přeskočí.

Cíl hry: Zápas končí, když je deska zcela zaplněna, nebo když ani jeden z hráčů nemůže provést platný tah. Vítězí hráč, který má na konci hry na desce více kamenů své barvy. V případě shody nastává remíza.

Herní módy a vlastnosti hráčů
Ve hře se budou moci utkat jakékoliv kombinace entit (Člověk vs. AI, Člověk vs. Člověk, AI vs. AI pro testovací účely). Umělá inteligence bude mít na výběr z několika úrovní obtížnosti:

Lehká (Random AI): Náhodně vybere jeden z aktuálně platných tahů. Slouží jako základní testovací protivník.

Střední (Heuristic / Greedy AI): Ohodnocuje herní desku na základě vah políček (např. rohy mají nejvyšší kladnou hodnotu, pole těsně vedle rohů naopak zápornou, jelikož nahrávají soupeři). Algoritmus vybere tah s nejvyšším okamžitým ziskem bodů.

Těžká (Minimax AI): Využívá algoritmus Minimax s alfa-beta prořezáváním k simulaci vývoje hry několik tahů dopředu (hloubka prohledávání bude nastavitelná nebo pevně daná, např. 4 tahy).

Popis herní desky a prvků
Kameny: Mají pouze dvě barvy (černá a bílá). Kámen po položení na desku už nikdy nemění svou pozici, mění pouze svou barvu (stav).

Políčka (Tiles): Každé políčko na desce může nabývat jednoho ze tří stavů: PRÁZDNÉ, OBSAZENÉ_ČERNOU, OBSAZENÉ_BÍLOU.

Nápověda (Highlighting): Pokud je na tahu lidský hráč, hra mu graficky (např. poloprůhledným kroužkem) zvýrazní všechna políčka, na která může v daném kole platně táhnout.

Ovládání a uživatelské rozhraní
Hra je ovládána myší z top-down (2D) pohledu.

Hlavní okno bude rozděleno na dvě části:

Levá/Hlavní část: Samotná herní deska, reagující na kliknutí levým tlačítkem myši (pokus o položení kamene).

Pravý panel: Ovládací prvky a statistiky. Bude zobrazovat:

Kdo je aktuálně na tahu.

Průběžné skóre (počet černých a bílých kamenů).

Tlačítka pro Uložit hru, Načíst hru, Nová hra a případně Zpět (Undo).

Před začátkem nové hry se zobrazí jednoduché dialogové okno s výběrem typu hráčů (Člověk/AI) a volbou obtížnosti.

Způsob načítání a ukládání
Uživatel bude moci hru kdykoliv pozastavit a její stav uložit na disk do formátu JSON.

Do souboru se bude ukládat: aktuální rozložení všech kamenů na desce, informace o tom, který hráč je na tahu, a zvolené typy hráčů (aby hra např. věděla, že má po načtení nechat táhnout Minimax).

Při spuštění aplikace nebo z pravého panelu půjde uložený soubor vybrat přes nativní FileChooser a rozehranou partii načíst. Hra bude ošetřena proti načtení poškozeného nebo nevalidního souboru.