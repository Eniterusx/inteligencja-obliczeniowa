from stripsProblem import Planning_problem, STRIPS_domain, Strips
from searchMPP import SearcherMPP
from stripsForwardPlanner import Forward_STRIPS

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
        "collectFire": (True, False),
    }

    for fire in fire_coords:
        feature_domain_dict[get_fire(*fire)] = (True, False)
    
    for earth in earth_coords:
        feature_domain_dict[get_earth(*earth)] = (True, False)

    # all possible player movements
    stmap = {
        Strips(move(x, y, x + dx, y + dy), { "player": (x, y)}, { "player": (x + dx, y + dy)}) 
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for x in range(n) 
            for y in range(n)
            if x + dx in range(n) and y + dy in range(n)
    }

    # collecting fire
    stmap.update({
        Strips(collectFire(*coords), { "player": coords, get_fire(*coords): False, "collectFire": True }, { get_fire(*coords): True, "collectFire": False})
        for coords in fire_coords
    })

    # collecting earth
    stmap.update({
        Strips(collectEarth(*coords), { "player": coords, get_earth(*coords): False, "collectFire": False }, { get_earth(*coords): True, "collectFire": True})
        for coords in earth_coords
    })

    prereq_fireball = {
        "fireball": False,
    }

    for fire in fire_coords:
        prereq_fireball[get_fire(*fire)] = True
    
    for earth in earth_coords:
        prereq_fireball[get_earth(*earth)] = True

    # building a fireball
    stmap.update({
        Strips(buildFireball(), 
        prereq_fireball,
        { "fireball": True })
    })

    # attacking a dragon
    stmap.update({
       Strips(attack(dragon_coords[0], dragon_coords[1]), { "player": dragon_coords, "dragon": True, "fireball": True}, { "dragon": False, "fireball": False }) 
    })

    return STRIPS_domain(feature_domain_dict, stmap)


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

def heur_func(state, goal):
    # calculate the heuristic based on the state
    player = state["player"]
    dragon = state["dragon_coords"]
    # get all the features related to fire locations
    firekeys = list(filter(lambda x: not state[x], filter(lambda x: "fire_at" in x, state.keys())))
    earthkeys = list(filter(lambda x: not state[x], filter(lambda x: "earth_at" in x, state.keys())))
    
    collectFire = state["collectFire"]
    fireball = state["fireball"]
    castle = goal["player"]

    def castle_dist():
        return abs(player[0] - castle[0]) + abs(player[1] - castle[1])
    
    def dragon_dist():
        return abs(player[0] - dragon[0]) + abs(player[1] - dragon[1])

    def fire_dist():
        firelocations = [f.split("_")[2:] for f in firekeys]
        return min([abs(player[0] - int(f[0])) + abs(player[1] - int(f[1])) for f in firelocations])
    
    def earth_dist():
        earthlocations = [f.split("_")[2:] for f in earthkeys]
        return min([abs(player[0] - int(f[0])) + abs(player[1] - int(f[1])) for f in earthlocations])

    # distance = manhattan distance
    # if dragon dead, heuristic is the distance to the castle
    if not dragon:
        return castle_dist()
    # if dragon alive, and player has fireball, heuristic is distance to the dragon + distance to the castle
    elif fireball or (len(firekeys) + len(earthkeys) == 0):
        return dragon_dist()
    # if dragon alive, player doesn't have fireball, heuristic is distance to the dragon + distance to the nearest fire/earth (whatever needs to be collected)
    elif collectFire:
        return fire_dist()
    else:
        return earth_dist()


def problemCreator(dragon, fire, earth, player_coords, castle, mapsize, iters=100):
    world1 = initWorld(mapsize, dragon, fire, earth)
    start_state = {
        "player": player_coords,
        "dragon": True,
        "fireball": False,
        "collectFire": True,
        "dragon_coords": dragon,
    }

    for f in fire:
        start_state[get_fire(*f)] = False

    for e in earth:
        start_state[get_earth(*e)] = False

    goal_state = {
        "player": castle,
        "dragon": False
    }

    problem = Planning_problem(
        world1, 
        start_state, 
        goal_state
    )
    sol = searchForSolutions(SearcherMPP(Forward_STRIPS(problem, heur=heur_func)), iters)
    print(sol)
    print(f"Cost of the solution: {sol.cost}")



dragon = (2, 11)
fire = [(2, 5), (5, 1), (10, 8), (1, 5)]
earth = [(4, 2), (0, 6), (3, 11)]
player_coords = (7, 2)
castle = (8, 8)
problemCreator(dragon, fire, earth, player_coords, castle, 12)


# easy

# dragon = (1, 3)
# fire = [(2, 2)]
# earth = [(7, 5)]
# player_coords = (1, 1)
# castle = (4, 4)
# problemCreator(dragon, fire, earth, player_coords, castle, 10)

# dragon = (1, 3)
# fire = [(2, 4), (8, 8)]
# earth = [(7, 5)]
# player_coords = (1, 1)
# castle = (4, 4)
# problemCreator(dragon, fire, earth, player_coords, castle, 10)

# dragon = (0, 0)
# fire = [(1, 1), (1, 2)]
# earth = [(2, 1), (9, 9)]
# player_coords = (2, 2)
# castle = (9, 8)
# problemCreator(dragon, fire, earth, player_coords, castle, 10)

# # hard

# dragon = (2, 11)
# fire = [(2, 5), (5, 1), (10, 8), (1, 5)]
# earth = [(4, 2), (0, 6), (3, 11)]
# player_coords = (7, 2)
# castle = (8, 8)
# problemCreator(dragon, fire, earth, player_coords, castle, 12)

# dragon = (10, 11)
# fire = [(2, 2), (10, 1), (1, 11), (1, 9), (0, 0)]
# earth = [(7, 5), (6, 6), (9, 11), (7, 9)]
# player_coords = (11, 10)
# castle = (5, 5)
# problemCreator(dragon, fire, earth, player_coords, castle, 12)

# dragon = (10, 11)
# fire = [(2, 2), (6, 1), (5, 9), (1, 9), (2, 8)]
# earth = [(7, 5), (4, 6), (3, 11), (7, 9), (11, 11)]
# player_coords = (11, 10)
# castle = (5, 5)
# problemCreator(dragon, fire, earth, player_coords, castle, 12)