# games/wordsearch_generator.py
import random


def generate_wordsearch(theme="general", size=12):
    words_lists = {
        "animals": [
            "ELEPHANT",
            "GIRAFFE",
            "PENGUIN",
            "DOLPHIN",
            "KANGAROO",
            "TIGER",
            "ZEBRA",
            "MONKEY",
            "PANDA",
            "KOALA",
            "CHEETAH",
            "LEOPARD",
            "EAGLE",
            "FALCON",
            "SHARK",
            "WHALE",
            "OCTOPUS",
            "RABBIT",
            "SQUIRREL",
            "HEDGEHOG",
        ],
        "food": [
            "PIZZA",
            "BURGER",
            "PASTA",
            "SUSHI",
            "TACOS",
            "CURRY",
            "SALAD",
            "COFFEE",
            "CHOCOLATE",
            "CHEESE",
            "APPLE",
            "BANANA",
            "ORANGE",
            "MANGO",
            "BREAD",
            "RICE",
            "CHICKEN",
            "SALMON",
            "COOKIES",
            "CAKE",
        ],
        "travel": [
            "PARIS",
            "LONDON",
            "TOKYO",
            "BEACH",
            "MOUNTAIN",
            "DESERT",
            "ISLAND",
            "AIRPORT",
            "HOTEL",
            "PASSPORT",
            "LUGGAGE",
            "CRUISE",
            "SAFARI",
            "CAMPING",
            "HIKING",
            "TRAIN",
            "PLANE",
            "ROAD",
            "JOURNEY",
            "ADVENTURE",
        ],
        "tech": [
            "COMPUTER",
            "INTERNET",
            "SOFTWARE",
            "CODING",
            "DATABASE",
            "PYTHON",
            "JAVASCRIPT",
            "WEBSITE",
            "MOBILE",
            "CLOUD",
            "SERVER",
            "NETWORK",
            "SECURITY",
            "DIGITAL",
            "ROBOT",
            "VIRTUAL",
            "GAMING",
            "SCREEN",
            "KEYBOARD",
            "MOUSE",
        ],
        "nature": [
            "FOREST",
            "OCEAN",
            "RIVER",
            "MOUNTAIN",
            "FLOWER",
            "TREE",
            "SUNSET",
            "RAINBOW",
            "CLOUD",
            "STORM",
            "THUNDER",
            "LIGHTNING",
            "BREEZE",
            "VALLEY",
            "CANYON",
            "MEADOW",
            "STREAM",
            "WATERFALL",
            "GLACIER",
            "VOLCANO",
        ],
        "music": [
            "GUITAR",
            "PIANO",
            "DRUMS",
            "VIOLIN",
            "TRUMPET",
            "SAXOPHONE",
            "FLUTE",
            "SINGER",
            "CONCERT",
            "MELODY",
            "RHYTHM",
            "HARMONY",
            "TEMPO",
            "JAZZ",
            "ROCK",
            "CLASSICAL",
            "BLUES",
            "ORCHESTRA",
            "BAND",
            "CHORUS",
        ],
        "sports": [
            "FOOTBALL",
            "BASKETBALL",
            "TENNIS",
            "CRICKET",
            "BASEBALL",
            "HOCKEY",
            "SWIMMING",
            "RUNNING",
            "CYCLING",
            "GOLF",
            "BOXING",
            "WRESTLING",
            "SURFING",
            "SKIING",
            "SKATING",
            "RUGBY",
            "VOLLEYBALL",
            "BADMINTON",
            "ARCHERY",
            "FENCING",
        ],
        "movies": [
            "ACTION",
            "COMEDY",
            "DRAMA",
            "THRILLER",
            "HORROR",
            "ROMANCE",
            "FANTASY",
            "MYSTERY",
            "ADVENTURE",
            "WESTERN",
            "DIRECTOR",
            "ACTOR",
            "SCRIPT",
            "CINEMA",
            "SCREEN",
            "PREMIERE",
            "SEQUEL",
            "BLOCKBUSTER",
            "OSCAR",
            "CREDITS",
        ],
        "space": [
            "GALAXY",
            "PLANET",
            "STAR",
            "MOON",
            "COMET",
            "ASTEROID",
            "NEBULA",
            "COSMOS",
            "ORBIT",
            "ROCKET",
            "SATELLITE",
            "ASTRONAUT",
            "TELESCOPE",
            "UNIVERSE",
            "SOLAR",
            "METEOR",
            "GRAVITY",
            "ALIEN",
            "SPACESHIP",
            "MARS",
        ],
        "christmas": [
            "CHRISTMAS",
            "SNOWFLAKE",
            "REINDEER",
            "PRESENTS",
            "SANTA",
            "BELLS",
            "CAROLS",
            "SLEIGH",
            "MISTLETOE",
            "ORNAMENT",
            "TINSEL",
            "WREATH",
            "GINGERBREAD",
            "STOCKINGS",
            "COOKIES",
            "CHIMNEY",
            "ELVES",
            "FESTIVE",
            "DECEMBER",
            "FAMILY",
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
            "HAPPY",
            "JOY",
            "FUN",
            "PLAY",
            "SHARE",
            "KINDNESS",
            "PEACE",
            "HOPE",
            "DREAM",
            "MAGIC",
            "WONDER",
            "SUNSHINE",
        ],
    }
    # Start with empty grid filled with spaces
    grid = [[" " for _ in range(size)] for _ in range(size)]

    # Select candidate words
    candidate_words = random.sample(
        words_lists.get(theme, words_lists["general"]),
        min(10, len(words_lists.get(theme, words_lists["general"]))),
    )

    placed_words = []

    for word in candidate_words:
        placed = False
        for _ in range(100):
            if placed:
                break
            direction = random.choice(["h", "v"])
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)

            # Check if word fits
            if direction == "h" and col + len(word) <= size:
                # Check if all cells are empty or match the word
                can_place = all(
                    grid[row][col + i] == " " or grid[row][col + i] == word[i]
                    for i in range(len(word))
                )
                if can_place:
                    for i in range(len(word)):
                        grid[row][col + i] = word[i]
                    placed = True

            elif direction == "v" and row + len(word) <= size:
                # Check if all cells are empty or match the word
                can_place = all(
                    grid[row + i][col] == " " or grid[row + i][col] == word[i]
                    for i in range(len(word))
                )
                if can_place:
                    for i in range(len(word)):
                        grid[row + i][col] = word[i]
                    placed = True

        # Only add to word list if successfully placed
        if placed:
            placed_words.append(word)
            if len(placed_words) >= 8:
                break

    # Fill remaining empty spaces with random letters
    for i in range(size):
        for j in range(size):
            if grid[i][j] == " ":
                grid[i][j] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    return {"grid": grid, "words": placed_words}
