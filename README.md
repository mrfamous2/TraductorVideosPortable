# 🎥 Traductor de Videos Portátil

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://python.org)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-yellow)](https://openai.com/research/whisper)
[![Argos Translate](https://img.shields.io/badge/Argos%20Translate-Offline-green)](https://www.argosopentech.com/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-lightgrey)](LICENSE)

## 📝 Descripción del Proyecto

Aplicación **100% local y portátil** que transcribe videos en inglés y genera subtítulos traducidos al español automáticamente. Todo el procesamiento ocurre en tu propia computadora, **sin enviar datos a internet**.

## 🛠️ Tecnologías y Modelos Utilizados

### **Lenguaje de Programación**
- **Python 3.10** - Lenguaje principal del proyecto

### **Modelos de IA**
- **Whisper (OpenAI)** - Modelo de transcripción de audio a texto
  - Modelos disponibles: `tiny`, `base`, `small`, `medium`, `large`
  - Precisión: desde ~75% (tiny) hasta ~95% (large)
  - Tamaño: desde 75MB (tiny) hasta 2.9GB (large)

- **Argos Translate** - Motor de traducción local
  - Traducción inglés → español completamente offline
  - Modelos neuronales basados en OpenNMT

### **Herramientas**
- **FFmpeg** - Extracción de audio de videos
- **PyInstaller** - Empaquetado en un solo .exe portátil

## ⚙️ Características Principales

- ✅ **Sin internet** - Todo el procesamiento es local
- ✅ **Portátil** - Un solo archivo .exe, no requiere instalación
- ✅ **Múltiples modelos** - Elige entre velocidad y precisión
- ✅ **Privacidad total** - Tus videos nunca salen de tu PC
- ✅ **Subtítulos automáticos** - Genera archivos .srt listos para usar

## 📊 Rendimiento Estimado

| Modelo | RAM | Video 30min | Precisión |
|--------|-----|-------------|-----------|
| tiny   | 1GB | 10-15 min   | ~75%      |
| base   | 1GB | 20-30 min   | ~85%      |
| small  | 2GB | 40-60 min   | ~90%      |
| medium | 5GB | 60-90 min   | ~93%      |
| large  | 10GB| 90-120 min  | ~95%      |

## 🚀 Cómo Funciona Internamente

1. **FFmpeg** extrae el audio del video
2. **Whisper** transcribe el audio a texto en inglés
3. **Argos Translate** traduce el texto a español
4. **Generación de SRT** crea el archivo de subtítulos

## 📁 Estructura del Proyecto
TraductorVideosPortable/
├── traductor_portable.py # Código principal
├── empaquetar_portable.py # Script de empaquetado
├── ffmpeg/ # Ejecutable de FFmpeg
├── modelos/ # Modelos de Whisper (descarga automática)
├── argos_models/ # Modelos de traducción (descarga automática)
└── dist/ # Ejecutable compilado
└── TraductorVideosPortable.exe


## 📥 Instalación y Uso

1. **Descarga** el ejecutable desde [Releases](https://github.com/mrfamous2/TraductorVideosPortable/releases)
2. **Ejecuta** el archivo .exe
3. **Elige** el modelo de transcripción (recomiendo "base")
4. **Arrastra** tu video a la ventana
5. **Espera** a que termine el proceso
6. **Encuentra** los subtítulos .srt junto a tu video

## 👨‍💻 Autor

**mrfamous** - [GitHub](https://github.com/mrfamous2)

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver archivo [LICENSE](LICENSE)
