# 🔴 Error 403 al Descargar de YouTube - Solución

## 🚨 **Problema**

Al intentar descargar audio desde YouTube, obtienes:
```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

## 📋 **¿Por qué ocurre?**

YouTube ha implementado restricciones más agresivas que bloquean herramientas automatizadas como yt-dlp. Esto es parte de sus medidas anti-bot.

---

## ✅ **SOLUCIONES** (en orden de efectividad)

### **Solución 1: Actualizar yt-dlp (LA MÁS IMPORTANTE)** ⭐

YouTube cambia constantemente sus restricciones, y yt-dlp se actualiza frecuentemente para eludirlas.

```bash
# En tu entorno virtual
.venv\Scripts\activate
pip install -U yt-dlp

# O con pip directamente
pip install --upgrade yt-dlp
```

**Verifica la versión:**
```bash
yt-dlp --version
```

Debe ser **2023.12.30 o superior**. Si es más antigua, actualiza.

---

### **Solución 2: Cambios en el Código (YA APLICADOS)** ✅

He actualizado `main.py` con las siguientes mejoras:

#### **A. Cliente Android de YouTube**
```python
'extractor_args': {
    'youtube': {
        'player_client': ['android', 'web'],
        'player_skip': ['webpage', 'configs'],
    }
}
```
Usa la API de Android de YouTube que suele tener menos restricciones.

#### **B. Headers de Navegador Real**
```python
'http_headers': {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept': 'text/html,application/xhtml+xml,...',
    # ... más headers
}
```
Simula un navegador real en lugar de un script.

#### **C. Reintentos y Timeouts**
```python
'socket_timeout': 30,
'retries': 3,
'fragment_retries': 3,
```

---

### **Solución 3: Usar Cookies de Navegador** 🍪

Si tienes una sesión activa en YouTube, puedes usar tus cookies:

#### **Opción A: Exportar cookies del navegador**

1. Instala extensión de navegador para exportar cookies:
   - Chrome/Edge: **"Get cookies.txt LOCALLY"**
   - Firefox: **"cookies.txt"**

2. Ve a YouTube en tu navegador (con sesión iniciada)

3. Exporta las cookies a un archivo `youtube_cookies.txt`

4. Modifica el código para usarlas:

```python
# En DownloadWorker.run(), en ydl_opts añade:
'cookiefile': 'youtube_cookies.txt',
```

#### **Opción B: Usar cookies del navegador directamente**

```python
# En ydl_opts añade:
'cookiesfrombrowser': ('chrome',),  # o 'firefox', 'edge', etc.
```

---

### **Solución 4: Proxies/VPN** 🌐

Si YouTube bloquea tu IP:

```python
# En ydl_opts añade:
'proxy': 'http://proxy-server:port',
# o
'geo_bypass': True,
'geo_bypass_country': 'US',
```

⚠️ **No recomendado** para uso general.

---

### **Solución 5: Alternativas a yt-dlp**

Si nada funciona, considera:

1. **youtube-dl** (más lento pero a veces funciona):
   ```bash
   pip uninstall yt-dlp
   pip install youtube-dl
   ```

2. **Descargar manualmente** con extensiones de navegador:
   - **Video DownloadHelper** (Firefox)
   - **SaveFrom.net** (varios navegadores)

3. **Usar servicios online**:
   - [ytmp3.cc](https://ytmp3.cc/)
   - [y2mate.com](https://www.y2mate.com/)
   
   Luego arrastra los archivos descargados al conversor.

---

## 🔧 **PASOS RECOMENDADOS (EN ORDEN)**

### 1️⃣ **PRIMERO: Actualizar yt-dlp**
```bash
cd "c:\Users\marti\Documents\!PROGRAMAS\Apps\audio_converter_gui"
.venv\Scripts\activate
pip install --upgrade yt-dlp
```

### 2️⃣ **Reiniciar la aplicación**
```bash
# Cierra la aplicación si está abierta
.venv\Scripts\python main.py
```

### 3️⃣ **Probar con un video diferente**
Algunos videos tienen restricciones específicas. Prueba con:
- Un video público diferente
- Un video sin restricciones de edad
- Un video corto (menos vigilado)

### 4️⃣ **Si sigue fallando: Usar cookies**

**Implementación rápida:**

```python
# En main.py, línea ~195, en ydl_opts añade DESPUÉS de 'extractor_args':

'cookiesfrombrowser': ('chrome',),  # Usa cookies de Chrome
# O si usas Firefox:
# 'cookiesfrombrowser': ('firefox',),
```

---

## 🧪 **Testing**

### Test 1: Video Público Simple
```
https://www.youtube.com/watch?v=jNQXAC9IVRw
```
"Me at the zoo" - El primer video de YouTube, sin restricciones.

### Test 2: Video Musical
```
https://www.youtube.com/watch?v=kJQP7kiw5Fk
```
"Despacito" - Si este falla, es probable que sea tu IP/región.

### Test 3: Tu Video Original
```
https://www.youtube.com/watch?v=5I6jIZHOsDY
```

---

## 📊 **Diagnóstico**

Ejecuta esto en PowerShell para diagnosticar:

```powershell
cd "c:\Users\marti\Documents\!PROGRAMAS\Apps\audio_converter_gui"
.venv\Scripts\activate
yt-dlp --version
yt-dlp -F "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

**Resultados esperados:**
- ✅ Si muestra una lista de formatos → yt-dlp funciona
- ❌ Si da error 403 → necesitas actualizar o usar cookies

---

## 🔍 **Logs Detallados**

Para ver exactamente qué está pasando:

```powershell
.venv\Scripts\activate
yt-dlp --verbose "https://www.youtube.com/watch?v=5I6jIZHOsDY"
```

Guarda el output completo y analiza:
- ¿Qué cliente usa? (android/web/ios)
- ¿Qué formato intenta descargar?
- ¿En qué paso falla?

---

## ⚡ **Solución Rápida para Aplicar Ahora**

### Opción A: Actualizar y Reiniciar (2 minutos)
```bash
.venv\Scripts\pip install -U yt-dlp
# Reinicia la aplicación
```

### Opción B: Añadir Cookies de Chrome (5 minutos)

Edita `main.py`, línea ~195, añade:
```python
'cookiesfrombrowser': ('chrome',),
```

Guarda, reinicia, prueba.

---

## 📞 **Si Nada Funciona**

### Plan B: Usar la App Sin YouTube
1. Descarga audio manualmente de YouTube (extensión de navegador)
2. Usa la app solo para **conversión** (arrastra los .webm/.opus)
3. La conversión funciona perfectamente sin internet

### Plan C: Downgrade de yt-dlp
```bash
pip install yt-dlp==2023.10.13
```
Versión más antigua pero estable.

---

## 🔮 **Prevención Futura**

### 1. Mantén yt-dlp Actualizado
```bash
# Cada semana:
pip install -U yt-dlp
```

### 2. Usa un Script de Actualización
Crea `update_ytdlp.bat`:
```batch
@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
pip install --upgrade yt-dlp
pause
```

### 3. Monitorea el Repo de yt-dlp
https://github.com/yt-dlp/yt-dlp/issues

Si hay problemas masivos con YouTube, ahí se reportan.

---

## 📚 **Recursos Adicionales**

- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp Wiki](https://github.com/yt-dlp/yt-dlp/wiki)
- [Cookies from Browser](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)

---

## ✅ **Checklist de Diagnóstico**

Antes de reportar el problema, verifica:

- [ ] yt-dlp está actualizado (versión 2023.12.30+)
- [ ] Probaste con un video diferente
- [ ] El video es público y disponible en tu región
- [ ] No tienes restricciones de red (firewall/proxy corporativo)
- [ ] FFmpeg está instalado correctamente
- [ ] Los cambios de código están aplicados
- [ ] Reiniciaste la aplicación después de cambios

---

**Estado Actual:** ✅ Los cambios en el código ya están aplicados.  
**Siguiente Paso:** Actualizar yt-dlp y reiniciar la aplicación.

```bash
# EJECUTA ESTO AHORA:
.venv\Scripts\pip install --upgrade yt-dlp
```

¡Después prueba de nuevo! 🚀
