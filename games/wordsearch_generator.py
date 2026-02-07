import random


def generate_wordsearch(theme="general", size=12):
    words_lists = {
        "christmas": [
            "CHRISTMAS",
            "SNOWFLAKE",
            "REINDEER",
            "PRESENTS",
            "SANTA",
            "BELLS",
            "CAROLS",
        ],
        "general": [
            "HELLO",
            "FRIEND",
            "WELCOME",
            "CHAT",
            "GAMES",
            "CONNECT",
            "SMILE",
            "LAUGH",
        ],
    }
    words = words_lists.get(theme, words_lists["general"])[:6]
    grid = [
        [random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(size)]
        for _ in range(size)
    ]

    for word in words:
        placed = False
        for _ in range(50):
            if placed:
                break
            direction = random.choice(["h", "v"])
            row, col = random.randint(0, size - 1), random.randint(0, size - 1)

            if direction == "h" and col + len(word) <= size:
                if all(
                    grid[row][col + i] == word[i]
                    or grid[row][col + i] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    for i in range(len(word))
                ):
                    for i in range(len(word)):
                        grid[row][col + i] = word[i]
                    placed = True
            elif direction == "v" and row + len(word) <= size:
                if all(
                    grid[row + i][col] == word[i]
                    or grid[row + i][col] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    for i in range(len(word))
                ):
                    for i in range(len(word)):
                        grid[row + i][col] = word[i]
                    placed = True

    return {"grid": grid, "words": words}
