import pygame
import sys
import random
import os
from player import Jugador

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60
ANCHO_NIVEL = 4000

# Colores
CIELO = (107, 140, 255)
MARRON = (139, 69, 19)
VERDE = (34, 139, 34)
ROJO = (200, 0, 0)
AMARILLO = (255, 200, 0)
VERDE_OSCURO = (50, 120, 50)
GRIS = (100, 100, 100)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)

# 🍄 NIVEL 1-1 AUTÉNTICO DE SUPER MARIO BROS 3
NIVELES = {
    1: {
        "nombre": "World 1-1 - Grass Land",
        "plataformas": [
            (0, 550, ANCHO_NIVEL, 50),
            (580, 380, 80, 20),
            (700, 380, 80, 20),
            (820, 380, 80, 20),
            (1100, 480, 80, 20),
            (1200, 420, 80, 20),
            (1300, 360, 80, 20),
            (1450, 300, 120, 20),
            (1620, 360, 80, 20),
            (1720, 420, 80, 20),
            (1820, 480, 80, 20),
            (2100, 450, 100, 20),
            (2300, 400, 100, 20),
            (2700, 490, 60, 20),
            (2760, 450, 60, 20),
            (2820, 410, 60, 20),
            (2880, 370, 60, 20),
            (2940, 330, 60, 20),
            (3000, 290, 60, 20),
            (3100, 250, 120, 20),
            (3260, 290, 60, 20),
            (3320, 330, 60, 20),
            (3380, 370, 60, 20),
            (3440, 410, 60, 20),
            (3500, 450, 60, 20),
            (3560, 490, 60, 20),
        ],
        "bloques": [
            (300, 360), (360, 360),
            (620, 290), (740, 290), (860, 290),
            (1000, 330), (1060, 330),
            (1480, 210),
            (1680, 270), (1740, 270),
            (2140, 360), (2200, 360), (2340, 310),
            (2500, 360), (2560, 360), (2620, 360),
            (2800, 320), (2920, 240), (3040, 200),
            (3300, 240), (3420, 280)
        ],
        "tuberias": [
            (450, 450, 120, 100),
            (950, 410, 120, 140),
            (2000, 350, 120, 200),
            (2450, 410, 120, 140),
            (3650, 450, 120, 100),
        ],
        "enemigos": [
            (600, 500, "goomba"),
            (900, 500, "goomba"),
            (1400, 500, "goomba"),
            (1900, 500, "goomba"),
            (2600, 500, "goomba"),
            (3000, 500, "goomba"),
        ],
        "monedas": [
            (330, 330), (390, 330), 
            (650, 260), (770, 260), 
            (1200, 370), (1230, 370), (1260, 370),
            (1700, 240), (1730, 240), (1760, 240),
            (2150, 330), (2210, 330),
            (2500, 330), (2560, 330), (2620, 330),
            (2800, 290), (2920, 210), (3040, 170),
            (3300, 210), (3420, 250)
        ],
        "meta": (3800, 500),
        "fondo_arbustos": [
            (200, 530), (500, 530), (800, 530),
            (1200, 530), (1600, 530), (2000, 530),
            (2400, 530), (2800, 530), (3200, 530),
        ],
        "fondo_colinas": [
            (150, 450), (600, 480), (1100, 470),
            (1700, 460), (2200, 475), (2900, 465),
        ],
    }
}

class Bloque:
    def __init__(self, x, y, sprites, sprite_usado=None):
        self.x = x
        self.y = y
        self.sprites = sprites
        self.sprite_usado = sprite_usado
        self.frame_actual = 0
        self.contador_animacion = 0
        self.velocidad_animacion = 8
        self.ancho = 36 
        self.alto = 36
        self.golpeado = False
        self.usado = False
        self.offset_golpe = 0
        self.velocidad_golpe = 0
        self.pending_item = None
        
    def actualizar(self):
        if not self.usado:
            self.contador_animacion += 1
            if self.contador_animacion >= self.velocidad_animacion:
                self.frame_actual = (self.frame_actual + 1) % len(self.sprites)
                self.contador_animacion = 0
        
        if self.offset_golpe != 0:
            self.offset_golpe += self.velocidad_golpe
            self.velocidad_golpe += 0.5
            if self.offset_golpe >= 0:
                self.offset_golpe = 0
                self.velocidad_golpe = 0
    
    def golpear(self):
        if not self.usado and self.offset_golpe == 0:
            self.offset_golpe = -10
            self.velocidad_golpe = 0
            self.golpeado = True
            self.usado = True
            self.pending_item = "hongo"
    
    def dibujar(self, pantalla, camara_x=0):
        if self.usado and self.sprite_usado:
            pantalla.blit(self.sprite_usado, (self.x - camara_x, self.y + self.offset_golpe))
        else:
            sprite_actual = self.sprites[self.frame_actual]
            pantalla.blit(sprite_actual, (self.x - camara_x, self.y + self.offset_golpe))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

class Hongo:
    def __init__(self, x, y, sprite):
        self.original_y = y
        self.x = x
        self.y = y
        self.sprite = sprite
        if sprite:
            self.ancho = sprite.get_width()
            self.alto = sprite.get_height()
        else:
            self.ancho = 30
            self.alto = 30
            
        self.velocidad_x = 2
        self.velocidad_y = 0
        self.estado = "saliendo"
        self.contador_salida = 0
        self.altura_salida = 0
        self.activo = True
        
    def actualizar(self, plataformas, tuberias, bloques):
        if not self.activo:
            return

        if self.estado == "saliendo":
            self.altura_salida += 1
            self.y = self.original_y - self.altura_salida
            if self.altura_salida >= self.alto:
                self.estado = "moviendo"
                self.y = self.original_y - self.alto
        elif self.estado == "moviendo":
            # Gravedad
            self.velocidad_y += 0.5
            self.y += self.velocidad_y
            
            # Movimiento horizontal
            self.x += self.velocidad_x
            
            # Colisiones simples (suelo)
            rect_hongo = self.get_rect()
            en_suelo = False
            
            # Colisión con plataformas
            for plataforma in plataformas:
                rect_plat = pygame.Rect(plataforma)
                if rect_hongo.colliderect(rect_plat):
                    if self.velocidad_y > 0: # Cayendo
                        self.y = plataforma[1] - self.alto
                        self.velocidad_y = 0
                        en_suelo = True
            
            # Colisión con bloques
            for bloque in bloques:
                rect_bloque = bloque.get_rect()
                if rect_hongo.colliderect(rect_bloque):
                    # Si choca lateralmente
                    if self.y + self.alto > rect_bloque.top + 5:
                        self.velocidad_x *= -1
                        self.x += self.velocidad_x * 2 # Rebote simple
                    elif self.velocidad_y > 0: # Cayendo encima
                        self.y = rect_bloque.top - self.alto
                        self.velocidad_y = 0
                        en_suelo = True
            
            # Colisión con tuberías
            for tuberia in tuberias:
                rect_tub = tuberia.get_rect()
                if rect_hongo.colliderect(rect_tub):
                    if self.y + self.alto > rect_tub.top + 5:
                        self.velocidad_x *= -1
                        self.x += self.velocidad_x * 2
                    elif self.velocidad_y > 0:
                        self.y = rect_tub.top - self.alto
                        self.velocidad_y = 0
                        en_suelo = True

    def dibujar(self, pantalla, camara_x):
        if not self.activo:
            return
            
        if self.sprite:
            # Si está saliendo, recortar o dibujar detrás del bloque
            # Para simplificar, dibujamos normal pero controlando Y
            pantalla.blit(self.sprite, (int(self.x - camara_x), int(self.y)))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

class Tuberia:
    def __init__(self, x, y, ancho, alto, sprite_tubo=None, sprites_planta=None):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.tiene_planta = alto > 150
        self.frame_planta = 0
        self.contador_planta = 0
        self.planta_visible = False
        self.tiempo_visible = 0
        self.tiempo_escondida = 0
        self.duracion_visible = 180
        self.duracion_escondida = 120
        self.altura_planta = 0
        self.velocidad_subida = 3
        self.margen_lateral = 32
        self.margen_superior = 10
        
        if sprite_tubo:
            self.sprite = pygame.transform.scale(sprite_tubo, (ancho, alto))
        else:
            self.sprite = None
        
        self.sprites_planta = sprites_planta if sprites_planta else []
    
    def get_rect(self):
        return pygame.Rect(
            self.x + self.margen_lateral, 
            self.y + self.margen_superior,
            self.ancho - (self.margen_lateral * 2), 
            self.alto - self.margen_superior
        )
    
    def get_body_rect(self):
        return pygame.Rect(
            self.x + self.margen_lateral, 
            self.y + self.margen_superior,
            self.ancho - (self.margen_lateral * 2), 
            self.alto - self.margen_superior
        )
    
    def get_top_rect(self):
        return pygame.Rect(
            self.x + self.margen_lateral, 
            self.y,
            self.ancho - (self.margen_lateral * 2), 
            20
        )
        
    def actualizar(self):
        if self.tiene_planta and len(self.sprites_planta) >= 2:
            if self.planta_visible:
                self.tiempo_visible += 1
                
                self.contador_planta += 1
                if self.contador_planta >= 8:
                    self.frame_planta = 0 if self.frame_planta == 1 else 1
                    self.contador_planta = 0
                
                if self.tiempo_visible <= 30:
                    self.altura_planta += self.velocidad_subida
                    if self.altura_planta > 100:
                        self.altura_planta = 100
                
                if self.tiempo_visible >= self.duracion_visible - 30:
                    self.altura_planta -= self.velocidad_subida
                    if self.altura_planta < 0:
                        self.altura_planta = 0
                
                if self.tiempo_visible >= self.duracion_visible:
                    self.planta_visible = False
                    self.tiempo_visible = 0
                    self.tiempo_escondida = 0
                    self.frame_planta = 0
                    self.contador_planta = 0
                    self.altura_planta = 0
            else:
                self.tiempo_escondida += 1
                
                if self.tiempo_escondida >= self.duracion_escondida:
                    self.planta_visible = True
                    self.tiempo_escondida = 0
                    self.tiempo_visible = 0
                    self.frame_planta = 0
                    self.contador_planta = 0
                    self.altura_planta = 0
    
    def dibujar(self, pantalla, camara_x):
        x_pantalla = self.x - camara_x
        
        if self.sprite:
            pantalla.blit(self.sprite, (x_pantalla, self.y))
        else:
            pygame.draw.rect(pantalla, (34, 177, 76), (x_pantalla + 8, self.y, self.ancho - 16, self.alto))
            pygame.draw.rect(pantalla, VERDE_OSCURO, (x_pantalla, self.y - 10, self.ancho, 10))
            pygame.draw.rect(pantalla, (50, 200, 100), (x_pantalla + 12, self.y + 5, 8, self.alto - 10), 2)
            pygame.draw.rect(pantalla, (50, 200, 100), (x_pantalla + self.ancho - 20, self.y + 5, 8, self.alto - 10), 2)
        
        if self.tiene_planta and self.planta_visible and len(self.sprites_planta) >= 2:
            frame_index = self.frame_planta % len(self.sprites_planta)
            sprite_actual = self.sprites_planta[frame_index]
            
            planta_x = x_pantalla + (self.ancho // 2) - (sprite_actual.get_width() // 2)
            alto_sprite = sprite_actual.get_height()
            alto_visible = int(alto_sprite * self.altura_planta / 100)
            
            if alto_visible > 0:
                try:
                    rect_recorte = pygame.Rect(0, 0, sprite_actual.get_width(), alto_visible)
                    sprite_recortado = sprite_actual.subsurface(rect_recorte)
                    
                    y_dibujo = self.y - alto_visible + 10
                    pantalla.blit(sprite_recortado, (int(planta_x), int(y_dibujo)))
                except:
                    pass

class Arbusto:
    def __init__(self, x, y, sprite=None):
        self.x = x
        self.y = y
        self.sprite = sprite
        
    def dibujar(self, pantalla, camara_x):
        x_pantalla = self.x - camara_x * 0.3
        
        if self.sprite:
            # Dibujar el sprite centrado en la posición
            ancho = self.sprite.get_width()
            alto = self.sprite.get_height()
            pantalla.blit(self.sprite, (int(x_pantalla - ancho // 2), int(self.y - alto // 2)))
        else:
            pygame.draw.circle(pantalla, (34, 139, 34), (int(x_pantalla), int(self.y)), 15)
            pygame.draw.circle(pantalla, (34, 139, 34), (int(x_pantalla - 12), int(self.y + 5)), 12)
            pygame.draw.circle(pantalla, (34, 139, 34), (int(x_pantalla + 12), int(self.y + 5)), 12)

class Colina:
    def __init__(self, x, y, sprite=None):
        self.x = x
        self.y = y
        self.sprite = sprite
        
    def dibujar(self, pantalla, camara_x):
        x_pantalla = self.x - camara_x * 0.5
        
        if self.sprite:
            # Dibujar sprite anclado al suelo (y es el pico originalmente, ajustamos)
            # En el original, self.y era el pico. El suelo era ALTO - 50 = 550.
            # Queremos que la base del sprite esté en 550.
            ancho = self.sprite.get_width()
            alto = self.sprite.get_height()
            
            # Dibujar con la base en 550
            pantalla.blit(self.sprite, (int(x_pantalla - ancho // 2), 550 - alto))
        else:
            # Fallback (no debería usarse si hay sprites)
            puntos = [
                (x_pantalla - 50, ALTO - 50),
                (x_pantalla, self.y - 30),
                (x_pantalla + 50, ALTO - 50)
            ]
            pygame.draw.polygon(pantalla, (34, 139, 34), puntos)

class Nube:
    def __init__(self, x, y, velocidad, sprite):
        self.x = x
        self.y = y
        self.velocidad = velocidad
        self.sprite = sprite
        self.ancho = sprite.get_width()
        
    def actualizar(self):
        self.x -= self.velocidad
        if self.x + self.ancho < 0:
            self.x = ANCHO + random.randint(50, 200)
            self.y = random.randint(30, 200)
    
    def dibujar(self, pantalla):
        pantalla.blit(self.sprite, (int(self.x), int(self.y)))

class ScorePopup:
    def __init__(self, x, y, texto, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.texto = texto
        self.color = color
        self.tiempo = 0
        self.duracion = 60
    
    def actualizar(self):
        self.tiempo += 1
        self.y -= 0.5
    
    def terminado(self):
        return self.tiempo >= self.duracion
    
    def dibujar(self, pantalla, fuente):
        superficie = fuente.render(self.texto, True, self.color)
        pantalla.blit(superficie, (int(self.x), int(self.y)))
class Enemigo:
    """Clase para enemigos (Goombas) con animación de sprites y aplastamiento"""
    def __init__(self, x, y, tipo="goomba"):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.velocidad = 1
        self.direccion = -1  # -1 izquierda, 1 derecha
        self.ancho = 30
        self.alto = 30
        self.vivo = True
        self.aplastado = False
        self.tiempo_aplastado = 0
        self.duracion_aplastado = 60  # frames que permanece aplastado antes de desaparecer
        
        # Sistema de animación
        self.frame_actual = 0
        self.contador_animacion = 0
        self.velocidad_animacion = 10  # Cambia de frame cada 10 ticks
        
        # Cargar sprites animados
        self.sprites = []
        self.sprite_aplastado = None
        self._cargar_sprites()
    
    def _cargar_sprites(self):
        """Carga gumba1.png, gumba2.png y gumba_aplastado.png desde assets"""
        nombres_sprites = ["gumba1.png", "gumba2.png"]
        
        for nombre in nombres_sprites:
            ruta = os.path.join("assets", nombre)
            if os.path.exists(ruta):
                try:
                    sprite = pygame.image.load(ruta).convert_alpha()
                    escala = 0.3
                    ancho = int(sprite.get_width() * escala)
                    alto = int(sprite.get_height() * escala)
                    sprite = pygame.transform.scale(sprite, (ancho, alto))
                    self.sprites.append(sprite)
                except:
                    pass
        
        # Cargar sprite aplastado
        ruta_aplastado = os.path.join("assets", "gumba_aplastado.png")
        if os.path.exists(ruta_aplastado):
            try:
                sprite = pygame.image.load(ruta_aplastado).convert_alpha()
                escala = 0.3
                ancho = int(sprite.get_width() * escala)
                alto = int(sprite.get_height() * escala)
                self.sprite_aplastado = pygame.transform.scale(sprite, (ancho, alto))
            except:
                pass
        
        # Sprites por defecto si no se cargaron
        if len(self.sprites) == 0:
            for i in range(2):
                sprite_default = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.ellipse(sprite_default, (139, 69, 19), (0, 0, 30, 30))
                pygame.draw.circle(sprite_default, (255, 255, 255), (10, 10), 4)
                pygame.draw.circle(sprite_default, (255, 255, 255), (20, 10), 4)
                pygame.draw.circle(sprite_default, (0, 0, 0), (10, 10), 2)
                pygame.draw.circle(sprite_default, (0, 0, 0), (20, 10), 2)
                self.sprites.append(sprite_default)
        
        if self.sprite_aplastado is None:
            sprite_aplastado_default = pygame.Surface((30, 15), pygame.SRCALPHA)
            pygame.draw.ellipse(sprite_aplastado_default, (139, 69, 19), (0, 0, 30, 15))
            self.sprite_aplastado = sprite_aplastado_default
        
        if len(self.sprites) > 0:
            self.ancho = self.sprites[0].get_width()
            self.alto = self.sprites[0].get_height()
    
    def aplastar(self):
        """Aplasta al Goomba"""
        if not self.aplastado:
            self.aplastado = True
            self.tiempo_aplastado = 0
            self.velocidad = 0
        
    def actualizar(self, plataformas, tuberias=[], bloques=[]):
        """Actualiza posición y animación del enemigo"""
        if not self.vivo:
            return
        
        if self.aplastado:
            # Contar tiempo aplastado
            self.tiempo_aplastado += 1
            if self.tiempo_aplastado >= self.duracion_aplastado:
                self.vivo = False
            return
        
        # Actualizar animación (alterna entre frame 0 y 1)
        self.contador_animacion += 1
        if self.contador_animacion >= self.velocidad_animacion:
            self.frame_actual = (self.frame_actual + 1) % len(self.sprites)
            self.contador_animacion = 0
        
        # Guardar posición anterior
        x_anterior = self.x
        
        # Movimiento horizontal
        self.x += self.velocidad * self.direccion
        
        # Crear rectángulo de colisión
        rect_enemigo = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
        # ===== COLISIÓN CON TUBERÍAS =====
        for tuberia in tuberias:
            rect_tuberia = tuberia.get_rect()
            if rect_enemigo.colliderect(rect_tuberia):
                self.x = x_anterior
                self.direccion *= -1
                break
        
        # ===== COLISIÓN CON BLOQUES =====
        rect_enemigo = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        for bloque in bloques:
            rect_bloque = bloque.get_rect()
            if rect_enemigo.colliderect(rect_bloque):
                self.x = x_anterior
                self.direccion *= -1
                break
        
        # Aplicar gravedad
        self.y += 2
        
        # ===== COLISIÓN CON PLATAFORMAS =====
        rect_enemigo = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        en_plataforma = False
        
        for plataforma in plataformas:
            rect_plataforma = pygame.Rect(plataforma)
            if rect_enemigo.colliderect(rect_plataforma):
                self.y = plataforma[1] - self.alto
                en_plataforma = True
                break
        
        # ===== DETECTAR BORDE DE PLATAFORMA =====
        if en_plataforma:
            # Verificar si hay suelo adelante (prevenir caída)
            pos_adelante_x = self.x + (self.ancho if self.direccion == 1 else -5)
            pos_adelante_y = self.y + self.alto + 10
            
            hay_suelo_adelante = False
            for plataforma in plataformas:
                # Verificar si hay una plataforma debajo de la posición adelante
                if (pos_adelante_x >= plataforma[0] and 
                    pos_adelante_x <= plataforma[0] + plataforma[2] and
                    pos_adelante_y >= plataforma[1] and 
                    pos_adelante_y <= plataforma[1] + plataforma[3]):
                    hay_suelo_adelante = True
                    break
            
            # Si no hay suelo adelante, cambiar de dirección
            if not hay_suelo_adelante:
                self.direccion *= -1
    
    def dibujar(self, pantalla, camara_x):
        """Dibuja el enemigo con sprite animado o aplastado"""
        if not self.vivo:
            return
        
        x_pantalla = self.x - camara_x
        
        if self.aplastado:
            # Dibujar sprite aplastado
            pantalla.blit(self.sprite_aplastado, (int(x_pantalla), int(self.y + self.alto - self.sprite_aplastado.get_height())))
        else:
            # Dibujar sprite actual de la animación
            if len(self.sprites) > 0:
                sprite_actual = self.sprites[self.frame_actual]
                pantalla.blit(sprite_actual, (int(x_pantalla), int(self.y)))
    
    def get_rect(self):
        """Retorna rectángulo de colisión"""
        import pygame
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
    
    def get_cabeza_rect(self):
        """Retorna rectángulo de la cabeza (tercio superior)"""
        import pygame
        altura_cabeza = self.alto // 3
        return pygame.Rect(self.x, self.y, self.ancho, altura_cabeza)

class Moneda:
    def __init__(self, x, y, sprites):
        self.x = x
        self.y = y
        self.sprites = sprites
        self.frame_actual = 0
        self.contador_animacion = 0
        self.velocidad_animacion = 10
        if sprites:
            self.ancho = sprites[0].get_width()
            self.alto = sprites[0].get_height()
        else:
            self.ancho = 35
            self.alto = 35
        self.recogida = False
        
    def actualizar(self):
        if self.recogida:
            return
            
        self.contador_animacion += 1
        if self.contador_animacion >= self.velocidad_animacion:
            self.frame_actual = (self.frame_actual + 1) % len(self.sprites)
            self.contador_animacion = 0
            
    def dibujar(self, pantalla, camara_x):
        if self.recogida:
            return
        
        x_pantalla = self.x - camara_x
        if self.sprites:
            sprite_actual = self.sprites[self.frame_actual]
            pantalla.blit(sprite_actual, (int(x_pantalla), int(self.y)))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

class Juego:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            pass
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("🍄 Super Mario Bros 3 - World 1-1")
        self.reloj = pygame.time.Clock()
        self.nivel_actual = 1
        self.camara_x = 0
        self.musica_activa = False
        self.sonido_power_up = None
        self.sonido_power_down = None
        self.sonido_moneda = None
        self.sonido_salto = None
        self.sonido_lose = None
        self.sonido_golpe = None
        self.popups = []
        self.combo_ultimo_kill = 0
        self.combo_valor = 100
        
        self.cargar_sprites_nubes()
        self.cargar_sprites_bloques()
        self.cargar_sprite_hongo()
        self.cargar_sprites_monedas()
        self.cargar_sprites_arbustos()
        self.cargar_sprite_colina()
        self.cargar_sprite_tubo()
        self.cargar_sprite_piso()
        self.cargar_sprites_planta()
        
        self.cargar_sonidos()
        self.crear_nubes()
        self.cargar_nivel(self.nivel_actual)
        self.reproducir_musica_fondo()

    def reproducir_musica_fondo(self):
        try:
            ruta = os.path.join("musicas", "musica1.mp3")
            if os.path.exists(ruta):
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.musica_activa = True
        except:
            self.musica_activa = False
    
    def cargar_sonidos(self):
        try:
            ruta_up = os.path.join("musicas", "power_up.wav")
            if not os.path.exists(ruta_up):
                ruta_up = os.path.join("musicas", "power up.wav")
            if os.path.exists(ruta_up):
                self.sonido_power_up = pygame.mixer.Sound(ruta_up)
                self.sonido_power_up.set_volume(0.8)
        except:
            self.sonido_power_up = None
        try:
            ruta_down = os.path.join("musicas", "power_down.wav")
            if not os.path.exists(ruta_down):
                ruta_down = os.path.join("musicas", "power down.wav")
            if os.path.exists(ruta_down):
                self.sonido_power_down = pygame.mixer.Sound(ruta_down)
                self.sonido_power_down.set_volume(0.8)
        except:
            self.sonido_power_down = None
        try:
            ruta_coin = os.path.join("musicas", "meneda.wav")
            if not os.path.exists(ruta_coin):
                ruta_coin = os.path.join("musicas", "moneda.wav")
            if os.path.exists(ruta_coin):
                self.sonido_moneda = pygame.mixer.Sound(ruta_coin)
                self.sonido_moneda.set_volume(0.7)
        except:
            self.sonido_moneda = None
        try:
            ruta_salto = os.path.join("musicas", "salto.wav")
            if not os.path.exists(ruta_salto):
                ruta_salto = os.path.join("musicas", "sonido.wav")
            if os.path.exists(ruta_salto):
                self.sonido_salto = pygame.mixer.Sound(ruta_salto)
                self.sonido_salto.set_volume(0.7)
        except:
            self.sonido_salto = None
        try:
            ruta_lose = os.path.join("musicas", "lose.wav")
            if os.path.exists(ruta_lose):
                self.sonido_lose = pygame.mixer.Sound(ruta_lose)
                self.sonido_lose.set_volume(0.9)
        except:
            self.sonido_lose = None
        try:
            ruta_golpe = os.path.join("musicas", "golpe.wav")
            if os.path.exists(ruta_golpe):
                self.sonido_golpe = pygame.mixer.Sound(ruta_golpe)
                self.sonido_golpe.set_volume(0.8)
        except:
            self.sonido_golpe = None

    def matar_mario(self):
        if not self.jugador.muriendo:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            if self.sonido_lose:
                duracion_seg = self.sonido_lose.get_length()
                duracion_frames = max(1, int(duracion_seg * FPS))
                self.jugador.duracion_muerte = duracion_frames
                try:
                    self.sonido_lose.play()
                except:
                    pass
            self.jugador.morir()

    def cargar_sprite_tubo(self):
        ruta = os.path.join("assets", "tubo1.png")
        if os.path.exists(ruta):
            try:
                self.sprite_tubo = pygame.image.load(ruta).convert_alpha()
            except:
                self.sprite_tubo = None
        else:
            self.sprite_tubo = None

    def cargar_sprite_piso(self):
        ruta = os.path.join("assets", "piso1.png")
        if os.path.exists(ruta):
            try:
                self.sprite_piso = pygame.image.load(ruta).convert_alpha()
            except:
                self.sprite_piso = None
        else:
            self.sprite_piso = None

    def cargar_sprites_planta(self):
        self.sprites_planta = []
        nombres = ["rojo_arriba.png", "rojo_arriba2.png"]
        
        for nombre in nombres:
            ruta = os.path.join("assets", nombre)
            if os.path.exists(ruta):
                try:
                    sprite = pygame.image.load(ruta).convert_alpha()
                    escala = 0.5
                    ancho = int(sprite.get_width() * escala)
                    alto = int(sprite.get_height() * escala)
                    sprite = pygame.transform.scale(sprite, (ancho, alto))
                    self.sprites_planta.append(sprite)
                except:
                    pass
        
        if len(self.sprites_planta) < 2:
            for i in range(2):
                planta_default = pygame.Surface((50, 50), pygame.SRCALPHA)
                if i == 0:
                    pygame.draw.circle(planta_default, (200, 0, 0), (25, 25), 20)
                    pygame.draw.circle(planta_default, (255, 255, 255), (25, 25), 8)
                else:
                    pygame.draw.circle(planta_default, (200, 0, 0), (25, 25), 20)
                    pygame.draw.ellipse(planta_default, (255, 255, 255), (10, 15, 30, 20))
                self.sprites_planta.append(planta_default)


    def cargar_sprites_bloques(self):
        self.sprites_bloques = []
        
        for i in range(1, 5):
            ruta = os.path.join("assets", f"bloque{i}.png")
            if os.path.exists(ruta):
                try:
                    sprite = pygame.image.load(ruta).convert_alpha()
                    sprite = pygame.transform.scale(sprite, (36, 36))
                    self.sprites_bloques.append(sprite)
                except:
                    pass
        
        if len(self.sprites_bloques) < 4:
            for i in range(4):
                bloque_default = pygame.Surface((36, 36))
                bloque_default.fill(AMARILLO)
                fuente = pygame.font.Font(None, 32)
                texto = fuente.render("?", True, (139, 69, 19))
                rect_texto = texto.get_rect(center=(18, 18))
                bloque_default.blit(texto, rect_texto)
                self.sprites_bloques.append(bloque_default)
        
        # Cargar sprite de bloque usado
        self.sprite_bloque_usado = None
        ruta_usado = os.path.join("assets", "usados.png")
        if os.path.exists(ruta_usado):
            try:
                sprite = pygame.image.load(ruta_usado).convert_alpha()
                self.sprite_bloque_usado = pygame.transform.scale(sprite, (36, 36))
            except:
                pass
        
        if self.sprite_bloque_usado is None:
            # Fallback
            self.sprite_bloque_usado = pygame.Surface((36, 36))
            self.sprite_bloque_usado.fill((100, 100, 100)) # Gris
            pygame.draw.rect(self.sprite_bloque_usado, (50, 50, 50), (0, 0, 36, 36), 2)

    def cargar_sprite_hongo(self):
        self.sprite_hongo = None
        ruta = os.path.join("assets", "hongo.png")
        if os.path.exists(ruta):
            try:
                sprite = pygame.image.load(ruta).convert_alpha()
                self.sprite_hongo = pygame.transform.scale(sprite, (36, 36))
            except:
                pass
        
        if self.sprite_hongo is None:
            self.sprite_hongo = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite_hongo, (255, 0, 0), (18, 18), 18)
            pygame.draw.circle(self.sprite_hongo, (255, 255, 255), (12, 12), 6)

    def cargar_sprites_monedas(self):
        self.sprites_monedas = []
        for i in range(1, 6):
            ruta = os.path.join("assets", f"moneda{i}.png")
            if os.path.exists(ruta):
                try:
                    sprite = pygame.image.load(ruta).convert_alpha()
                    # Escalar a un tamaño un poco más grande
                    sprite = pygame.transform.scale(sprite, (35, 35))
                    self.sprites_monedas.append(sprite)
                except:
                    pass
        
        # Sprite por defecto si no se encuentran las imágenes
        if not self.sprites_monedas:
            moneda_default = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(moneda_default, (255, 215, 0), (17, 17), 15) # Oro
            pygame.draw.circle(moneda_default, (0, 0, 0), (17, 17), 15, 1) # Borde
            self.sprites_monedas.append(moneda_default)

    def cargar_sprites_arbustos(self):
        self.sprites_arbustos = []
        
        ruta = os.path.join("assets", "arbustos.png")
        if os.path.exists(ruta):
            try:
                sprite = pygame.image.load(ruta).convert_alpha()
                factor = 50 / sprite.get_height()
                nuevo_ancho = int(sprite.get_width() * factor)
                sprite = pygame.transform.scale(sprite, (nuevo_ancho, 50))
                self.sprites_arbustos.append(sprite)
            except:
                pass
        
        if not self.sprites_arbustos:
            self.sprites_arbustos = [None] # Fallback para dibujar círculos

    def cargar_sprite_colina(self):
        ruta = os.path.join("assets", "mcactus.png")
        if os.path.exists(ruta):
            try:
                self.sprite_colina = pygame.image.load(ruta).convert_alpha()
                alto_objetivo = 150
                factor = alto_objetivo / self.sprite_colina.get_height()
                nuevo_ancho = int(self.sprite_colina.get_width() * factor)
                self.sprite_colina = pygame.transform.scale(self.sprite_colina, (nuevo_ancho, alto_objetivo))
            except:
                self.sprite_colina = None
        else:
            self.sprite_colina = None

    def cargar_sprites_nubes(self):
        self.sprites_nubes = []
        
        for i in range(1, 4):
            ruta = os.path.join("assets", f"nube{i}.png")
            if os.path.exists(ruta):
                try:
                    sprite = pygame.image.load(ruta).convert_alpha()
                    escala = 0.5
                    ancho = int(sprite.get_width() * escala)
                    alto = int(sprite.get_height() * escala)
                    sprite = pygame.transform.scale(sprite, (ancho, alto))
                    self.sprites_nubes.append(sprite)
                except:
                    pass
        
        if not self.sprites_nubes:
            nube_default = pygame.Surface((60, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(nube_default, (255, 255, 255), (0, 10, 30, 20))
            pygame.draw.ellipse(nube_default, (255, 255, 255), (20, 5, 35, 25))
            pygame.draw.ellipse(nube_default, (255, 255, 255), (35, 10, 25, 20))
            self.sprites_nubes.append(nube_default)

    def crear_nubes(self):
        self.nubes = []
        num_nubes = random.randint(5, 8)
        
        for _ in range(num_nubes):
            sprite = random.choice(self.sprites_nubes)
            x = random.randint(0, ANCHO)
            y = random.randint(30, 200)
            velocidad = random.uniform(0.3, 0.8)
            nube = Nube(x, y, velocidad, sprite)
            self.nubes.append(nube)

    def crear_bloques(self, posiciones_bloques):
        self.bloques = []
        for pos in posiciones_bloques:
            bloque = Bloque(pos[0], pos[1], self.sprites_bloques, self.sprite_bloque_usado)
            self.bloques.append(bloque)

    def crear_monedas(self, posiciones_monedas):
        self.monedas = []
        for pos in posiciones_monedas:
            moneda = Moneda(pos[0], pos[1], self.sprites_monedas)
            self.monedas.append(moneda)

    def crear_tuberias(self, datos_tuberias):
        self.tuberias = []
        for datos in datos_tuberias:
            tuberia = Tuberia(datos[0], datos[1], datos[2], datos[3], self.sprite_tubo, self.sprites_planta)
            self.tuberias.append(tuberia)
    
    def crear_enemigos(self, datos_enemigos):
        """Crea enemigos en el nivel"""
        self.enemigos = []
        for datos in datos_enemigos:
            enemigo = Enemigo(datos[0], datos[1], datos[2])
            self.enemigos.append(enemigo)

    def crear_decoraciones(self, arbustos_pos, colinas_pos):
        self.arbustos = []
        for x, y in arbustos_pos:
            sprite = random.choice(self.sprites_arbustos) if self.sprites_arbustos and self.sprites_arbustos[0] is not None else None
            self.arbustos.append(Arbusto(x, y, sprite))

        self.colinas = [Colina(x, y, self.sprite_colina) for x, y in colinas_pos]

    def cargar_nivel(self, numero_nivel):
        if numero_nivel not in NIVELES:
            return
        
        nivel = NIVELES[numero_nivel]
        self.nivel_actual = numero_nivel
        self.plataformas = nivel["plataformas"]
        self.meta = nivel["meta"]
        self.nombre_nivel = nivel["nombre"]
        
        self.crear_bloques(nivel["bloques"])
        self.hongos = [] # Lista de hongos activos
        self.crear_monedas(nivel.get("monedas", []))
        self.crear_tuberias(nivel.get("tuberias", []))
        self.crear_enemigos(nivel.get("enemigos", []))
        self.crear_decoraciones(nivel.get("fondo_arbustos", []), nivel.get("fondo_colinas", []))
        
        self.jugador = Jugador(100, 500)
        try:
            if self.sonido_salto:
                self.jugador.set_sonido_salto(self.sonido_salto)
        except:
            pass

    def verificar_meta(self):
        distancia = ((self.jugador.x - self.meta[0])**2 + (self.jugador.y - self.meta[1])**2)**0.5
        if distancia < 30:
            self.cargar_nivel(self.nivel_actual)

    def actualizar_camara(self):
        self.camara_x = self.jugador.x - ANCHO // 2
        if self.camara_x < 0:
            self.camara_x = 0
        if self.camara_x > ANCHO_NIVEL - ANCHO:
            self.camara_x = ANCHO_NIVEL - ANCHO

    def dibujar_meta(self):
        meta_x = self.meta[0] - self.camara_x
        pygame.draw.rect(self.pantalla, (50, 50, 50), (meta_x, self.meta[1] - 100, 6, 100))
        
        for i in range(3):
            for j in range(3):
                color = BLANCO if (i + j) % 2 == 0 else NEGRO
                pygame.draw.rect(self.pantalla, color, (meta_x + 6 + j * 8, self.meta[1] - 100 + i * 8, 8, 8))
        
        pygame.draw.circle(self.pantalla, AMARILLO, (int(meta_x + 3), int(self.meta[1] - 103)), 8)

    def ejecutar(self):
        while True:
            self.reloj.tick(FPS)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.cargar_nivel(1)
                        self.reproducir_musica_fondo()

            teclas = pygame.key.get_pressed()
            self.jugador.mover(teclas, self.plataformas, self.bloques, self.tuberias)
            
            # Actualizar animación de muerte
            resultado = self.jugador.actualizar_muerte()
            if resultado == "game_over":
                self.cargar_nivel(1)
                self.reproducir_musica_fondo()
            elif resultado == "reset_world":
                self.cargar_nivel(self.nivel_actual)
                self.reproducir_musica_fondo()

            self.verificar_meta()
            self.actualizar_camara()
            
            # ========== VERIFICAR COLISIONES CON ENEMIGOS ==========
            if not self.jugador.muriendo:
                rect_jugador = pygame.Rect(self.jugador.x, self.jugador.y, 
                                          self.jugador.ancho, self.jugador.alto)
                
                # Colisión con Goombas
                for enemigo in self.enemigos:
                    if enemigo.vivo and not enemigo.aplastado:
                        rect_enemigo = enemigo.get_rect()
                        
                        if rect_jugador.colliderect(rect_enemigo):
                            if self.jugador.invulnerable:
                                continue
                            # Verificar si Mario está cayendo sobre el Goomba
                            # (Mario está arriba Y está cayendo)
                            if (self.jugador.velocidad_y > 0 and 
                                self.jugador.y + self.jugador.alto <= enemigo.y + enemigo.alto // 2):
                                
                                # MARIO SALTA SOBRE LA CABEZA - GOOMBA APLASTADO
                                enemigo.aplastar()
                                try:
                                    if self.sonido_golpe:
                                        self.sonido_golpe.play()
                                except:
                                    pass
                                self.jugador.velocidad_y = -8
                                ahora = pygame.time.get_ticks()
                                if ahora - self.combo_ultimo_kill <= 1000:
                                    self.combo_valor += 100
                                else:
                                    self.combo_valor = 100
                                self.combo_ultimo_kill = ahora
                                self.jugador.puntos += self.combo_valor
                                px = enemigo.x - self.camara_x
                                py = enemigo.y - 20
                                self.popups.append(ScorePopup(px, py, str(self.combo_valor)))
                            else:
                                if self.jugador.grande:
                                    try:
                                        if self.sonido_power_down:
                                            self.sonido_power_down.play()
                                    except:
                                        pass
                                    self.jugador.encoger()
                                else:
                                    self.matar_mario()
                            break
                
                # Colisión con Plantas Carnívoras
                for tuberia in self.tuberias:
                    if tuberia.tiene_planta and tuberia.planta_visible and tuberia.altura_planta > 20:
                        # Calcular posición de la planta
                        if len(tuberia.sprites_planta) >= 2:
                            sprite_actual = tuberia.sprites_planta[tuberia.frame_planta % len(tuberia.sprites_planta)]
                            planta_x = tuberia.x + (tuberia.ancho // 2) - (sprite_actual.get_width() // 2)
                            alto_sprite = sprite_actual.get_height()
                            alto_visible = int(alto_sprite * tuberia.altura_planta / 100)
                            planta_y = tuberia.y - alto_visible + 10
                            
                            # Crear rectángulo de colisión de la planta
                            rect_planta = pygame.Rect(planta_x, planta_y, sprite_actual.get_width(), alto_visible)
                            
                            if rect_jugador.colliderect(rect_planta):
                                if not self.jugador.invulnerable:
                                    if self.jugador.grande:
                                        try:
                                            if self.sonido_power_down:
                                                self.sonido_power_down.play()
                                        except:
                                            pass
                                        self.jugador.encoger()
                                    else:
                                        self.matar_mario()
                                break
                
                # Colisión con Monedas
                rect_jugador = pygame.Rect(self.jugador.x, self.jugador.y, self.jugador.ancho, self.jugador.alto)
                for moneda in self.monedas:
                    if not moneda.recogida and rect_jugador.colliderect(moneda.get_rect()):
                        moneda.recogida = True
                        self.jugador.puntos += 100
                        try:
                            if self.sonido_moneda:
                                self.sonido_moneda.play()
                        except:
                            pass
                        px = moneda.x - self.camara_x
                        py = moneda.y - 10
                        self.popups.append(ScorePopup(px, py, "100"))
                        print(f"💰 Moneda recogida (+100)! Puntos: {self.jugador.puntos}")
                
                # Colisión con Hongos
                for hongo in self.hongos:
                    if hongo.activo and rect_jugador.colliderect(hongo.get_rect()):
                        hongo.activo = False
                        self.jugador.puntos += 10000
                        try:
                            if self.sonido_power_up:
                                self.sonido_power_up.play()
                        except:
                            pass
                        self.jugador.crecer()
                        px = self.jugador.x - self.camara_x
                        py = self.jugador.y - 20
                        self.popups.append(ScorePopup(px, py, "10000"))
                        print(f"🍄 Hongo recogido! Puntos: {self.jugador.puntos}")
            
            for nube in self.nubes:
                nube.actualizar()
            for moneda in self.monedas:
                moneda.actualizar()
            for bloque in self.bloques:
                bloque.actualizar()
                if bloque.pending_item == "hongo":
                    self.hongos.append(Hongo(bloque.x, bloque.y, self.sprite_hongo))
                    bloque.pending_item = None
            
            for hongo in self.hongos:
                hongo.actualizar(self.plataformas, self.tuberias, self.bloques)

            for tuberia in self.tuberias:
                tuberia.actualizar()
            for enemigo in self.enemigos:
                enemigo.actualizar(self.plataformas, self.tuberias, self.bloques)

            # Dibujar cielo
            for y in range(ALTO):
                intensidad = int(107 + (200 - 107) * (y / ALTO))
                color = (intensidad, 140, 255)
                pygame.draw.line(self.pantalla, color, (0, y), (ANCHO, y))
            
            # Dibujar nubes
            for nube in self.nubes:
                nube_x = nube.x - (self.camara_x * 0.5)
                self.pantalla.blit(nube.sprite, (int(nube_x), int(nube.y)))
            
            # Dibujar decoraciones
            for colina in self.colinas:
                colina.dibujar(self.pantalla, self.camara_x)
            for arbusto in self.arbustos:
                arbusto.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar plataformas
            for p in self.plataformas:
                plat_x = p[0] - self.camara_x
                if plat_x + p[2] > -100 and plat_x < ANCHO + 100:
                    if p[1] >= 550:
                        if self.sprite_piso:
                            ancho_sprite = self.sprite_piso.get_width()
                            x_actual = plat_x
                            while x_actual < plat_x + p[2]:
                                self.pantalla.blit(self.sprite_piso, (x_actual, p[1]))
                                x_actual += ancho_sprite
                        else:
                            pygame.draw.rect(self.pantalla, (255, 140, 0), (plat_x, p[1], p[2], p[3]))
                    else:
                        pygame.draw.rect(self.pantalla, VERDE, (plat_x, p[1], p[2], 5))
                        pygame.draw.rect(self.pantalla, MARRON, (plat_x, p[1] + 5, p[2], p[3] - 5))
            
            # Dibujar tuberías
            for tuberia in self.tuberias:
                tuberia_x = tuberia.x - self.camara_x
                if -100 < tuberia_x < ANCHO + 100:
                    tuberia.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar bloques
            for bloque in self.bloques:
                bloque.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar hongos
            for hongo in self.hongos:
                hongo.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar monedas
            for moneda in self.monedas:
                moneda.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar enemigos
            for enemigo in self.enemigos:
                enemigo_x = enemigo.x - self.camara_x
                if -50 < enemigo_x < ANCHO + 50:
                    enemigo.dibujar(self.pantalla, self.camara_x)
            
            # Dibujar meta
            self.dibujar_meta()
            
            # Dibujar jugador
            jugador_x = self.jugador.x - self.camara_x
            self.jugador.dibujar_en_posicion(self.pantalla, jugador_x, self.jugador.y)
            
            fuente_popup = pygame.font.Font(None, 22)
            for p in self.popups:
                p.actualizar()
                p.dibujar(self.pantalla, fuente_popup)
            self.popups = [p for p in self.popups if not p.terminado()]
            
            # UI - Información del nivel
            fuente = pygame.font.Font(None, 30)
            texto_info = fuente.render(f"X: {int(self.jugador.x)} | Vidas: {self.jugador.vidas} | Muriendo: {self.jugador.muriendo}", True, BLANCO)
            self.pantalla.blit(texto_info, (11, 11))
            self.pantalla.blit(texto_info, (10, 10))
            
            texto_nivel = fuente.render(self.nombre_nivel, True, BLANCO)
            self.pantalla.blit(texto_nivel, (11, 41))
            self.pantalla.blit(texto_nivel, (10, 40))
            
            fuente_small = pygame.font.Font(None, 18)
            texto_ayuda = fuente_small.render("FLECHAS/WASD: Mover | ESPACIO: Saltar | SHIFT: Correr | R: Reiniciar", True, BLANCO)
            self.pantalla.blit(texto_ayuda, (10, 570))

            pygame.display.flip()


if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
