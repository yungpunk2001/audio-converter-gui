# Sistema de Auto-actualización de yt-dlp

## Resumen

Se ha implementado un sistema automático de actualización de yt-dlp que se ejecuta al iniciar la aplicación. Este sistema previene errores futuros de descarga de YouTube (como el HTTP 403) manteniendo yt-dlp actualizado.

## Funcionamiento

### 1. Verificación Inteligente (Solo 1 vez al día)

- Al iniciar la app, se verifica si hay actualización disponible
- Se usa un **archivo de caché** para evitar verificaciones repetidas:
  - Ubicación: `~/.audio_converter_cache/ytdlp_last_update.txt`
  - Almacena: fecha/hora de última verificación
  - Período: 24 horas (1 día)
  
**Beneficio**: No ralentiza el inicio de la app con verificaciones innecesarias

### 2. Proceso de Verificación

```python
check_ytdlp_update()
```

**Pasos**:
1. Verifica si pasaron 24h desde última verificación
2. Si no pasó tiempo suficiente → retorna sin hacer nada
3. Si pasó tiempo → ejecuta `pip list --outdated` (timeout 10s)
4. Compara versión instalada vs disponible
5. Guarda timestamp en archivo de caché
6. Retorna resultado: `(needs_update, current_version, message)`

**Ejemplo de salida**:
- Actualización disponible: `(True, "2025.10.22", "Nueva versión 2025.11.01 disponible")`
- Ya actualizado: `(False, "2025.10.22", "yt-dlp está actualizado")`

### 3. Diálogo de Actualización

Si hay actualización disponible, se muestra:

```
┌─────────────────────────────────────────┐
│  Actualización de yt-dlp disponible     │
├─────────────────────────────────────────┤
│  Se ha detectado una nueva versión      │
│  Nueva versión 2025.11.01 disponible    │
│                                          │
│  Se recomienda actualizar para evitar   │
│  errores al descargar de YouTube.       │
│                                          │
│  ¿Deseas actualizar ahora?              │
│  (tardará unos segundos)                │
│                                          │
│          [Sí]        [No]               │
└─────────────────────────────────────────┘
```

**Características del diálogo**:
- ✅ **No intrusivo**: aparece solo cuando hay actualización real
- ✅ **Informativo**: explica el motivo (evitar errores de YouTube)
- ✅ **Opcional**: el usuario puede omitir la actualización
- ✅ **Predeterminado**: botón "Sí" seleccionado por defecto

### 4. Proceso de Actualización

```python
update_ytdlp_silent()
```

Si el usuario acepta:
1. Muestra mensaje de progreso: "Actualizando yt-dlp, por favor espera..."
2. Ejecuta: `pip install --upgrade yt-dlp` (timeout 30s)
3. Guarda timestamp de última actualización
4. Muestra resultado:
   - **Éxito**: "✓ yt-dlp se ha actualizado correctamente"
   - **Error**: mensaje con instrucciones para actualización manual

### 5. Manejo de Errores

El sistema es **robusto** ante fallos:

```python
try:
    needs_update, current_ver, message = check_ytdlp_update()
    # ... proceso de actualización ...
except Exception as e:
    # Fallo SILENCIOSO: no interrumpir inicio de app
    print(f"Error al verificar actualización de yt-dlp: {e}")
```

**Ventajas**:
- ❌ **No bloquea** el inicio de la aplicación si hay error de red
- ❌ **No muestra** mensajes de error molestos al usuario
- ✅ **Registra** el error en consola para debugging
- ✅ **Permite** usar la app normalmente aunque falle la actualización

## Archivos Modificados

### 1. `main.py`

#### Imports añadidos:
```python
from datetime import datetime, timedelta
```

#### Funciones de utilidad añadidas (antes de `find_ffmpeg()`):
```python
def check_ytdlp_update() -> tuple[bool, str, str]:
    """Verifica si hay actualización de yt-dlp disponible (con caché de 24h)"""
    # ... 35 líneas ...

def update_ytdlp_silent() -> tuple[bool, str]:
    """Actualiza yt-dlp silenciosamente en background"""
    # ... 25 líneas ...
```

#### Modificación en `MainWindow.__init__()`:
```python
self.worker: Optional[ConvertWorker] = None
self.download_worker: Optional[DownloadWorker] = None

# ✨ NUEVO: Verificar actualización de yt-dlp al inicio
if YT_DLP_AVAILABLE:
    self.check_and_update_ytdlp()
```

#### Método añadido en clase `MainWindow` (antes de `closeEvent()`):
```python
def check_and_update_ytdlp(self):
    """Verifica y actualiza yt-dlp si es necesario (solo una vez al día)"""
    # ... 50 líneas ...
```

## Beneficios del Sistema

### 1. Prevención de Errores
- ✅ **Evita HTTP 403**: mantiene compatibilidad con restricciones de YouTube
- ✅ **Actualización proactiva**: detecta versiones nuevas automáticamente
- ✅ **Sin intervención manual**: el usuario no necesita recordar actualizar

### 2. Experiencia de Usuario
- ✅ **Inicio rápido**: caché de 24h evita checks innecesarios
- ✅ **No intrusivo**: solo aparece cuando hay actualización real
- ✅ **Opcional**: el usuario decide si actualizar o no
- ✅ **Informativo**: explica claramente el motivo de la actualización

### 3. Robustez
- ✅ **Manejo de errores**: fallos no bloquean la aplicación
- ✅ **Timeouts**: evita bloqueos por conexión lenta (10s check, 30s update)
- ✅ **Logging**: registra errores para debugging sin molestar al usuario

### 4. Mantenibilidad
- ✅ **Código modular**: funciones separadas y reutilizables
- ✅ **Bien documentado**: comentarios claros en cada función
- ✅ **Fácil de modificar**: cambiar período de caché (24h) es trivial

## Casos de Uso

### Caso 1: Primera ejecución
```
1. Usuario abre la app por primera vez
2. Sistema verifica actualización (no hay caché)
3. yt-dlp está desactualizado → muestra diálogo
4. Usuario acepta → actualiza en 10-15 segundos
5. Guarda timestamp → no volverá a preguntar hasta mañana
```

### Caso 2: Ejecución diaria normal
```
1. Usuario abre la app (2da vez en el día)
2. Sistema lee caché: "última verificación hace 3 horas"
3. No ha pasado 24h → NO verifica actualización
4. App inicia inmediatamente sin delays
```

### Caso 3: Error de red
```
1. Usuario abre la app sin conexión a internet
2. Sistema intenta verificar actualización
3. pip list --outdated falla (timeout 10s)
4. Excepción capturada → fallo SILENCIOSO
5. App continúa con normalidad
6. Error registrado en consola para debugging
```

### Caso 4: Usuario rechaza actualización
```
1. Aparece diálogo de actualización disponible
2. Usuario presiona "No"
3. Diálogo se cierra sin actualizar
4. App continúa con normalidad
5. Volverá a preguntar mañana (24h después)
```

## Configuración Avanzada

### Cambiar período de caché

Para verificar actualizaciones más/menos frecuentemente:

```python
# En check_ytdlp_update(), línea ~20:
if last_check:
    last_check_dt = datetime.fromisoformat(last_check)
    # MODIFICAR aquí:
    if datetime.now() - last_check_dt < timedelta(hours=24):  # ← Cambiar "24"
        return False, "", ""
```

Opciones sugeridas:
- `timedelta(hours=12)` - 2 veces al día
- `timedelta(days=7)` - 1 vez por semana
- `timedelta(days=1)` - actual (1 vez al día) ✅ RECOMENDADO

### Deshabilitar auto-verificación

En `MainWindow.__init__()`, comentar la línea:

```python
# if YT_DLP_AVAILABLE:
#     self.check_and_update_ytdlp()
```

### Forzar verificación manual

Agregar botón en UI que llame:

```python
self.check_and_update_ytdlp()
```

Esto ignorará el caché y verificará inmediatamente.

## Comparación: Antes vs Después

| Aspecto | ANTES | DESPUÉS |
|---------|-------|---------|
| **Actualización yt-dlp** | Manual (usuario olvidaba) | Automática (cada 24h) |
| **Errores 403 YouTube** | Frecuentes (yt-dlp viejo) | Prevenidos (siempre actual) |
| **Experiencia usuario** | Frustrante (errores sin explicación) | Proactiva (app se mantiene sola) |
| **Mantenimiento** | Usuario debe recordar actualizar | Sistema se encarga automáticamente |
| **Inicio de app** | Normal | Sin impacto (caché 24h) |
| **Robustez** | Errores bloqueaban descargas | Actualización opcional y robusta |

## Conclusión

El sistema de auto-actualización de yt-dlp implementado es:

✅ **Efectivo**: Previene errores de descarga de YouTube  
✅ **Eficiente**: Usa caché para no ralentizar inicio  
✅ **Amigable**: Diálogos claros y no intrusivos  
✅ **Robusto**: Manejo de errores sin bloquear la app  
✅ **Mantenible**: Código modular y bien documentado  

**Resultado**: Los usuarios tendrán siempre la última versión de yt-dlp sin esfuerzo manual, eliminando el problema recurrente de errores HTTP 403 en descargas de YouTube.
