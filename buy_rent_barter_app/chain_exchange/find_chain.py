def comparator(first, second):
    return first == second

def simple(searched_for, possible):
    result = []
    for i in range(0, len(possible)):
        if comparator(possible[i]["wanted"], searched_for["ware"]) and comparator(possible[i]["ware"],
                                                                                  searched_for["wanted"]):
            result.append([possible[i], searched_for])
    return result


def find_possibille_chain(searched_for, possible):
    result = []
    a = "ff"
    for i in range(0, len(possible) - 1):
        for j in range(i+1, len(possible)):
            #print(possible[i]["ware"] + " " +possible[j]["wanted"])
            #if possible[i]["ware"] == possible[j]["wanted"]:
                #print(1)
            if comparator(searched_for["ware"], possible[i]["wanted"]) and comparator(searched_for["wanted"],
                                                                                          possible[j]["ware"]) and comparator(possible[j]["wanted"],
                                                                                          possible[i]["ware"]):
                    result.append([searched_for, possible[i], possible[j]])
            if comparator(searched_for["ware"], possible[j]["wanted"]) and comparator(searched_for["wanted"],
                                                                                          possible[i]["ware"]) and comparator(possible[i]["wanted"],
                                                                                          possible[j]["ware"]):
                    result.append([searched_for, possible[i], possible[j]])
       #     print(result)
    return result


searched_for = {"ware": "a", "wanted": "b"}
available = [{"ware": "b", "wanted": "a"},
             {"ware": "b", "wanted": "c"},
             {"ware": "c", "wanted": "a"},
             {"ware": "c", "wanted": "d"},
             {"ware": "t", "wanted": "a"},
             {"ware": "s", "wanted": "x"},
             {"ware": "d", "wanted": "e"}]
searched = []
result = find_possibille_chain(searched_for, available)
#print(result)
#print("*****")
result = simple(searched_for, available)
#print(result)
