# Safari na Wildzie 

### Wersja python
Aby odpalić kod należy przejść do folderu algorithm i wywołać komendę:

```commandline
mpiexec -n x python .\main.py
```

gdzie x to liczba procesów.

### Wersja c++
Aby odpalić kod należy przejść do folderu c++ i wywołać komendę:

**Kompilacja:**
```commandline
mpic++ -o main main.cpp listener.cpp sender.cpp communication.cpp -lpthread
```

**Odpalenie:**
```commandline
mpirun -np x ./main
```

gdzie x to liczba procesów.