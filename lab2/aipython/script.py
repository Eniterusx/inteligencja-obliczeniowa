from stripsProblem import Planning_problem, STRIPS_domain, Strips
from searchMPP import SearcherMPP
from stripsForwardPlanner import Forward_STRIPS

def searchForSolutions(searcher: SearcherMPP, iterations=1000):
    best_sol = None
    for i in range(iterations):
        print("Iteration: ", i)
        new_sol = searcher.search()
        if new_sol is None:
            break
        if best_sol is None or new_sol.cost < best_sol.cost:
            best_sol = new_sol
    return best_sol

def move(x, y, nx, ny):
    return 'move_from_'+str(x)+str(y)+'_to_'+str(nx)+str(ny)

def attack(x, y):
    return "attack_dragon_at_" + str(x) + "_" + str(y)

def open():
    pass

def collectFire(x, y):
    return "collect_fire_at_" + str(x) + "_" + str(y)

def collectEarth(x, y):
    return "collect_earth_at_" + str(x) + "_" + str(y)

def buildFireball():
    return "build_fireball"


def get_fire(x, y):
    return f"fire_at_{x}_{y}"

def get_earth(x, y):
    return f"earth_at_{x}_{y}"

# nxn grid with player, castle, walls, and dragons
# End goal is kill the dragon and react the castle
# To kill the dragon, player has to be at dragon coordinates and has the fireball
# To build a fireball, the player needs k earth and l fire
# To attack, the player has to be at the same position as a dragon
# Player can open a chest but idk why - skip for now

def initWorld(n, dragon_coords, fire_coords, earth_coords):
    # nxn grid
    feature_domain_dict = { 
        "player": [(i, j) for i in range(n) for j in range(n)], 
        "dragon": (True, False),
        "fireball": (True, False), 
    }

    for fire in fire_coords:
        feature_domain_dict[get_fire(*fire)] = (True, False)
    
    for earth in earth_coords:
        feature_domain_dict[get_earth(*earth)] = (True, False)

    print("DICTIONARY")
    print(feature_domain_dict)

    # all possible player movements
    stmap = {
        # Strips(move(x, y, x + dx, y + dy), { "player": (x, y)}, { "player": (x + dx, y + dy)}) 
        #     for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
        #     for x in range(n) 
        #     for y in range(n)
        #     if x + dx in range(n) and y + dy in range(n)
    }

    # collecting fire
    # for coords in fire_coords:
    #     print(get_fire(*coords))
    #     print({ "player": coords, str(get_fire(*coords)): False})

        
    # stmap.update({
    #     Strips(collectFire(coords[0], coords[1]), { "player": coords, get_fire(*coords): False}, { get_fire(*coords): True })
    #     for coords in fire_coords
    # })

    # collecting fire
    # stmap.update({
    #     Strips(collectFire(coords[0], coords[1]), { "player": coords, get_fire(*coords): False}, { get_fire(*coords): True })
    #     for coords in fire_coords
    # })

    # collecting earth
    print({
        Strips(collectEarth(coords[0], coords[1]), { "player": coords, get_earth(*coords): False}, { get_earth(*coords): True })
        for coords in earth_coords
    })

    # preq_fireball_map = {
        # "fireball": False
    # }
    # for coords in fire_coords:
    #     preq_fireball_map[get_fire(*coords)] = True
    
    # for coords in earth_coords:
    #     preq_fireball_map[get_earth(*coords)] = True
    


    # building a fireball
    stmap.update({
        Strips(buildFireball(), 
               { 
                   get_fire(*fcoords): True, 
                   get_earth(*ecoords): True, 
                   "fireball": False
                   }, { "fireball": True, "fire": False, "earth": False})
        for fcoords in fire_coords for ecoords in earth_coords
    })

    # attacking a dragon
    stmap.update({
       Strips(attack(dragon_coords[0], dragon_coords[1]), { "player": dragon_coords, "dragon": True, "fireball": True}, { "dragon": False, "fireball": False }) 
    })

    print("STMAP")
    print(stmap)

    return STRIPS_domain(feature_domain_dict, stmap)

def heur_func(state, goal):
    # calculate the heuristic based on the state
    player = state["player"]
    dragon = state["dragon_cords"]
    fire = state["fire_cords"]
    earth = state["earth_cords"]
    fireball = state["fireball"]
    isfire = state["fire"]
    isearth = state["earth"]
    castle = goal["player"]

    # distance = manhattan distance
    # if dragon dead, heuristic is the distance to the castle
    if not dragon:
        return abs(player[0] - castle[0]) + abs(player[1] - castle[1])
    # if dragon alive, and player has fireball, heuristic is distance to the dragon + distance to the castle
    elif fireball or (isfire and isearth):
        return abs(player[0] - dragon[0]) + abs(player[1] - dragon[1]) + abs(dragon[0] - castle[0]) + abs(dragon[1] - castle[1])
    # if dragon alive, and player doesn't have fireball but has fire, heuristic is distance to the dragon + distance to the nearest earth + distance to the castle
    elif isfire:
        return abs(player[0] - dragon[0]) + abs(player[1] - dragon[1]) + abs(fire[0] - player[0]) + abs(fire[1] - player[1]) + abs(fire[0] - castle[0]) + abs(fire[1] - castle[1])
    # if dragon alive, and player doesn't have fireball but has earth, heuristic is distance to the dragon + distance to the nearest fire + distance to the castle
    elif isearth:
        return abs(player[0] - dragon[0]) + abs(player[1] - dragon[1]) + abs(earth[0] - player[0]) + abs(earth[1] - player[1]) + abs(earth[0] - castle[0]) + abs(earth[1] - castle[1])
    # if dragon alive, and player doesn't have fireball, heuristic is distance to the dragon + distance to the nearest fire + distance to the nearest earth + distance to the castle
    else:
        return abs(player[0] - dragon[0]) + abs(player[1] - dragon[1]) + abs(fire[0] - player[0]) + abs(fire[1] - player[1]) + abs(earth[0] - player[0]) + abs(earth[1] - player[1]) + abs(earth[0] - castle[0]) + abs(earth[1] - castle[1])
    

dragon = (1, 3)
fire = [(2, 2), (1, 1)]
earth = [(7, 5), (6, 6)]
world1 = initWorld(10, dragon, fire, earth)
player_coords = (0, 0)
castle = (5, 5)

starting_state = { "player": player_coords, "dragon": True, "fireball": False, "dragon_cords": dragon }


problem = Planning_problem(
    world1, 
    { "player": player_coords, "dragon": True, "fire": 2, "earth": 2, "fireball": False, "dragon_cords": dragon, "fire_cords": fire, "earth_cords": earth}, 
    { "player": castle, "dragon": False}
)

searcher = SearcherMPP(Forward_STRIPS(problem, heur=heur_func))


# sol = searchForSolutions(searcher)
# print(f"Cost of the best solution found: {sol.cost}")