import pygame
from settings import *
from entity import Entity
from support import *

class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_animation, add_exp):
        super().__init__(groups)

        self.sprite_type = 'enemy'

        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites

        #stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # interaction
        self.attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_animation = trigger_death_animation
        self.add_exp = add_exp

        #invincibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

        # sounds
        self.dead_sound = pygame.mixer.Sound('../audio/dead.wav')
        self.hit_sound = pygame.mixer.Sound('../audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.dead_sound.set_volume(0.7)
        self.hit_sound.set_volume(0.7)
        self.attack_sound.set_volume(0.7)

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': [],}
        main_path = f'../graphics/monsters/{name}/'
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(main_path + animation)

    def get_player_distance_and_direction(self, player):
        enemy_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(player.rect.center)
        distance = (player_vector - enemy_vector).magnitude()
        if distance > 0:
            direction = (player_vector - enemy_vector).normalize()
        else:
            direction = pygame.math.Vector2()
        return (distance, direction)

    def get_status(self, player):
        distance = self.get_player_distance_and_direction(player)[0]

        if distance <= self.attack_radius and self.attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius: self.status = 'move'
        else: self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'move':
            self.direction = self.get_player_distance_and_direction(player)[1]
        else: self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.attack = False
            self.frame_index = 0
            
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        if not self.vulnerable:
            alpha = self.wave_values()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def enemy_attack_cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_damage(self , player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_and_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_dead(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_animation(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            self.dead_sound.play()

    def hit_react(self):
        if not self.vulnerable:
            self.direction *= -self.resistance


    def update(self):
        self.hit_react()
        self.move(self.speed)
        self.animate()
        self.enemy_attack_cooldown()
        self.check_dead()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)