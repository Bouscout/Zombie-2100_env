
from .stats import Env_Stats
import numpy as np

# Actions: move1,move2,move3,food,gas,ammo,hide

class Zombie_2100_Env :
    LOCATIONS = ["city", "suburbs", "mall"]

    def __init__(self, normalize=True) -> None:
        self.normalize = normalize
        self.reset()
        self.actions = ['move1','move2','move3','food','gas','ammo',"hide"]
        

    @property
    def action_space(self):
        return len(self.actions)
    
    @property
    def obs_space(self):
        return (33, )

    def change_location(self, new_loc:int) -> str:
        if self.stats.inventory["gas"] > 0 :
            self.location = new_loc
            self.stats.inventory["gas"] -= 1
            return " You moved to " + self.LOCATIONS[new_loc]
        
        else : 
            return " You tried to start your car but no gas"
        
    def get_location(self) -> str:
        return self.LOCATIONS[self.location]
        
    def shooting_zombie(self) -> str :
        message = " You encountered a zombie"
        if self.stats.inventory["ammo"] > 0 :
            # shooting bullet to kill zombie
            self.stats.inventory["ammo"] -= 1

            # changing zombie percent in area
            self.stats.items["zombie"].update_percentage(self.get_location(), 1)
            message += " shot 1 ammo and killed the zombie"
            return message
        else :
            message += " no ammo to shot"
            # 50% chance to get bite
            if np.random.choice([1, 0], p=np.array([0.5, 0.5])) :
                message += " it almost bit you."
            else :
                message += " it bit you and you died"
                self.alive = False

            return message
            

    def zombie_attack(self) -> str:
        # check zombie encounter 
        z_prob = self.stats.zombie.probs[self.get_location()]
  
        passed = np.random.choice([1, 0], p=np.array([1 - z_prob, z_prob]))

        if not passed  :
           return self.shooting_zombie()

        return " No zombie encountered"
        
    def eat_food(self) -> str :
        if self.stats.inventory["food"] > 0 :
            self.stats.inventory["food"] -= 1
            return "  Good morning, you ate 1 food"

        else :
            self.alive = False
            return " You died of hunger"
        
    def hiding(self):
        # 10% chance of meeting a zombie
        passed = np.random.choice([1, 0], p=np.array([0.9, 0.1]))
        if passed :
            return " You found a quiet spot to hide."

        else :
            return " you found a spot to hide but " + self.shooting_zombie()
        
    def reset(self) -> np.ndarray :
        self.alive = True
        self.day = 1
        self.max_day = 7

        self.stats = Env_Stats()
        self.stats.initialization()
        self.max_amount = np.max(self.stats.get_stats())

        self.location = np.random.randint(0, len(self.LOCATIONS))

        self.turn = 1
        return self.get_states()

        
    def step(self, action:int) -> tuple :
        """
        Perform an action in the environment and return the next state.

        action are passed as an index for the actionsList=[move1,move2,move3,food,gas,ammo,hide]

        >>> next_step, reward, done, message = env.step(3)
        """
        done = False
        message = "" 
        if self.day == 8 and self.alive :
            message += " You survived" 
            done = True
            return self.get_states(), 28, done, message  

        # action handling
        if action <= 2 :
            message += self.change_location(action)

        elif action == 6 :
            message += self.hiding()

        else :
            action_str = self.actions[action]
            found, message = self.stats.search_items(action_str, self.get_location())

            if found :
                # adding to inventory and substracting from location
                self.stats.inventory[action_str] += 1
                self.stats.items[action_str].update_percentage(self.get_location(), 1)

        # zombie attack
        if self.alive and self.actions[action] != "hide" :
            message += self.zombie_attack()

        # end turn
        if self.turn >= 4 :
            # hunger
            if self.alive :
                message += self.eat_food()
            if self.alive :
                self.day += 1
                self.turn = 0

          
        # reward attribution
        reward = 0
        if not self.alive :
            done = True
            reward = -3 * (self.max_day - self.day)
        
        elif self.day == self.max_day :
            message += "\n You survived"
            done = True
            reward = 28

        self.turn += 1
        states = self.get_states()
        return states, reward, done, message



    def get_states(self) -> np.ndarray:
        """
        Returnt the actual game states
        """
        states = np.array([self.alive, self.day / self.max_day, self.turn / 4])
        
        location = np.zeros((3))
        location[self.location] = 1

        if self.normalize :
            stats_states = self.stats.get_stats_normalized(self.max_amount)
        else :
            stats_states = self.stats.get_stats()

        all_states = np.concatenate([states, location, stats_states])
        return all_states
    
    
    def show_board(self):
        """
        Return a human understandable version of the board
        """
        board = {
            "game_info" : {
                "is_alive" : self.alive,
                "day/7" : self.day,
                "turn/3" : self.turn,
                "is_city" : self.location == 0,
                "is_suburbs" : self.location == 1,
                "is_mall" : self.location == 2,
            },
            "inventory" : {
                "inv_food" : self.stats.inventory["food"],
                "inv_gas" : self.stats.inventory["gas"],
                "inv_ammo" : self.stats.inventory["ammo"],
            } ,

            "city" : self.stats.get_location("city"),
            "suburbs" : self.stats.get_location("suburbs"),
            "mall" : self.stats.get_location("mall"),
        }

        return board