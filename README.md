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
T - liczba procesów

P - liczba zasobów

G - wielkość zasobu

* W jednym momencie z zasobu może korzystać G procesów ?

Opcje:

1. Proces musi uzyskać co najmniej G RELAY'ów
2. Proces musi uzyskać 