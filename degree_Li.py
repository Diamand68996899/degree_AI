import csv
import sys
import os


from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    # the python command for the command-line arguments passed to the scrip
    #if len(sys.argv) > 2:
    #    sys.exit("Usage: python degrees.py [directory]")
    #directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    cwd = os.getcwd()
    directory = cwd + '\small'  # *******
    print('----------------path', sys.argv[0], len(sys.argv), '---directory-> ', directory)
    ################################## ###########

    # Load data from files into memory

    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    source = person_id_for_name(input("Name: "))
    # with open(r'small\random_name') as f:                              #*******
    #    names = f.read().splitlines()
    # s_name = random.choice(names)
    # source = person_id_for_name(s_name.strip())
    if source is None:
        sys.exit("Person not found")

    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found")

    path = shortest_path(source, target)
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):

    # swap check -------output source_1deg, target_1deg/ (person_id,movie_id)   (source_2deg, target_2deg)----------------
    if True:
        source_1deg = set()
        target_1deg = set()
        source_2deg = set()
        target_2deg = set()

        for s in (source, target):
            to_1m = set()
            to_1m.add((s, None))
            to_1mm = set()
            to_1mp = set()
            for movie_id, person_id in neighbors_for_person(s):
                to_1m.add((person_id, movie_id))
                to_2m = set()
                for movie_id, person_id in neighbors_for_person(person_id):
                    to_2m.add((person_id, movie_id))
            if s == source:
                source_1deg = to_1m
                source_2deg = to_2m

            else:
                target_1deg = to_1m
                target_2deg = to_2m

        if (len(source_1deg) + len(source_2deg)) > (len(target_1deg) + len(target_2deg)):
            target, source = source, target
            source_1deg, target_1deg = target_1deg, source_1deg
            source_2deg, target_2deg = target_2deg, source_2deg

            print('---swap is done for target and source')
        print(source, target)
        # -----------------------------------------------------------------------------------
        pass

    # node population -------------------------------------------------------

        node = Node(state=source, parent= None, action= None)
        front = QueueFrontier()
        nodes_front = set()
        nodes_explored = set()
        nodes_explored.add((source, None, None))
        num_explored = 0
        paths = []

    gen_num = 1
    while True:

        # generating kid_node at same generation level
        kid_num = 0
        while gen_num > 0:               # generating new kids node at same generation level
            # get node under exploration
            if len(front.frontier) > 0:
                node = front.remove_first()

            # add node under exploration into  node_explored set
            if node.action != None:
                current_node = []
                p_node = node.parent
                current_node.append(p_node.state)  # fixed after
                current_node.append(node.action)
                current_node.append(node.state)
                current_node = tuple(current_node)
                nodes_explored.add(current_node)
                if current_node in nodes_front:
                    nodes_front.remove(current_node)
            num_explored += 1
            gen_num -= 1          # loop time control with number of nodes at the same generation level

            # generating kid_node for same node
            for movie_id, person_id in neighbors_for_person(node.state):

                if (person_id, movie_id, node.state) not in nodes_explored and (node.state, movie_id, person_id) not in nodes_explored and person_id != node.state:
                    if (person_id, movie_id, node.state) not in nodes_front and (node.state, movie_id, person_id) not in nodes_front:
                        kid_node = []
                        kid_node.append(person_id)
                        kid_node.append(movie_id)
                        kid_node.append(node.state)
                        nodes_front.add(tuple(kid_node))
                        m_node = Node(state=person_id, parent=node, action=movie_id)
                        front.add(m_node)
                        kid_num += 1

                    # target is reached ?? ---------------------------------------
                    if person_id == target:
                        print('reached the target:', target)
                        front.frontier[0], front.frontier[-1] = front.frontier[-1], front.frontier[0]
                        gen_num = 0
                        break

        gen_num = kid_num
        print(f'number of new kid nodes:{kid_num} / number of explored node: {num_explored} '
                  f'/ number of nodes in frontier {len(front.frontier)}')

        # checkpoint for ending the search loop----------------------------------------------------
        if len(front.frontier) == 0 and kid_num == 0:
            print('\n', f'search is ended and has found no path with {num_explored} explored nodes')
            return None

        # node.state == target ---output path short_path ---------------------------------------
        if person_id == target:
            node = front.remove_first()
            m_path = []
            action_dict = []

            while node.parent != None :
                m_path.append((node.action, node.state))
                action_dict.append(node.action)
                node = node.parent

            paths.append(m_path)
            print('new path length at: ', len(m_path))
            print('new path length at: ', m_path)
            print('*********************************')

            # return the shortest path
            if len(action_dict) == len(set(action_dict)):
                short_path = m_path
                short_path.reverse()
                print('\n', f'---->> connection found path with length: ', len((short_path)))
                return short_path

        # move node with short distance to the target to the next first node for exploration
        for i in range(kid_num):  # look up in all of kid_nodes
            node = front.frontier[i]
            if (node.state, node.action) in target_1deg:
                front.frontier[i], front.frontier[0] = front.frontier[0], front.frontier[-i]
                break
        else:
            for i in range(kid_num):  # look up in all of kid_nodes
                node = front.frontier[i]
                if (node.state, node.action) in target_2deg:
                    front.frontier[i], front.frontier[0] = front.frontier[0], front.frontier[-i]
                    break


def person_id_for_name(name):
    # Returns the IMDB id for a person's name,resolving ambiguities as needed.
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))

    return neighbors


if __name__ == "__main__":
    main()
