Jebać Danileckiego... Pomyśleli wszyscy

---

Normalny algorytm Lamporta:

````
INICJALIZACJA:
Dla każdego procesu P_i:
    Ustaw licznik czasu L_i na 0

WYSYŁANIE REQUESTU M PRZEZ PROCES P_i DO PROCESU P_j:
1. L_i = L_i + 1
2. Dołącz znacznik czasowy L_i do REQUESTU M
3. Wyślij REQUEST M do P_j

OTRZYMANIE REQUESTU PRZEZ PROCES P_j:
1. Odbierz znacznik czasowy T_m z wiadomości M
2. L_j = max(L_j, T_m) + 1
3. If P_j chce uzyskać dostęp do sekcji krytycznej i P_i ma mniejszy priorytet: Wait; Else: wyślij REPLAY(L_j) do P_i;
````

---
T - liczba procesów ( minimum 2*G )

G - wielkość grupy

P - liczba grup

1. Początkowy schemat wygląda tak samo jak w zwykłym zegarze lamporta + każdy proces ma kolejkę innych procesów które
   wysłały do niego REQUIRE.
2. Jeśli proces otrzyma T-G ACK to może wejść do sekcji krytycznej. Siedząc w środku zbiera pierwsze G - 1 procesów od
   których dostał REQUIRE (Jeśli jeszcze nie ma tylu to czeka ) i wysyła do nich AQUIRE. Procesy odpowiadają ACK (jeśli
   jest konflikt i 2 procesy chcą utworzyć grupę z tym samym procesem to ten który był zaproszony dołącza do grupy z
   liderem który ma większe ID). Jeśli proces odrzuca AQUIRE to odpowiada komunikatem REJECT. Wtedy liter wysyła AQUIRE
   do następnego z kolejki.
3. Gdy lider dostanie G-1 ACK to wycieczka rusza i w trakcie niej może nastąpić randomowe pobicie uczestnika, po którym
   trafia do szpitala. Z punktu kodu będzie to skutkowało tylko wyświetleniem komunikatu i ewentualnie odczekaniem
   randomowego czasu do wyświetlenia, że wrócił ze szptala.
4. Po zakończeniu wycieczki wysyłany jest komunikat RELEASE do wszystkich innych procesów, że zwolniono sekcję
   krytyczną.
