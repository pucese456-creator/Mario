import pygame
import sys
import os

pygame.init()

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
GRAVEDAD = 0.8
VELOCIDAD_SALTO = -15
VELOCIDAD_MOVIMIENTO = 5

# Colores
CIELO = (107, 140, 255)
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (200, 0, 0)
ROJO_CLARO = (255, 100, 100)
MARRON = (139, 69, 19)

class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidad_y = 0
        self.en_suelo = False
        self.direccion = 1
        self.animacion_frame = 0
        self.animacion_contador = 0
        self.vidas = 3
        self.puntos = 0

        # Sprites por defecto (debug)
        sprite_quieto = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(sprite_quieto, ROJO, (16, 16), 15)
        pygame.draw.circle(sprite_quieto, BLANCO, (16, 16), 5)

        sprite_caminando = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(sprite_caminando, (0, 255, 0), (2, 2, 28, 28))
        pygame.draw.line(sprite_caminando, BLANCO, (5, 5), (27, 27), 4)
        pygame.draw.line(sprite_caminando, BLANCO, (27, 5), (5, 27), 4)

        # Nombres actualizados
        nombres_quieto = ["mario_idle.png"]
        nombres_caminando = ["mario_smal_walking.png"]

        for nombre in nombres_quieto:
            ruta = os.path.join("assets", nombre)
            if os.path.exists(ruta):
                try:
                    sprite_quieto = pygame.image.load(ruta).convert_alpha()
                    print(f"✅ Cargado: {nombre}")
                except:
                    print(f"❌ Error cargando: {nombre}")

        for nombre in nombres_caminando:
            ruta = os.path.join("assets", nombre)
            if os.path.exists(ruta):
                try:
                    sprite_caminando = pygame.image.load(ruta).convert_alpha()
                    print(f"✅ Cargado: {nombre}")
                except:
                    print(f"❌ Error cargando: {nombre}")

        escala = 0.4
        ancho = int(sprite_quieto.get_width() * escala)
        alto = int(sprite_quieto.get_height() * escala)

        self.sprite_quieto = pygame.transform.scale(sprite_quieto, (ancho, alto))
        self.sprite_caminando = pygame.transform.scale(sprite_caminando, (ancho, alto))

        self.sprites_derecha = [self.sprite_quieto, self.sprite_caminando]
        self.sprites_izquierda = [
            pygame.transform.flip(self.sprite_quieto, True, False),
            pygame.transform.flip(self.sprite_caminando, True, False)
        ]

        self.sprite_saltando = self.sprite_quieto
        self.sprite_saltando_izq = self.sprites_izquierda[0]

        self.ancho = ancho
        self.alto = alto

    def mover(self, teclas, plataformas):
        moviendo = False

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x -= VELOCIDAD_MOVIMIENTO
            self.direccion = -1
            moviendo = True
            if self.x < 0:
                self.x = 0

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x += VELOCIDAD_MOVIMIENTO
            self.direccion = 1
            moviendo = True
            if self.x > ANCHO - self.ancho:
                self.x = ANCHO - self.ancho

        if moviendo and self.en_suelo:
            self.animacion_contador += 1
            if self.animacion_contador >= 2:
                self.animacion_frame = 1 if self.animacion_frame == 0 else 0
                self.animacion_contador = 0
        else:
            self.animacion_frame = 0
            self.animacion_contador = 0

        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.en_suelo:
            self.velocidad_y = VELOCIDAD_SALTO
            self.en_suelo = False

        self.velocidad_y += GRAVEDAD
        self.y += self.velocidad_y

        self.en_suelo = False
        rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)

        for plataforma in plataformas:
            rect_plataforma = pygame.Rect(plataforma)
            if rect_jugador.colliderect(rect_plataforma):
                if self.velocidad_y > 0:
                    self.y = plataforma[1] - self.alto
                    self.velocidad_y = 0
                    self.en_suelo = True

        if self.y > ALTO:
            self.vidas -= 1
            self.y = 100
            self.x = 100
            self.velocidad_y = 0

    def dibujar(self, pantalla):
        if not self.en_suelo:
            sprite = self.sprite_saltando if self.direccion == 1 else self.sprite_saltando_izq
        else:
            sprite = self.sprites_derecha[self.animacion_frame] if self.direccion == 1 else self.sprites_izquierda[self.animacion_frame]

        pantalla.blit(sprite, (int(self.x), int(self.y)))

        fuente = pygame.font.Font(None, 24)
        texto = fuente.render(f"Frame: {self.animacion_frame}", True, NEGRO)
        pantalla.blit(texto, (10, 10))

class Menu:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fuente_titulo = pygame.font.Font(None, 90)
        self.fuente_boton = pygame.font.Font(None, 50)
        self.boton_jugar = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 20, 300, 80)
        self.hover = False

    def dibujar(self):
        for y in range(ALTO):
            color = (20 + int((107-20) * y/ALTO),
                     20 + int((140-20) * y/ALTO),
                     50 + int((255-50) * y/ALTO))
            pygame.draw.line(self.pantalla, color, (0, y), (ANCHO, y))

        titulo = self.fuente_titulo.render("SUPER MARIO", True, ROJO)
        rect_titulo = titulo.get_rect(center=(ANCHO // 2, 120))
        self.pantalla.blit(titulo, rect_titulo)

        subtitulo = pygame.font.Font(None, 40).render("BROS 3", True, BLANCO)
        rect_sub = subtitulo.get_rect(center=(ANCHO // 2, 170))
        self.pantalla.blit(subtitulo, rect_sub)

        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.boton_jugar.collidepoint(mouse_pos)
        color_boton = ROJO_CLARO if self.hover else ROJO

        pygame.draw.rect(self.pantalla, color_boton, self.boton_jugar, border_radius=15)
        pygame.draw.rect(self.pantalla, BLANCO, self.boton_jugar, 5, border_radius=15)

        texto_jugar = self.fuente_boton.render("JUGAR", True, BLANCO)
        rect_texto = texto_jugar.get_rect(center=self.boton_jugar.center)
        self.pantalla.blit(texto_jugar, rect_texto)

    def manejar_click(self, pos):
        if self.boton_jugar.collidepoint(pos):
            return "jugar"
        return None

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("🍄 Super Mario Bros 3")
        self.reloj = pygame.time.Clock()

        self.estado = "menu"
        self.menu = Menu(self.pantalla)
        self.jugador = Jugador(100, 400)

        self.plataformas = [
            (0, 550, ANCHO, 50),
            (200, 450, 150, 20),
            (450, 380, 120, 20),
            (150, 280, 100, 20),
            (400, 200, 150, 20),
            (650, 320, 120, 20),
        ]

    def ejecutar(self):
        while True:
            self.reloj.tick(FPS)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()