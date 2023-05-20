''' PRIMER OBJETIVO: CREAR JUEGO DE FLAPPY BIRD

Modificaciones conseguidas:
- Aparece el Score
- Aparece Game Over
- Te mueres si tocas el techo o el suelo
- Cada vez el juego va más rápido
- Cerezas con power-ups
- Fantasma que elimina '''

# Importar las bibliotecas necesarias
import pygame, sys, time, random
from pygame.locals import *
import math

# Inicializar pygame
pygame.init()

# Definir el tamaño de la ventana del juego
width = 500
height = 700

# Crear la superficie de juego
play_surface = pygame.display.set_mode((width, height))

# Cargar las imágenes del fondo, del pájaro, y de los tubos superior e inferior
background_image = pygame.image.load("back.png").convert()
bird_image = pygame.image.load("bird.png").convert_alpha()
top_pipe = pygame.image.load("pipe_top.png").convert_alpha()
bot_pipe = pygame.image.load("pipe_bot.png").convert_alpha()
cherry_image = pygame.image.load("cherry.png").convert_alpha()
phantom_image = pygame.image.load("phantom.png").convert_alpha()

# Definir la tasa de fotogramas por segundo (fps)
fps = pygame.time.Clock()

# Función para generar una altura aleatoria para los tubos
def pipe_random_height():
    pipe_h = [random.randint(200,(height/2)-20), random.randint((height/2)+20, height-200)]
    return pipe_h

def game_over(score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Game Over. Score: {score}", True, (255, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (width // 2, height // 2)
    play_surface.blit(text, text_rect)
    pygame.display.update()
    time.sleep(2)
    pygame.quit()
    sys.exit()


# Función principal del juego
def main():
    # Definir la puntuación inicial, la posición del jugador, la gravedad, la velocidad, el salto, y el aumento de velocidad
    score = 0
    player_pos = [100, 350]
    gravity = 1
    speed = 0
    jump = -30
    speed_increase = 1

    # Definir la posición inicial del primer tubo
    pipe_pos = 500
    pipe_width = 50
    pipe_height = pipe_random_height()

    # Bucle principal del juego
    run = True
    while run:
        # Comprobar si se ha pulsado el botón de salir del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Comprobar si se ha pulsado la tecla de espacio para hacer que el pájaro salte
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        speed += jump

        # Aumentar la velocidad gradualmente
        speed += speed_increase

        # Aplicar la fuerza de la gravedad
        speed += gravity
        speed *= 0.95
        player_pos[1] += speed

        # Mover el tubo hacia la izquierda y crear un nuevo tubo si el tubo actual ha desaparecido de la pantalla
        if pipe_pos >= -20:
            pipe_pos -= 10
        else:
            pipe_pos = 500
            pipe_height = pipe_random_height()
            score += 10
        
        # Generar una cereza aleatoria en algún momento durante el juego
        if pipe_pos == 100: 
            cherry_pos = [random.randint(300, 500), random.randint(-100, 800)]

        # Generar fantasma en un momento del juego
        if (pipe_pos == 100) and (score % 10 == 0):
            phantom_pos = [random.randint(300, 500), random.randint(300, 600)]

        # Mostrar el fondo
        play_surface.blit(background_image, [0, 0])

        # Mostrar los tubos
        play_surface.blit(top_pipe, (pipe_pos, -pipe_height[0]))
        play_surface.blit(bot_pipe, (pipe_pos, pipe_height[1]))

        # Mostrar el pájaro
        play_surface.blit(bird_image, (int(player_pos[0]), int(player_pos[1])))
        
        # Mostrar la cereza en la pantalla si está presente en la posición generada aleatoriamente
        if 'cherry_pos' in locals():
            if cherry_pos[0] < 500:
                play_surface.blit(cherry_image, cherry_pos)
                cherry_pos[0] -= 10

        # Comprobar si el pájaro ha colisionado con la cereza y, si es así, 
        # agregar 5 puntos a la puntuación del jugador y eliminar la cereza de la pantalla
        if 'cherry_pos' in locals():
            cherry_rect = pygame.Rect(cherry_pos[0], cherry_pos[1], cherry_image.get_width(), cherry_image.get_height())
            if cherry_rect.colliderect(pygame.Rect(player_pos[0], player_pos[1], bird_image.get_width(), bird_image.get_height())):
                score += 5
                del cherry_pos

        # Mostrar el fantasma en la pantalla si está presente en la posición generada aleatoriamente
        if 'phantom_pos' in locals():
            if phantom_pos[0] < 500:
                play_surface.blit(phantom_image, phantom_pos)
                phantom_pos[0] -= 10
                phantom_pos[1] += 20 * math.sin(phantom_pos[0] / 50)  # movimiento sinusoidal en Y

        # Comprobar si el pájaro ha colisionado con el fantasma y, si es así, 
        # La partida terminará y se muestra en pantalla el mensaje de game over junto con la puntuación obtenida
        if 'phantom_pos' in locals():
            phantom_rect = pygame.Rect(phantom_pos[0], phantom_pos[1], phantom_image.get_width(), phantom_image.get_height())
            if phantom_rect.colliderect(pygame.Rect(player_pos[0], player_pos[1], bird_image.get_width(), bird_image.get_height())):
                # Mostrar pantalla de Game Over
                game_over(score)

                # Esperar 2 segundos antes de cerrar el juego
                time.sleep(2)
                pygame.quit()
                sys.exit()
                
        # Comprobar si ha habido una colisión entre el pájaro y un tubo
        if player_pos[1] <= (-pipe_height[0]+500) or player_pos[1] >= pipe_height[1]:
            if player_pos[0] in list(range(pipe_pos, pipe_pos+pipe_width)):
                # Mostrar pantalla de Game Over
                game_over(score)

                # Esperar 2 segundos antes de cerrar el juego
                time.sleep(2)
                pygame.quit()
                sys.exit()

        # Si el jugador toca el techo o el piso, su posición se fija y su velocidad se reinicia a cero
        if player_pos[1] >= height:
            player_pos[1] = height
            speed = 0
            # Agregar una verificación adicional para perder si toca el borde inferior
            game_over(score)
        elif player_pos[1] <= 0:
            player_pos[1] = 0
            speed = 0
            # Agregar una verificación adicional para perder si toca el borde superior
            game_over(score)

        # Vamos a intentar que el pájaro haga algo
        

        # Mostrar la puntuación actual en la esquina superior izquierda de la pantalla
        font = pygame.font.Font(None, 40)
        text = font.render(f"{score}", 1, (255, 255, 255))
        play_surface.blit(text, (250, 10))

        pygame.display.flip()
        fps.tick(25)
    
# Llamar a la función principal para ejecutar el juego
main()

# Cerrar Pygame y salir del juego
pygame.quit()

'''
SEGUNDO OBJETIVO: QUE UNA IA JUEGUE A FLAPPY BIRD

Las variables de entrada para la IA en el juego Flappy Bird son las siguientes:
    - La posición actual del jugador (posición del pájaro).
    - La velocidad actual del jugador (velocidad del pájaro).
    - La altura de los dos tubos que aparecen en la pantalla.
    - La posición de la cereza en la pantalla, si está presente.
    - La posición del fantasma en la pantalla, si está presente.
    - La puntuación actual del jugador.

Las variables de salida para la IA en el juego Flappy Bird son las siguientes:
    - Eventos del teclado: la tecla de espacio para hacer que el pájaro salte.
'''