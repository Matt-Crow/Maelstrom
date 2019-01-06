enemies = dict()
elemental_enemies = ("Lightning Entity", "Rain Entity", "Hail Entity", "Wind Entity")

enemies["MIN"] = ((0, 0, 0, 0, 0), "stone")

enemies["Lightning Entity"] = ((0, 15, 15, 10, 10), "lightning")
enemies["Rain Entity"] = ((3, -3, 3, 0, 0), "rain")
enemies["Hail Entity"] = ((3, -3, -3, 0, 0), "hail")
enemies["Wind Entity"] = ((-3, 3, -3, 0, 0), "wind")

enemies["stone soldier"] = ((15, 15, 10, 5, 5), "stone")
