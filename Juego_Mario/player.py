import pygame
import os

# Constantes compartidas
ANCHO = 800
ALTO = 600
ANCHO_NIVEL = 3200
GRAVEDAD = 0.8
VELOCIDAD_SALTO = -15
VELOCIDAD_MOVIMIENTO = 5
VELOCIDAD_CORRER = 8

# Colores
NEGRO = (0, 0, 0)
ROJO = (200, 0, 0)
BLANCO = (255, 255, 255)

class Jugador:
    def __init__(self, x, y):
        # Posición y físicas
        self.x = x
        self.y = y
        self.velocidad_y = 0
        self.en_suelo = True
        self.direccion = 1
        self.primer_frame = True

        # Estado
        self.vidas = 3
        self.puntos = 0
        self.estado = "idle"
        self.muriendo = False
        self.tiempo_muerte = 0
        self.duracion_muerte = 120
        self.grande = False
        self.transformando = False
        self.transform_tipo = None
        self.tiempo_transformacion = 0
        self.duracion_transformacion = 90 # 1.5 segundos a 60 FPS
        self.transform_blink_interval = 5
        self.invulnerable = False
        self.tiempo_invulnerable = 0
        self.duracion_invulnerable = 120

        # Cargar sprites
        self.sprite_quieto = self._cargar_sprite("mario_idle.png", default="idle")
        self.sprite_caminando = self._cargar_sprite("mario_smal_walking.png", default="walking")
        self.sprite_salto = self._cargar_sprite("mario_salto.png", default="jump")
        self.sprite_corre1 = self._cargar_sprite("mario_corre1.png", default="run1")
        self.sprite_corre2 = self._cargar_sprite("mario_corre2.png", default="run2")
        self.sprite_muerte = self._cargar_sprite("muerte.png", default="death")

        # Sprites Grande
        self.sprite_grande_quieto = self._cargar_sprite("marioG_quieto.png", default="idle_big")
        self.sprite_grande_caminando1 = self._cargar_sprite("marioG_caminando1.png", default="walk_big1")
        self.sprite_grande_caminando2 = self._cargar_sprite("marioG_caminando2.png", default="walk_big2")
        self.sprite_grande_salto = self._cargar_sprite("mario_grande_salto.png", default="jump_big")
        self.sprite_grande_corre1 = self._cargar_sprite("marioG_corre1.png", default="run_big1")
        self.sprite_grande_corre2 = self._cargar_sprite("marioG_corre2.png", default="run_big2")
        self.sprite_grande_corre3 = self._cargar_sprite("marioG_corre3.png", default="run_big3")

        # Escalado
        escala = 0.4
        self.sprite_quieto = self._escalar(self.sprite_quieto, escala)
        self.sprite_caminando = self._escalar(self.sprite_caminando, escala)
        self.sprite_salto = self._escalar(self.sprite_salto, escala)
        self.sprite_corre1 = self._escalar(self.sprite_corre1, escala)
        self.sprite_corre2 = self._escalar(self.sprite_corre2, escala)
        self.sprite_muerte = self._escalar(self.sprite_muerte, escala)
        
        # Escalado Grande (Asumiendo que necesitan el mismo factor o ajustado)
        # Si los sprites originales son grandes, 0.4 podría estar bien.
        self.sprite_grande_quieto = self._escalar(self.sprite_grande_quieto, escala)
        self.sprite_grande_caminando1 = self._escalar(self.sprite_grande_caminando1, escala)
        self.sprite_grande_caminando2 = self._escalar(self.sprite_grande_caminando2, escala)
        self.sprite_grande_salto = self._escalar(self.sprite_grande_salto, escala)
        self.sprite_grande_corre1 = self._escalar(self.sprite_grande_corre1, escala)
        self.sprite_grande_corre2 = self._escalar(self.sprite_grande_corre2, escala)
        self.sprite_grande_corre3 = self._escalar(self.sprite_grande_corre3, escala)

        # Sprites por dirección
        self.sprites_derecha = {
            "idle": self.sprite_quieto,
            "walking": self.sprite_caminando,
            "jump": self.sprite_salto,
            "run1": self.sprite_corre1,
            "run2": self.sprite_corre2,
            "death": self.sprite_muerte
        }
        self.sprites_izquierda = {
            "idle": pygame.transform.flip(self.sprite_quieto, True, False),
            "walking": pygame.transform.flip(self.sprite_caminando, True, False),
            "jump": pygame.transform.flip(self.sprite_salto, True, False),
            "run1": pygame.transform.flip(self.sprite_corre1, True, False),
            "run2": pygame.transform.flip(self.sprite_corre2, True, False),
            "death": self.sprite_muerte
        }
        
        # Sprites Grande por dirección
        self.sprites_grande_derecha = {
            "idle": self.sprite_grande_quieto,
            "walking1": self.sprite_grande_caminando1,
            "walking2": self.sprite_grande_caminando2,
            "jump": self.sprite_grande_salto,
            "run1": self.sprite_grande_corre1,
            "run2": self.sprite_grande_corre2,
            "run3": self.sprite_grande_corre3
        }
        self.sprites_grande_izquierda = {
            "idle": pygame.transform.flip(self.sprite_grande_quieto, True, False),
            "walking1": pygame.transform.flip(self.sprite_grande_caminando1, True, False),
            "walking2": pygame.transform.flip(self.sprite_grande_caminando2, True, False),
            "jump": pygame.transform.flip(self.sprite_grande_salto, True, False),
            "run1": pygame.transform.flip(self.sprite_grande_corre1, True, False),
            "run2": pygame.transform.flip(self.sprite_grande_corre2, True, False),
            "run3": pygame.transform.flip(self.sprite_grande_corre3, True, False)
        }

        self.ancho = self.sprite_quieto.get_width()
        self.alto = self.sprite_quieto.get_height()

        # Animación
        self.animacion_frame = 0
        self.animacion_contador = 0
        self.animacion_velocidad = 5
        self.corriendo = False
        self.sonido_salto = None

    def _cargar_sprite(self, nombre, default="idle"):
        ruta = os.path.join("assets", nombre)
        if os.path.exists(ruta):
            try:
                sprite = pygame.image.load(ruta).convert_alpha()
                print(f"✅ Cargado: {nombre} - Tamaño: {sprite.get_width()}x{sprite.get_height()}")
                return sprite
            except:
                print(f"❌ Error cargando {nombre}")
        
        print(f"⚠️ Usando sprite por defecto para: {nombre}")
        superficie = pygame.Surface((32, 32), pygame.SRCALPHA)
        if default == "idle":
            pygame.draw.circle(superficie, ROJO, (16, 16), 15)
            pygame.draw.circle(superficie, BLANCO, (16, 16), 5)
        elif default == "walking":
            pygame.draw.rect(superficie, (0, 255, 0), (2, 2, 28, 28))
            pygame.draw.line(superficie, BLANCO, (5, 5), (27, 27), 4)
            pygame.draw.line(superficie, BLANCO, (27, 5), (5, 27), 4)
        elif default == "jump":
            pygame.draw.polygon(superficie, (0, 100, 255), [(16, 5), (5, 27), (27, 27)])
        elif default == "run1":
            pygame.draw.rect(superficie, (255, 165, 0), (2, 2, 28, 28))
            pygame.draw.circle(superficie, BLANCO, (16, 16), 8)
        elif default == "run2":
            pygame.draw.rect(superficie, (255, 100, 0), (2, 2, 28, 28))
            pygame.draw.circle(superficie, BLANCO, (16, 16), 6)
        elif default == "death":
            pygame.draw.circle(superficie, ROJO, (16, 16), 15)
            pygame.draw.line(superficie, BLANCO, (8, 8), (24, 24), 3)
            pygame.draw.line(superficie, BLANCO, (24, 8), (8, 24), 3)
        return superficie

    def _escalar(self, sprite, escala):
        ancho = int(sprite.get_width() * escala)
        alto = int(sprite.get_height() * escala)
        return pygame.transform.scale(sprite, (ancho, alto))
    
    def set_sonido_salto(self, sonido):
        self.sonido_salto = sonido

    def morir(self):
        """Activa la animación de muerte"""
        if not self.muriendo:
            self.muriendo = True
            self.tiempo_muerte = 0
            self.velocidad_y = -12
            self.vidas -= 1
            print(f"💀 Mario ha muerto! Vidas restantes: {self.vidas}")
            print(f"🎭 Estado muriendo: {self.muriendo}")
    
    def crecer(self):
        """Activa la transformación a Mario Grande"""
        if not self.grande and not self.transformando:
            self.transformando = True
            self.transform_tipo = "grow"
            self.transform_blink_interval = 5
            self.tiempo_transformacion = 0
            self.velocidad_y = 0
            print("🍄 Mario creciendo!")
    
    def encoger(self):
        if self.grande and not self.muriendo and not self.transformando:
            self.transformando = True
            self.transform_tipo = "shrink"
            self.transform_blink_interval = 3
            self.tiempo_transformacion = 0
            self.velocidad_y = 0
            print("🔻 Mario encogiendo!")
            self.invulnerable = True
            self.tiempo_invulnerable = 0

    def actualizar_muerte(self):
        """Actualiza la animación de muerte"""
        if self.muriendo:
            self.tiempo_muerte += 1
            # Gravedad reducida para la animación de muerte (más dramática y visible)
            self.velocidad_y += GRAVEDAD * 0.4
            self.y += self.velocidad_y
            
            if self.tiempo_muerte >= self.duracion_muerte:
                if self.vidas > 0:
                    self.x = 100
                    self.y = 500
                    self.velocidad_y = 0
                    self.muriendo = False
                    self.tiempo_muerte = 0
                    self.en_suelo = True
                    print("✅ Mario reiniciado")
                    return "reset_world"
                else:
                    print("💀 GAME OVER!")
                    return "game_over"
        return None

    def mover(self, teclas, plataformas, bloques=[], tuberias=[]):
        if self.muriendo:
            return
        
        if self.invulnerable:
            self.tiempo_invulnerable += 1
            if self.tiempo_invulnerable >= self.duracion_invulnerable:
                self.invulnerable = False
                self.tiempo_invulnerable = 0
        
        if self.transformando:
            self.tiempo_transformacion += 1
            if self.tiempo_transformacion >= self.duracion_transformacion:
                self.transformando = False
                if self.transform_tipo == "grow":
                    self.grande = True
                    old_alto = self.alto
                    self.ancho = self.sprite_grande_quieto.get_width()
                    self.alto = self.sprite_grande_quieto.get_height()
                    self.y -= (self.alto - old_alto)
                    print("✨ Mario ahora es Grande!")
                elif self.transform_tipo == "shrink":
                    old_alto = self.alto
                    self.grande = False
                    self.ancho = self.sprite_quieto.get_width()
                    self.alto = self.sprite_quieto.get_height()
                    self.y += (old_alto - self.alto)
                    print("🔻 Mario volvió a pequeño")
                self.transform_tipo = None
            return

        if self.primer_frame:
            suelo = max(plataformas, key=lambda p: p[2])
            self.y = suelo[1] - self.alto
            self.en_suelo = True
            self.velocidad_y = 0
            self.estado = "idle"
            self.primer_frame = False

        moviendo = False
        self.corriendo = teclas[pygame.K_LSHIFT] or teclas[pygame.K_RSHIFT]
        velocidad_actual = VELOCIDAD_CORRER if self.corriendo else VELOCIDAD_MOVIMIENTO

        dx = 0
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -velocidad_actual
            self.direccion = -1
            moviendo = True

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = velocidad_actual
            self.direccion = 1
            moviendo = True

        self.x += dx
        
        if self.x < 0:
            self.x = 0

        rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        for bloque in bloques:
            rect_bloque = bloque.get_rect()
            if rect_jugador.colliderect(rect_bloque):
                if dx > 0:
                    self.x = rect_bloque.left - self.ancho
                elif dx < 0:
                    self.x = rect_bloque.right
                break
        
        rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        for tuberia in tuberias:
            rect_tuberia = tuberia.get_rect()
            if rect_jugador.colliderect(rect_tuberia):
                if dx > 0:
                    self.x = rect_tuberia.left - self.ancho
                elif dx < 0:
                    self.x = rect_tuberia.right
                break

        if (teclas[pygame.K_SPACE] or teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.en_suelo:
            try:
                if self.sonido_salto:
                    self.sonido_salto.play()
            except:
                pass
            self.velocidad_y = VELOCIDAD_SALTO
            self.en_suelo = False

        y_prev = self.y
        self.velocidad_y += GRAVEDAD
        self.y += self.velocidad_y

        self.en_suelo = False
        for plataforma in plataformas:
            if (self.x + self.ancho > plataforma[0] and 
                self.x < plataforma[0] + plataforma[2]):
                top = plataforma[1]
                bottom = plataforma[1] + plataforma[3]
                if self.velocidad_y > 0 and y_prev + self.alto <= top and self.y + self.alto >= top:
                    self.y = top - self.alto
                    self.velocidad_y = 0
                    self.en_suelo = True
                    break
                elif self.velocidad_y < 0 and y_prev >= bottom and self.y <= bottom:
                    self.y = bottom
                    self.velocidad_y = 0
                    break

        rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
        for bloque in bloques:
            rect_bloque = bloque.get_rect()
            
            if rect_jugador.colliderect(rect_bloque):
                if self.velocidad_y < 0:
                    self.y = rect_bloque.bottom
                    self.velocidad_y = 0
                    bloque.golpear()
                elif self.velocidad_y > 0:
                    self.y = rect_bloque.top - self.alto
                    self.velocidad_y = 0
                    self.en_suelo = True
        
        rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
        for tuberia in tuberias:
            rect_top = tuberia.get_top_rect()
            
            if (self.x + self.ancho > tuberia.x and 
                self.x < tuberia.x + tuberia.ancho):
                
                distancia = rect_top.top - (self.y + self.alto)
                
                if -10 <= distancia <= 10:
                    self.y = rect_top.top - self.alto
                    self.velocidad_y = 0
                    self.en_suelo = True
                    break
        
        for tuberia in tuberias:
            rect_body = tuberia.get_body_rect()
            rect_jugador = pygame.Rect(self.x, self.y, self.ancho, self.alto)
            
            if rect_jugador.colliderect(rect_body) and self.velocidad_y < 0:
                self.y = rect_body.bottom
                self.velocidad_y = 0
                break

        if moviendo and self.en_suelo:
            self.animacion_contador += 1
            if self.animacion_contador >= 5:
                limit = 3 if (self.grande and self.corriendo) else 2
                self.animacion_frame = (self.animacion_frame + 1) % limit
                self.animacion_contador = 0
        else:
            self.animacion_frame = 0
            self.animacion_contador = 0

    def dibujar(self, pantalla):
        ajuste_y = 0
        sprite = None
        
        if self.transformando:
            # Parpadeo entre pequeño y grande
            if (self.tiempo_transformacion // self.transform_blink_interval) % 2 == 0:
                sprite = self.sprites_derecha["idle"] if self.direccion == 1 else self.sprites_izquierda["idle"]
            else:
                sprite = self.sprites_grande_derecha["idle"] if self.direccion == 1 else self.sprites_grande_izquierda["idle"]
                ajuste_y = self.sprite_quieto.get_height() - self.sprite_grande_quieto.get_height()
                
        elif self.muriendo:
            sprite = self.sprite_muerte
            
        elif self.grande:
            # Lógica Mario Grande
            if not self.en_suelo:
                sprite = self.sprites_grande_derecha["jump"] if self.direccion == 1 else self.sprites_grande_izquierda["jump"]
            elif self.corriendo:
                if self.animacion_frame == 0:
                    sprite = self.sprites_grande_derecha["run1"] if self.direccion == 1 else self.sprites_grande_izquierda["run1"]
                elif self.animacion_frame == 1:
                    sprite = self.sprites_grande_derecha["run2"] if self.direccion == 1 else self.sprites_grande_izquierda["run2"]
                else:
                    sprite = self.sprites_grande_derecha["run3"] if self.direccion == 1 else self.sprites_grande_izquierda["run3"]
            elif self.animacion_frame > 0: 
                # Si está moviéndose (animacion_frame oscila 0-1)
                if self.animacion_frame == 1:
                     sprite = self.sprites_grande_derecha["walking2"] if self.direccion == 1 else self.sprites_grande_izquierda["walking2"]
                else:
                     sprite = self.sprites_grande_derecha["walking1"] if self.direccion == 1 else self.sprites_grande_izquierda["walking1"]
            else:
                sprite = self.sprites_grande_derecha["idle"] if self.direccion == 1 else self.sprites_grande_izquierda["idle"]
                
        else:
            # Lógica Mario Pequeño
            if not self.en_suelo:
                sprite = self.sprites_derecha["jump"] if self.direccion == 1 else self.sprites_izquierda["jump"]
            elif self.corriendo:
                if self.animacion_frame == 1:
                    sprite = self.sprites_derecha["run2"] if self.direccion == 1 else self.sprites_izquierda["run2"]
                else:
                    sprite = self.sprites_derecha["run1"] if self.direccion == 1 else self.sprites_izquierda["run1"]
                ajuste_y = 7
            elif self.animacion_frame == 1:
                sprite = self.sprites_derecha["walking"] if self.direccion == 1 else self.sprites_izquierda["walking"]
            else:
                sprite = self.sprites_derecha["idle"] if self.direccion == 1 else self.sprites_izquierda["idle"]

        if sprite and not (self.invulnerable and (self.tiempo_invulnerable // 5) % 2 == 0):
            pantalla.blit(sprite, (int(self.x), int(self.y + ajuste_y)))

        fuente = pygame.font.Font(None, 24)
        texto = fuente.render(f"Vidas: {self.vidas} | Grande: {self.grande}", True, NEGRO)
        pantalla.blit(texto, (10, 10))

    def dibujar_en_posicion(self, pantalla, x, y):
        """Dibuja el jugador en una posición específica (para la cámara)"""
        ajuste_y = 0
        sprite = None
        
        if self.transformando:
            if (self.tiempo_transformacion // self.transform_blink_interval) % 2 == 0:
                sprite = self.sprites_derecha["idle"] if self.direccion == 1 else self.sprites_izquierda["idle"]
            else:
                sprite = self.sprites_grande_derecha["idle"] if self.direccion == 1 else self.sprites_grande_izquierda["idle"]
                ajuste_y = self.sprite_quieto.get_height() - self.sprite_grande_quieto.get_height()
        
        elif self.muriendo:
            sprite = self.sprite_muerte
            
        elif self.grande:
            if not self.en_suelo:
                sprite = self.sprites_grande_derecha["jump"] if self.direccion == 1 else self.sprites_grande_izquierda["jump"]
            elif self.corriendo:
                if self.animacion_frame == 0:
                    sprite = self.sprites_grande_derecha["run1"] if self.direccion == 1 else self.sprites_grande_izquierda["run1"]
                elif self.animacion_frame == 1:
                    sprite = self.sprites_grande_derecha["run2"] if self.direccion == 1 else self.sprites_grande_izquierda["run2"]
                else:
                    sprite = self.sprites_grande_derecha["run3"] if self.direccion == 1 else self.sprites_grande_izquierda["run3"]
            elif self.animacion_frame > 0:
                if self.animacion_frame == 1:
                     sprite = self.sprites_grande_derecha["walking2"] if self.direccion == 1 else self.sprites_grande_izquierda["walking2"]
                else:
                     sprite = self.sprites_grande_derecha["walking1"] if self.direccion == 1 else self.sprites_grande_izquierda["walking1"]
            else:
                sprite = self.sprites_grande_derecha["idle"] if self.direccion == 1 else self.sprites_grande_izquierda["idle"]
                
        else:
            if not self.en_suelo:
                sprite = self.sprites_derecha["jump"] if self.direccion == 1 else self.sprites_izquierda["jump"]
            elif self.corriendo:
                if self.animacion_frame == 1:
                    sprite = self.sprites_derecha["run2"] if self.direccion == 1 else self.sprites_izquierda["run2"]
                else:
                    sprite = self.sprites_derecha["run1"] if self.direccion == 1 else self.sprites_izquierda["run1"]
                ajuste_y = 7
            elif self.animacion_frame == 1:
                sprite = self.sprites_derecha["walking"] if self.direccion == 1 else self.sprites_izquierda["walking"]
            else:
                sprite = self.sprites_derecha["idle"] if self.direccion == 1 else self.sprites_izquierda["idle"]

        if sprite and not (self.invulnerable and (self.tiempo_invulnerable // 5) % 2 == 0):
            pantalla.blit(sprite, (int(x), int(y + ajuste_y)))

        fuente = pygame.font.Font(None, 20)
        texto = fuente.render(f"X: {int(self.x)} | Vidas: {self.vidas}", True, NEGRO)
        pantalla.blit(texto, (10, 10))
