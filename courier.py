# Mini-Project: “Skyrim Delivery Ledger”
# A single-player, text-only retro-RPG that forces the learner to use every basic control structure while staying 100 % in-universe.

import json, random, os

# ---CONFIG---
MAP_W, MAP_H = 4, 4
START_POS = (0, 0)
PLAYER_FILE = "courier_ledger.json"

# ---UTILS / SYSTEMS---
def load_player():
    if os.path.exists(PLAYER_FILE):
        return json.load(open(PLAYER_FILE))
    return {"gold": 20, "health": 10, "rep": 0, "day": 1}

def save_player(player):
    json.dump(player, open(PLAYER_FILE, "w"), indent = 2)

def generate_packages(day):
    townsfolk = ["Aela", "Balgruuf", "Cicero", "Delphine", "Esbern", "Farkas"]
    items     = ["Alto Wine", "Dwemer Cog", "Mammoth Cheese", "Nightshade", "Sweetroll"]
    packages = []
    for i in range(3 + day):
        packages.append({
            "id": i,
            "npc": random.choice(townsfolk),
            "item": random.choice(items),
            "reward": random.randint(1, 10),
            "destination": (random.randint(0, MAP_W-1), random.randint(0, MAP_H-1)),
            "deadline": 8 + day # turns
        })
    return packages

# ---CORE GAMEPLAY FUNCTIONS---
def show_status(player, pos, inventory, turns_left, packages):
    print("\nTurns left:", turns_left, "| Health:", player["health"], "| Gold:", player["gold"], "| Rep:", player["rep"])
    print("You are at", pos)
    print("Inventory:", inventory)

    # Show active deliveries
    todo = [p for p in packages if p["id"] in [itm.get("pkg_id") for itm in inventory]]
    for t in todo:
        print("  – Deliver {} to {} at {}".format(t["item"], t["npc"], t["destination"]))

def handle_move(cmd, pos, turns_left, player, inventory, packages):
    old_pos = pos[:]
    if cmd == "w": pos[1] += 1
    elif cmd == "s": pos[1] -= 1
    elif cmd == "a": pos[0] -= 1
    elif cmd == "d": pos[0] += 1

    # Keep inside map bounds
    pos[0] = max(0, min(MAP_W-1, pos[0]))
    pos[1] = max(0, min(MAP_H-1, pos[1]))

    if pos != old_pos:
        turns_left -= 1
        road_event(player, inventory)
        arrive_at_location(pos, packages, inventory, player)

    return pos, turns_left

def handle_packages(packages, inventory):
    print("\nAvailable packages today:")
    for pkg in packages:
        print(" {}: {} -> {} @ {}  (reward {} gold)".format(
            pkg["id"], pkg["item"], pkg["npc"], pkg["destination"], pkg["reward"]))

    pick = input("Pick package id to accept (or Enter to skip): ")
    if pick.isdigit():
        pick = int(pick)
        chosen = next((p for p in packages if p["id"] == pick), None)
        if chosen and chosen["id"] not in [itm.get("pkg_id") for itm in inventory]:
            inventory.append({"name": chosen["item"], "pkg_id": chosen["id"]})
            print("Accepted:", chosen["item"])
        else:
            print("Invalid or already accepted.")

# ---GAME LOOP---
def main():
    player = load_player()
    packages = generate_packages(player["day"])
    inventory = []
    pos = list(START_POS)
    turns_left = 10 + player["day"]

    print("=== Skyrim Courier Day {} ===".format(player["day"]))
    while turns_left > 0 and player["health"] > 0:
        show_status(player, pos, inventory, turns_left, packages)

        cmd = input("Move (wasd), Check packages (p), Quit (q): ").lower()
        if cmd == "q":
            break
        elif cmd in "wasd":
            pos, turns_left = handle_move(cmd, pos, turns_left, player, inventory, packages)
        elif cmd == "p":
            handle_packages(packages, inventory)

    # End of day
    print("\nDay over. Final stats:", player)
    player["day"] += 1
    save_player(player)

# ---------- EVENT & LOCATION ----------
def road_event(p, inv):
    if random.random() < 0.3:
        evt = random.choice(["wolf", "bandit", "sweetroll"])
        if evt == "wolf":
            print("A wolf attacks! You lose 2 health.")
            p["health"] -= 2
        elif evt == "bandit":
            if p["gold"] >= 5:
                print("Bandit demands 5 gold.")
                p["gold"] -= 5
            else:
                print("Bandit robs one item!")
                if inv: inv.pop()
        else:
            print("You found a sweetroll on the road. Yum! +1 health.")
            p["health"] += 1

def arrive_at_location(pos, packages, inventory, player):
    for pkg in packages:
        if tuple(pos) == pkg["destination"]:
            carried = next((itm for itm in inventory if itm.get("pkg_id") == pkg["id"]), None)
            if carried:
                print("Delivered {} to {}! +{} gold, +1 rep".format(
                    pkg["item"], pkg["npc"], pkg["reward"]))
                inventory.remove(carried)
                player["gold"] += pkg["reward"]
                player["rep"] += 1
            else:
                print("{} is here but you don't have their package.".format(pkg["npc"]))

if __name__ == "__main__":
    main()