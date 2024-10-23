import pygame
import random


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Finite State")
clock = pygame.time.Clock()
dt = 0

center = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2) 

class Entity:
    def __init__(self, name, shape, attack, health, pos):
        self.name = name    
        self.shape = shape      
        self.attack = attack 
        self.health = health 
        self.pos = pos
    
    def take_damage(self, damage):
        self.health -= damage

    def is_alive(self):
        return self.health > 0
    
    def get_attack(self):
        return self.attack


class NPC(Entity):
    def __init__(self, name, shape, attack, health, pos):
        super().__init__(name, shape, attack, health, pos)
        self.current_state = 0
        self.next_state = 0
        self.gold = 0

    def take_damage(self, damage):
        self.health -= damage


    def ai(self, resource, base):
        if self.is_alive():
            # column 0 has gold, column 1 is has no gold, column 2 base is attacked

            table = [ [1, 2, 3],  #just spawned
                      [1, 2, 3],  #go deliver gold
                      [1, 2, 3],  #go and mine
                      [1, 2, 3]]  #defend base
            
            self.current_state = table[self.current_state][self.next_state]
            
            distance_to_resource = self.pos.distance_to(resource.pos)
            distance_to_base = self.pos.distance_to(base.pos)
            threshold = 5  


            self.check_gold()
            match self.current_state:
                case 0: #state just spawned
                    pass
                case 1: #go deliver gold
                    if distance_to_base > threshold:
                        self.move(base.pos)
                    elif distance_to_base <= threshold:
                        self.drop_gold()
                        self.check_gold()
                case 2: #go and mine
                    if distance_to_resource > threshold:
                        self.move(resource.pos)
                    elif distance_to_resource <= threshold:
                        self.mine()
                        self.check_gold()
                case 3:  # defend base
                    if base.attacker_list:  
                        enemy = base.attacker_list[0]  
                        distance_to_enemy = self.pos.distance_to(enemy.pos)
                        threshold = 50
                        if distance_to_enemy > threshold:
                            self.move(enemy.pos)
                        elif distance_to_enemy <= threshold:
                            enemy.take_damage(self)
                            if not enemy.is_alive():
                                base.attacker_list.remove(enemy)
                                enemies.remove_entity(enemy) 
                    self.check_gold()
            self.draw()


    def check_gold(self):
        if self.gold >= 1:
            self.next_state = 0
        else:
            self.next_state = 1
    def mine(self):
        self.gold += 1  
    
    def drop_gold(self):
        self.gold = 0  

    def move(self, target_pos):
        if target_pos.x > self.pos.x:
            self.pos.x += 100 * dt
        elif target_pos.x < self.pos.x:
            self.pos.x -= 100 * dt

        if target_pos.y > self.pos.y:
            self.pos.y += 100 * dt
        elif target_pos.y < self.pos.y:
            self.pos.y -= 100 * dt


    def draw(self):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), 5)


class Raider(Entity):
    def __init__(self, name, shape, attack, health, pos):
        super().__init__(name, shape, attack, health, pos)
        self.current_state = 0
        self.next_state = 0
        self.grudge_list = []


    def take_damage(self, npc):
        self.health -= npc.get_attack()



        for raiders in enemies.entity_list:
            if npc not in self.grudge_list:
                raiders.grudge_list.append(npc)
                raiders.next_state = 1

        if self.health <= 0:
            print(f"{self.name} is dead!")

    def ai(self, base):
        if self.is_alive():
            
            table = [ [1, 2],  #state just spawned
                      [1, 2],  #state attacking base
                      [1, 2]]  #state defending self
            
            self.current_state = table[self.current_state][self.next_state]
            
            distance_to_base = self.pos.distance_to(base.pos)
            threshold = 100  

            
            match self.current_state:
                
                case 0: #curr state just spawned
                    pass
                case 1: #curr state is attaking base
                    if distance_to_base > threshold:
                        self.move(base.pos)
                    else:
                        self.attack_base(base)

                case 2: #curr state is defending self
                    if self.grudge_list:
                        grudge = self.grudge_list[0]  
                        distance_to_enemy = self.pos.distance_to(grudge.pos)
                        threshold = 50
                        if distance_to_enemy > threshold:
                            self.move(grudge.pos)
                        elif distance_to_enemy <= threshold:
                            grudge.take_damage(self.get_attack())
                            if not grudge.is_alive():
                                for raiders in enemies.entity_list:
                                    if grudge in raiders.grudge_list:
                                        raiders.grudge_list.remove(grudge)
                                allies.remove_entity(grudge) 
                                # print("Removing...")
                                print(self.grudge_list)
                    else:
                        self.next_state = 0
            self.draw()
            

    def attack_base(self, base):
        base.take_damage(self)

    def move(self, target_pos):
        if target_pos.x > self.pos.x:
            self.pos.x += 100 * dt
        elif target_pos.x < self.pos.x:
            self.pos.x -= 100 * dt

        if target_pos.y > self.pos.y:
            self.pos.y += 100 * dt
        elif target_pos.y < self.pos.y:
            self.pos.y -= 100 * dt
        
        


    def draw(self):
        pygame.draw.circle(screen, (176, 224, 230), (int(self.pos.x), int(self.pos.y)), 5)
        

class Townhall(Entity):
    def __init__(self, name, shape, attack, health, pos):
        super().__init__(name, shape, attack, health, pos)
        self.attacker_list = []

    def take_damage(self, raider):
        self.health -= raider.get_attack()
        if raider not in self.attacker_list:
            self.attacker_list.append(raider)

        for npc in allies.entity_list:
            npc.next_state = 2

        if self.health <= 0:
            print(f"{self.name} is dead!")

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 0 , 0), (int(self.pos.x), int(self.pos.y)), 50)

class Resource(Entity):
    def __init__(self, name, shape, attack, health, pos):
        super().__init__(name, shape, attack, health, pos)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 215, 0), (int(self.pos.x), int(self.pos.y)), 20)

class Faction:
    def __init__(self, name, entity_list=None):
        self.name = name    
        self.entity_list = entity_list if entity_list is not None else []

    def add_entity(self, entity):
        self.entity_list.append(entity)

    def remove_entity(self, entity):
        self.entity_list.remove(entity)

def spawn(screen, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            pos = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (255, 215, 0), (pos[0], pos[1]), 20)

townhall = Townhall("Townhall", "Circle", 0, 99999, pygame.Vector2(center.x, center.y - 100))

goldmine = Resource("Gold", "Circle", 0, 999999, pygame.Vector2(center.x, center.y + 100)) 

enemies = Faction("Enemy", [])
allies = Faction("Allies", []) 

max_npcs = 10
spawn_interval_npc = 1300  
time_since_last_spawn_npc = 0 

max_raiders = 5
spawn_interval_raiders = 3000  
time_since_last_spawn_raiders = 0 

spawn_coordinates = [ [0,800, 0, 50],
                      [0,800, 550, 600],
                      [0, 50, 0, 600],
                      [750,800, 0, 600]]


x = random.choice(spawn_coordinates)

run = True

#Game loop
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        spawn(screen, event)

    screen.fill((0, 0, 0))

    townhall.draw(screen)
    goldmine.draw(screen)

    dt = clock.tick(60) / 1000  

    time_since_last_spawn_npc += dt * 1000  
    time_since_last_spawn_raiders += dt * 1000  

    if len(allies.entity_list) < max_npcs and time_since_last_spawn_npc > spawn_interval_npc:
        x = random.choice(spawn_coordinates)
        new_npc = NPC("Peasant", "Circle", 15, 50, pygame.Vector2(random.randint(x[0],x[1]),random.randint(x[2],x[3])))
        allies.add_entity(new_npc) 
        time_since_last_spawn_npc = 0  
    
    if len(enemies.entity_list) < max_raiders and time_since_last_spawn_raiders > spawn_interval_raiders:
        x = random.choice(spawn_coordinates)
        new_npc = Raider("Raider", "Circle", 12.5, 50, pygame.Vector2(random.randint(x[0],x[1]),random.randint(x[2],x[3])))
        enemies.add_entity(new_npc) 
        time_since_last_spawn_raiders = 0  

    for npc in allies.entity_list:
        npc.ai(goldmine, townhall) 

    for raiders in enemies.entity_list:
        raiders.ai(townhall) 

    pygame.display.update()

pygame.quit()
