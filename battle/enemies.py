enemies = dict()
elemental_enemies = ("Lightning Entity", "Rain Entity", "Hail Entity", "Wind Entity")

enemies["MAX"] = ((5, 0, 0, 0, 0), "stone")
enemies["MIN"] = ((-5, 0, 0, 0, 0), "stone")

enemies["Lightning Entity"] = ((-3, 3, 3, 0, 0), "lightning")
enemies["Rain Entity"] = ((3, -3, 3, 0, 0), "rain")
enemies["Hail Entity"] = ((3, -3, -3, 0, 0), "hail")
enemies["Wind Entity"] = ((-3, 3, -3, 0, 0), "wind")

enemies["stone soldier"] = ((2, -3, -3, 0, 0), "stone")