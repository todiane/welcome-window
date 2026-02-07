import random


def generate_sudoku(difficulty="medium"):
    def is_valid(grid, row, col, num):
        if num in grid[row]:
            return False
        if num in [grid[i][col] for i in range(9)]:
            return False
        br, bc = 3 * (row // 3), 3 * (col // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if grid[i][j] == num:
                    return False
        return True

    def solve(grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    for num in random.sample(range(1, 10), 9):
                        if is_valid(grid, i, j, num):
                            grid[i][j] = num
                            if solve(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True

    grid = [[0] * 9 for _ in range(9)]
    for box in range(0, 9, 3):
        nums = random.sample(range(1, 10), 9)
        for i in range(3):
            for j in range(3):
                grid[box + i][box + j] = nums[i * 3 + j]

    solve(grid)
    solution = [row[:] for row in grid]

    cells_to_remove = {"easy": 30, "medium": 40, "hard": 50}.get(difficulty, 40)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    for i in range(cells_to_remove):
        grid[cells[i][0]][cells[i][1]] = 0

    return {"puzzle": grid, "solution": solution}
