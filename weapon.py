import pygame
import math
import random
import constants

class Weapon():
    def __init__(self, image, bullet_image):
        self.original_image = image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.bullet_image = bullet_image
        self.rect = self.image.get_rect()
        self.fired = False
        self.last_shot = pygame.time.get_ticks()
        self.facing_left = False

    def update(self, player):
        shot_cooldown = 300
        bullet = None
        self.rect.center = player.rect.center

        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.centerx
        y_dist = -(pos[1] - self.rect.centery) #negative jo pygame y kordinatas palielinas leja ekranam
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        self.facing_left = x_dist < 0
        #get mouse click
        if pygame.mouse.get_pressed()[0] and self.fired == False and (pygame.time.get_ticks() - self.last_shot >= shot_cooldown):
            bullet = Bullet(self.bullet_image, self.rect.centerx, self.rect.centery, self.angle)
            self.fired = True
            self.last_shot = pygame.time.get_ticks()
        #reset mouse click
        if pygame.mouse.get_pressed()[0] == False:
            self.fired = False

        return bullet

    def draw(self, surface):
        # Start from original image
        base_image = self.original_image

        # If aiming left, flip vertically so it’s not upside down
        if self.facing_left:
            base_image = pygame.transform.flip(base_image, False, True)

        # Rotate towards mouse
        self.image = pygame.transform.rotate(base_image, self.angle)

        # Draw centered
        surface.blit(
            self.image,
            (
                self.rect.centerx - self.image.get_width() // 2,
                self.rect.centery - self.image.get_height() // 2 +10
            )
        )

class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #calculate the hor and ver speeds based on angle
        self.dx = math.cos(math.radians(self.angle)) * constants.BULLET_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.BULLET_SPEED) # neg becaus pygame y coordinates increase down the screen

    def update(self, screen_scroll, obstacle_tiles, enemy_list):
        #reset variables
        damage = 0
        damage_pos = None

        #reposition based on speed
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy

        #check for collision between BULLET and tile walls
        for obstacle in obstacle_tiles:
            if obstacle[1].colliderect(self.rect):
                self.kill()

        #check if bullet offscreen
        if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()

        #check collision between bullet and enemies
        for enemy in enemy_list:
            if enemy.rect.colliderect(self.rect) and enemy.alive :
                damage_pos = enemy.rect
                damage = 10 + random.randint(-5, 5)
                enemy.health -= damage
                enemy.hit = True
                self.kill()
                break

        return damage, damage_pos



    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2)),
                                  self.rect.centery - int(self.image.get_height() / 2)))


class Fireball(pygame.sprite.Sprite):
    def __init__(self, image, x, y, target_x, target_y):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = image
        self.x_dist = target_x - x
        self.y_dist = -(target_y - y)
        self.angle = math.degrees(math.atan2(self.y_dist,self.x_dist))
        self.image = pygame.transform.rotate(self.original_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        #calculate the hor and ver speeds based on angle
        self.dx = math.cos(math.radians(self.angle)) * constants.FIREBALL_SPEED
        self.dy = -(math.sin(math.radians(self.angle)) * constants.FIREBALL_SPEED) # neg becaus pygame y coordinates increase down the screen

    def update(self, screen_scroll, player):

        #reposition based on speed
        self.rect.x += screen_scroll[0] + self.dx
        self.rect.y += screen_scroll[1] + self.dy


        #check if fireball is offscreen
        if self.rect.right < 0 or self.rect.left > constants.SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > constants.SCREEN_HEIGHT:
            self.kill()

        #check collision between fireball and player
        if player.rect.colliderect(self.rect) and player.hit == False:
            player.hit = True
            player.last_shot = pygame.time.get_ticks()
            player.health -= 10
            pygame.mixer.Sound("assets/audio/damaged.mp3").play()
            self.kill()


    def draw(self, surface):
        surface.blit(self.image, ((self.rect.centerx - int(self.image.get_width() / 2)),
                                  self.rect.centery - int(self.image.get_height() / 2)))
