# all the player and env stats

from dataclasses import dataclass, field
from typing import Dict
import numpy as np

@dataclass
class Item:
    city : int
    suburbs : int
    mall : int
    probs_initial : list

    def initialization(self):
        # generating prob values
        self.probs = {}
        for i, city in enumerate(["city", "suburbs", "mall"]) :
            self.probs[city] = self.probs_initial[i]

    
    def update_percentage(self, location:str, amount:int=1):
        # substract the given amount and update the probability
        value = getattr(self, location)
        if value == 0 :
            self.probs[location] = 0
            return

        prob = self.probs[location]

        new_value = max(0, value - amount)
        new_prob = round((new_value * prob) / value, 2)

        setattr(self, location, new_value)
        self.probs[location] = new_prob



    def get_stats(self):
        return np.array([
            self.city, self.suburbs, self.mall, *self.probs.values()
        ])
    
    def get_stats_norm(self, max_amount):
        # normalized version of stats
        return np.array([
            self.city/max_amount, self.suburbs/max_amount, self.mall/max_amount, *self.probs.values()
        ])




@dataclass
class Env_Stats :
    inventory: Dict[str, int] = field(default_factory=lambda: {'food': 2, 'gas': 2, 'ammo': 2})
   
    def __post_init__(self):
        self.food = Item(8, 2, 12, [0.40, 0.10, 0.60])
        self.gas = Item(3, 12, 8, [0.15, 0.60, 0.40])
        self.ammo = Item(12, 8, 3, [0.60, 0.40, 0.15])
        self.zombie = Item(10, 8, 6, [0.50, 0.40, 0.30])

        self.items = {
            "food": self.food,
            "gas": self.gas,
            "ammo": self.ammo,
            "zombie": self.zombie,
        }

    def initialization(self):
        for item in self.items.values():
            item.initialization()

    def get_location(self, location:str):
        info = {
            "food" : [getattr(self.food, location), self.food.probs[location]],
            "gas" : [getattr(self.gas, location), self.gas.probs[location]],
            "ammo" : [getattr(self.ammo, location), self.ammo.probs[location]],
            "zombie" : [getattr(self.zombie, location), self.zombie.probs[location]]
        }
        return info


    def search_items(self, item:str, location:str) -> str :
        prob = self.items[item].probs[location]
        found = np.random.choice([1, 0], p=np.array([1 - prob, prob]))

        if found :
            return True, " You searched and found 1 " + item + " in " + location

        return False, " You searched but did not found any " + item 

    def get_stats(self) :
        all_stats = np.array([*self.inventory.values()])
        all_stats = np.concatenate([all_stats, *[x.get_stats() for x in self.items.values()]], axis=0)
        return all_stats
    
    def get_stats_normalized(self, max_amount) :
        all_stats = np.array([x/max_amount for x in self.inventory.values()])
        all_stats = np.concatenate([all_stats, *[x.get_stats_norm(max_amount) for x in self.items.values()]], axis=0)
        return all_stats





    