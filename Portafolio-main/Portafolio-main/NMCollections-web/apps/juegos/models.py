from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import BaseModel


class MiniJuego(BaseModel):
    """
    Mini juegos disponibles basado en tabla mini_juego del script.sql
    """
    TIPO_JUEGO_CHOICES = [
        ('generico', 'Genérico'),
        ('personalizado', 'Personalizado'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_JUEGO_CHOICES,
        verbose_name='Tipo'
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de creación')
    
    # Campos adicionales
    activo = models.BooleanField(default=True, verbose_name='Activo')
    imagen_icono = models.ImageField(upload_to='juegos/iconos/', blank=True, verbose_name='Icono')
    configuracion = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Configuración del juego'
    )
    puntaje_maximo = models.IntegerField(null=True, blank=True, verbose_name='Puntaje máximo posible')
    tiempo_limite = models.IntegerField(null=True, blank=True, verbose_name='Tiempo límite (segundos)')
    
    class Meta:
        verbose_name = 'Mini Juego'
        verbose_name_plural = 'Mini Juegos'
        db_table = 'mini_juego'
    
    def __str__(self):
        return self.nombre
    
    @property
    def total_partidas(self):
        """Retorna el total de partidas jugadas"""
        return self.partidas.count()
    
    @property
    def jugadores_unicos(self):
        """Retorna el número de jugadores únicos"""
        return self.progresos.values('usuario').distinct().count()


class Partida(BaseModel):
    """
    Partidas de juegos basado en tabla partida del script.sql
    """
    RESULTADO_CHOICES = [
        ('1', 'Ganó Jugador 1'),
        ('2', 'Ganó Jugador 2'),
        ('empate', 'Empate'),
        ('cancelado', 'Cancelado'),
    ]
    
    juego = models.ForeignKey(
        MiniJuego, 
        on_delete=models.CASCADE, 
        related_name='partidas',
        verbose_name='Juego'
    )
    player1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='partidas_como_player1',
        verbose_name='Jugador 1'
    )
    player2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='partidas_como_player2',
        null=True,
        blank=True,
        verbose_name='Jugador 2'
    )
    fecha_inicio = models.DateTimeField(default=timezone.now, verbose_name='Fecha de inicio')
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de fin')
    ganador = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='partidas_ganadas',
        verbose_name='Ganador'
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        null=True,
        blank=True,
        verbose_name='Resultado'
    )
    
    # Campos adicionales
    puntaje_player1 = models.IntegerField(default=0, verbose_name='Puntaje Jugador 1')
    puntaje_player2 = models.IntegerField(default=0, verbose_name='Puntaje Jugador 2')
    duracion_segundos = models.IntegerField(null=True, blank=True, verbose_name='Duración en segundos')
    datos_partida = models.JSONField(
        null=True, 
        blank=True, 
        verbose_name='Datos específicos de la partida'
    )
    
    class Meta:
        verbose_name = 'Partida'
        verbose_name_plural = 'Partidas'
        db_table = 'partida'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        vs = f" vs {self.player2.email}" if self.player2 else " (solo)"
        return f"{self.juego.nombre}: {self.player1.email}{vs}"
    
    @property
    def esta_en_curso(self):
        """Verifica si la partida está en curso"""
        return self.fecha_fin is None
    
    def finalizar_partida(self, resultado, ganador=None):
        """Finaliza la partida y actualiza estadísticas"""
        self.fecha_fin = timezone.now()
        self.resultado = resultado
        self.ganador = ganador
        
        # Calcular duración
        if self.fecha_inicio:
            duracion = self.fecha_fin - self.fecha_inicio
            self.duracion_segundos = int(duracion.total_seconds())
        
        self.save()
        
        # Actualizar progreso de los jugadores
        self._actualizar_progreso_jugadores()
    
    def _actualizar_progreso_jugadores(self):
        """Actualiza el progreso de ambos jugadores"""
        # Actualizar progreso del jugador 1
        progreso1, created = ProgresoJuego.objects.get_or_create(
            juego=self.juego,
            usuario=self.player1,
            defaults={'puntaje_total': 0, 'nivel': 0}
        )
        progreso1.puntaje_total += self.puntaje_player1
        if self.ganador == self.player1:
            progreso1.partidas_ganadas += 1
        progreso1.partidas_jugadas += 1
        progreso1.save()
        
        # Actualizar progreso del jugador 2 si existe
        if self.player2:
            progreso2, created = ProgresoJuego.objects.get_or_create(
                juego=self.juego,
                usuario=self.player2,
                defaults={'puntaje_total': 0, 'nivel': 0}
            )
            progreso2.puntaje_total += self.puntaje_player2
            if self.ganador == self.player2:
                progreso2.partidas_ganadas += 1
            progreso2.partidas_jugadas += 1
            progreso2.save()


class ProgresoJuego(BaseModel):
    """
    Progreso de usuarios en juegos basado en tabla progreso_juego del script.sql
    """
    juego = models.ForeignKey(
        MiniJuego, 
        on_delete=models.CASCADE, 
        related_name='progresos',
        verbose_name='Juego'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='progresos_juegos',
        verbose_name='Usuario'
    )
    nivel = models.IntegerField(default=0, verbose_name='Nivel')
    puntaje_total = models.IntegerField(default=0, verbose_name='Puntaje total')
    fecha_actualizacion = models.DateTimeField(default=timezone.now, verbose_name='Fecha de actualización')
    
    # Campos adicionales
    partidas_jugadas = models.IntegerField(default=0, verbose_name='Partidas jugadas')
    partidas_ganadas = models.IntegerField(default=0, verbose_name='Partidas ganadas')
    mejor_puntaje = models.IntegerField(default=0, verbose_name='Mejor puntaje')
    tiempo_total_jugado = models.IntegerField(default=0, verbose_name='Tiempo total jugado (segundos)')
    logros = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name='Logros obtenidos'
    )
    
    class Meta:
        verbose_name = 'Progreso de Juego'
        verbose_name_plural = 'Progresos de Juego'
        db_table = 'progreso_juego'
        unique_together = ['juego', 'usuario']
    
    def __str__(self):
        return f"{self.usuario.email} - {self.juego.nombre} (Nivel {self.nivel})"
    
    @property
    def porcentaje_victoria(self):
        """Calcula el porcentaje de victorias"""
        if self.partidas_jugadas == 0:
            return 0
        return (self.partidas_ganadas / self.partidas_jugadas) * 100
    
    def actualizar_nivel(self):
        """Actualiza el nivel basado en el puntaje total"""
        # Lógica simple: cada 1000 puntos = 1 nivel
        nuevo_nivel = self.puntaje_total // 1000
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
            self.fecha_actualizacion = timezone.now()
            self.save()
            return True
        return False
    
    def agregar_logro(self, logro):
        """Agrega un logro al jugador"""
        if logro not in self.logros:
            self.logros.append(logro)
            self.save()


# Modelo adicional para logros/achievements
class Logro(BaseModel):
    """
    Sistema de logros para gamificación
    """
    TIPO_LOGRO_CHOICES = [
        ('puntaje', 'Por puntaje'),
        ('partidas', 'Por cantidad de partidas'),
        ('victorias', 'Por victorias consecutivas'),
        ('tiempo', 'Por tiempo jugado'),
        ('especial', 'Logro especial'),
    ]
    
    juego = models.ForeignKey(
        MiniJuego, 
        on_delete=models.CASCADE, 
        related_name='logros',
        null=True,
        blank=True,
        verbose_name='Juego específico'
    )
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    tipo = models.CharField(max_length=20, choices=TIPO_LOGRO_CHOICES, verbose_name='Tipo')
    icono = models.ImageField(upload_to='logros/', blank=True, verbose_name='Icono')
    condiciones = models.JSONField(verbose_name='Condiciones para obtener el logro')
    puntos_recompensa = models.IntegerField(default=0, verbose_name='Puntos de recompensa')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Logro'
        verbose_name_plural = 'Logros'
    
    def __str__(self):
        return self.nombre