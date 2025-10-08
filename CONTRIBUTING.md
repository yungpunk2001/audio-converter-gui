# Guía de Contribución

¡Gracias por tu interés en contribuir a Audio Converter GUI! 🎉

## Cómo contribuir

### Reportar Bugs
1. Verifica que el bug no haya sido reportado antes en [Issues](https://github.com/yungpunk2001/audio-converter-gui/issues)
2. Abre un nuevo Issue incluyendo:
   - Descripción clara del problema
   - Pasos para reproducirlo
   - Comportamiento esperado vs actual
   - Versión de Windows y Python
   - Logs o capturas de pantalla si son relevantes

### Sugerir Mejoras
1. Abre un Issue con la etiqueta "enhancement"
2. Describe claramente la funcionalidad propuesta
3. Explica por qué sería útil

### Enviar Pull Requests
1. **Fork** el repositorio
2. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
3. **Realiza tus cambios**:
   - Mantén el código limpio y comentado
   - Sigue el estilo existente (PEP 8 para Python)
   - Asegúrate de que el código funcione correctamente
4. **Commit** tus cambios:
   ```bash
   git commit -m "Descripción clara del cambio"
   ```
5. **Push** a tu fork:
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```
6. Abre un **Pull Request** hacia `main`

## Configuración del entorno de desarrollo

### Requisitos
- Python 3.10 o superior
- FFmpeg instalado o en `./bin/`

### Instalación
```bash
# Clonar el repositorio
git clone https://github.com/yungpunk2001/audio-converter-gui.git
cd audio-converter-gui

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar en desarrollo
```bash
python main.py
```

## Estilo de Código

### Python
- Seguir [PEP 8](https://pep8.org/)
- Usar encoding UTF-8: `# -*- coding: utf-8 -*-`
- Comentarios en español para mantener consistencia
- Type hints cuando sea posible
- Docstrings para funciones complejas

### Commits
- Mensajes claros y descriptivos
- En español o inglés (consistente con el proyecto)
- Ejemplos:
  - ✅ `Añade soporte para formato FLAC de 32-bit`
  - ✅ `Corrige bug en detección de FFmpeg en PATH`
  - ❌ `fix`
  - ❌ `cambios varios`

## Áreas de contribución

### Ideas de mejoras
- [ ] Soporte para conversión por lotes más avanzado
- [ ] Previsualización de audio antes de convertir
- [ ] Perfiles personalizados guardables
- [ ] Soporte para más formatos (DSD, etc.)
- [ ] Interfaz en otros idiomas
- [ ] Versión para Linux/macOS
- [ ] Tests unitarios
- [ ] Análisis de espectro pre/post conversión
- [ ] Normalización de volumen
- [ ] Edición de metadatos (tags ID3)

### Ayuda necesaria
- Pruebas en diferentes versiones de Windows
- Documentación mejorada
- Traducción de la interfaz
- Optimización de rendimiento
- Manejo de errores más robusto

## Preguntas

Si tienes dudas sobre cómo contribuir, abre un Issue con la etiqueta "question" o contacta al mantenedor.

¡Gracias por contribuir! 🚀
