import findbus

finder = findbus.AdvancedBusRouteFinder()

orgin_lat , orgin_long = 11.2588, 75.7804
dest_lat , dest_long = 11.1410, 75.9550
max_tranfers = 3 
max_walking = 2000
journeys = finder.find_all_routes(orgin_lat,orgin_long,dest_lat,dest_long)


print(journeys)
