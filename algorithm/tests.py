import re
import subprocess
import time
import unittest


def find_numbers_in_file(file_path):
    """
    Funkcja sprawdzająca, czy w pliku znajdują się liczby i je zwracająca.
    :param file_path: Ścieżka do pliku
    :return: Lista liczb (jako stringi)
    """
    numbers = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                numbers.extend(re.findall(r'\d+', line))
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    return numbers


class TestFindNumbersInFile(unittest.TestCase):
    def setUp(self):
        """
        Przygotowanie tymczasowego pliku do testów.
        """
        try:
            self.mpi_process = subprocess.Popen(
                ["mpiexec", "-n", "4", "python", "./main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Poczekaj 10 sekund, aby proces miał czas na działanie
            time.sleep(5)
        except subprocess.TimeoutExpired:
            # Jeśli proces trwa za długo, zostanie zakończony
            self.mpi_process.terminate()

        self.test_file = '../log/cs.txt'

    def test_find_numbers(self):
        """
        Test sprawdzający, czy liczby są poprawnie znajdowane w pliku.
        """
        expected_numbers = ['0', '1', '2', '3']
        numbers = find_numbers_in_file(self.test_file)

        split_numbers = [''.join(numbers[i:i + 4]) for i in range(0, len(numbers), 4)]

        for substring in split_numbers:
            if len(substring) < 4:
                for char in substring:
                    self.assertIn(char, expected_numbers)
            else:
                for expected in expected_numbers:
                    self.assertIn(expected, substring)


if __name__ == '__main__':
    unittest.main()
