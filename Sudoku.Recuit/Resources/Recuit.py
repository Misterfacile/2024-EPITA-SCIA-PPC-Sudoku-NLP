import random
import numpy as np


def blocks_index():
    """
    Generate the indexes of the 3x3 sub-grids
    """
    blocks = []
    for row in range(9):
        row_start = 3 * (row % 3)
        column_start = 3 * (row // 3)
        block = [
            [x, y]
            for x in range(row_start, row_start + 3)
            for y in range(column_start, column_start + 3)
        ]
        blocks.append(block)
    return np.array(blocks)


class Solver:
    """
    The Solver class is a model for solving a sudoku using the Simulated Annealing algorithm.
    """

    def __init__(self, grid: np.ndarray, cooling_rate: float):
        self.basic_grid = grid
        self.index = blocks_index()
        self.grid = self.random_matrix(grid)
        self.grid_score = self.compute_error(self.grid)

        self.pre_filled_indexes = [tuple(l) for l in np.argwhere(grid != 0)]
        self.temperature = self.init_temperature()
        self.limit = np.count_nonzero(grid == 0)

        self.cooling_rate = cooling_rate

    def compute_error(self, matrix: np.ndarray):
        """
        Calculate the number of errors in the sudoku.
        An error is defined as the missing values in a row or a column.
        """
        nb_error = 0
        rows = [set() for _ in range(9)]
        cols = [set() for _ in range(9)]
        for i in range(9):
            for j in range(9):
                val = matrix[i][j]
                nb_error += (val in rows[i]) + (val in cols[j])
                rows[i].add(val)
                cols[j].add(val)
        return nb_error

    def random_matrix(self, sudoku: np.ndarray) -> np.ndarray:
        """
        Create a matrix by filling empty cells, filled so each block of the sudoku contains random unique values from 1 to 9.
        """
        result = sudoku.copy()
        for blocks in self.index:
            L = np.arange(1, 10)
            np.random.shuffle(L)
            for block in blocks:
                if sudoku[block[0]][block[1]] != 0:
                    L = L[L != sudoku[block[0]][block[1]]]

            for block in blocks:
                if len(L) != 0 and result[block[0]][block[1]] == 0:
                    result[block[0]][block[1]] = L[0]
                    L = L[1:]
        return result

    def neighbor_sudoku(self) -> np.ndarray:
        """
        Select a random block within the Sudoku grid and choose two available cells, denoted as cell1 and cell2.
        Subsequently, exchange the values contained in these two cells.
        """
        result = np.copy(self.grid)
        block = random.randint(0, 8)
        cells_available = []
        for b in self.index[block]:
            if (b[0], b[1]) not in self.pre_filled_indexes:
                cells_available.append(b)
        if len(cells_available) < 2:
            return result

        cell1, cell2 = random.sample(cells_available, 2)
        result[cell1[0], cell1[1]], result[cell2[0], cell2[1]] = (
            result[cell2[0], cell2[1]],
            result[cell1[0], cell1[1]],
        )

        return result

    def init_temperature(self):
        """
        Initialize the temperature of the algorithm based on the number of empty cells of 10 sudoku's neighbor.
        """
        sudoku_list = []
        for _ in range(10):
            neighbor = self.neighbor_sudoku()
            neighbor_score = self.compute_error(neighbor)
            sudoku_list.append(neighbor_score)
            self.grid = neighbor
            self.grid_score = neighbor_score
        return np.std(sudoku_list)

    def solve(self) -> np.ndarray:
        reheats = 0

        while True:
            if self.compute_error(self.grid) == 0:
                return self.grid
            previousScore = self.grid_score
            for _ in range(self.limit):
                neighbor = self.neighbor_sudoku()
                neighbor_score = self.compute_error(neighbor)
                p = np.exp((self.grid_score - neighbor_score) / self.temperature)
                if np.random.uniform(1, 0, 1) < p:
                    self.grid = neighbor
                    self.grid_score += neighbor_score - self.grid_score
                if self.grid_score <= 0:
                    return self.grid

            if self.grid_score >= previousScore:
                reheats += 1
            else:
                reheats = 0

            self.temperature *= self.cooling_rate
            if reheats > 80:
                self.temperature += 2
                reheats = 0


np.random.seed()
solver = Solver(np.array(instance).flatten().reshape((9, 9)), 0.99)
result = solver.solve()
r = result.astype("int").reshape((9, 9)).tolist()
