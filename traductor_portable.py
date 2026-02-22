#!/usr/bin/env python
"""
TRADUCTOR DE VIDEOS PORTÁTIL - VERSIÓN FINAL CORREGIDA
Con todas las correcciones para Argos Translate y FFmpeg
"""

import os
import sys
import time
import subprocess
import tempfile
import shutil
import traceback
from pathlib import Path

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

def obtener_ruta_base():
    """Obtiene la ruta base del ejecutable o script"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def obtener_ruta_recurso(nombre_recurso):
    """Busca un recurso en múltiples ubicaciones posibles"""
    ruta_base = obtener_ruta_base()
    
    posibles_rutas = [
        os.path.join(ruta_base, nombre_recurso),
        os.path.join(ruta_base, "recursos", nombre_recurso),
        os.path.join(ruta_base, "bin", nombre_recurso),
        os.path.join(ruta_base, "ffmpeg", "bin", nombre_recurso),
        os.path.join(ruta_base, "ffmpeg", nombre_recurso),
    ]
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        posibles_rutas.append(os.path.join(sys._MEIPASS, nombre_recurso))
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    
    return None

# Importaciones
try:
    import whisper
    import argostranslate.package
    import argostranslate.translate
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("   Asegúrate de tener instalados: whisper, argostranslate")
    input("\nPresiona Enter para salir...")
    sys.exit(1)

# ============================================================
# PARCHAR WHISPER PARA FFMPEG
# ============================================================

def parchear_whisper_ffmpeg(ruta_ffmpeg):
    """Parchea Whisper para usar FFmpeg específico"""
    if not ruta_ffmpeg or ruta_ffmpeg == "ffmpeg":
        return False
    
    try:
        if not hasattr(whisper.audio, '_original_load_audio'):
            whisper.audio._original_load_audio = whisper.audio.load_audio
        
        def load_audio_parchada(file, sr=16000):
            import numpy as np
            cmd = [
                ruta_ffmpeg,
                "-i", file,
                "-f", "s16le",
                "-ac", "1",
                "-ar", str(sr),
                "-"
            ]
            try:
                out = subprocess.run(cmd, capture_output=True, check=True).stdout
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"FFmpeg error: {e.stderr.decode()}") from e
            return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0
        
        whisper.audio.load_audio = load_audio_parchada
        print("✅ Whisper parchado para usar FFmpeg específico")
        return True
    except Exception as e:
        print(f"⚠️ No se pudo parchear Whisper: {e}")
        return False

# ============================================================
# CLASE PRINCIPAL
# ============================================================

class TraductorPortatil:
    """Traductor local con soporte para rutas con espacios"""
    
    def __init__(self):
        print("📚 Inicializando traductor portátil...")
        self.ruta_base = obtener_ruta_base()
        self.ruta_modelos = os.path.join(self.ruta_base, "modelos")
        self.ruta_ffmpeg = None
        self.modelo_whisper = None
        self.traductor = None
        self.traductor_listo = False
        
        # Crear carpetas necesarias
        os.makedirs(self.ruta_modelos, exist_ok=True)
        os.makedirs(os.path.join(self.ruta_base, "argos_models"), exist_ok=True)
        
        # Configurar FFmpeg
        self.configurar_ffmpeg()
        
        # Parchear Whisper
        if self.ruta_ffmpeg and self.ruta_ffmpeg != "ffmpeg":
            parchear_whisper_ffmpeg(self.ruta_ffmpeg)
        
        # Inicializar traductor (VERSIÓN CORREGIDA)
        self.inicializar_traductor()
    
    # ------------------------------------------------------------
    # CONFIGURACIÓN FFMPEG
    # ------------------------------------------------------------
    
    def configurar_ffmpeg(self):
        """Busca y configura FFmpeg en el sistema"""
        print("🔧 Configurando FFmpeg...")
        self.ruta_ffmpeg = obtener_ruta_recurso("ffmpeg.exe")
        
        if self.ruta_ffmpeg and os.path.exists(self.ruta_ffmpeg):
            print(f"✅ FFmpeg encontrado en: {self.ruta_ffmpeg}")
            ffmpeg_dir = os.path.dirname(self.ruta_ffmpeg)
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            os.environ["FFMPEG_BINARY"] = self.ruta_ffmpeg
        else:
            print("⚠️ No se encontró FFmpeg. Intentando usar el del sistema...")
            try:
                subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
                self.ruta_ffmpeg = "ffmpeg"
                print("✅ FFmpeg encontrado en PATH")
            except:
                print("❌ FFmpeg no encontrado")
                self.ruta_ffmpeg = None
    
    # ------------------------------------------------------------
    # CONFIGURACIÓN TRADUCTOR (VERSIÓN CORREGIDA)
    # ------------------------------------------------------------
    
    def inicializar_traductor(self):
        """Configura el traductor de idiomas local con instalación forzada"""
        print("📖 Configurando traductor inglés-español...")
        
        # Configurar carpeta de modelos de Argos
        argos_data = os.path.join(self.ruta_base, "argos_models")
        os.environ["ARGOS_PACKAGES_DIR"] = argos_data
        
        try:
            # Actualizar índice
            print("   Actualizando índice de paquetes...")
            argostranslate.package.update_package_index()
            
            # ✅ CORREGIDO: get_installed_packages está en package
            paquetes_instalados = argostranslate.package.get_installed_packages()
            print(f"   Paquetes instalados: {len(paquetes_instalados)}")
            
            # Verificar si inglés-español ya está instalado
            instalado = False
            for p in paquetes_instalados:
                if hasattr(p, 'from_code') and hasattr(p, 'to_code'):
                    if p.from_code == "en" and p.to_code == "es":
                        instalado = True
                        print(f"   ✅ Modelo encontrado: {p}")
                        break
            
            if not instalado:
                print("   ⚠️ Modelo inglés-español NO instalado")
                print("   📥 Descargando e instalando modelo...")
                
                # Obtener paquetes disponibles
                paquetes = argostranslate.package.get_available_packages()
                paquete_es = None
                
                for p in paquetes:
                    if p.from_code == "en" and p.to_code == "es":
                        paquete_es = p
                        print(f"   ✅ Paquete encontrado: {p}")
                        break
                
                if paquete_es:
                    print(f"   Descargando desde: {paquete_es}")
                    ruta_paquete = paquete_es.download()
                    print(f"   Instalando desde: {ruta_paquete}")
                    argostranslate.package.install_from_path(ruta_paquete)
                    print("   ✅ Modelo instalado correctamente")
                else:
                    print("   ❌ No se encontró paquete de traducción")
                    self.traductor_listo = False
                    return
            else:
                print("   ✅ Modelo inglés-español ya instalado")
            
            # ✅ CORREGIDO: Obtener idiomas instalados (translate)
            print("   Obteniendo traductor...")
            installed_languages = argostranslate.translate.get_installed_languages()
            
            from_lang = None
            to_lang = None
            
            for lang in installed_languages:
                if lang.code == "en":
                    from_lang = lang
                if lang.code == "es":
                    to_lang = lang
            
            if from_lang and to_lang:
                self.traductor = from_lang.get_translation(to_lang)
                
                if self.traductor:
                    self.traductor_listo = True
                    print("   ✅ Traductor listo para usar")
                    
                    # PRUEBA DE TRADUCCIÓN
                    prueba = "Hello world"
                    try:
                        traduccion = self.traductor.translate(prueba)
                        print(f"   📝 Prueba: '{prueba}' → '{traduccion}'")
                        if traduccion == prueba:
                            print("   ⚠️ ADVERTENCIA: La traducción devolvió el mismo texto")
                        else:
                            print("   ✅ Traducción funcionando correctamente")
                    except Exception as e:
                        print(f"   ❌ Error en prueba: {e}")
                else:
                    print("   ❌ No se pudo obtener el traductor")
                    self.traductor_listo = False
            else:
                print("   ❌ No se encontraron los idiomas instalados")
                self.traductor_listo = False
                
        except Exception as e:
            print(f"❌ Error configurando traductor: {e}")
            traceback.print_exc()
            self.traductor_listo = False
    
    # ------------------------------------------------------------
    # CARGA DE MODELO WHISPER
    # ------------------------------------------------------------
    
    def cargar_modelo_whisper(self, modelo="base"):
        """Carga el modelo de Whisper"""
        print(f"🎤 Cargando modelo Whisper '{modelo}'...")
        inicio = time.time()
        
        try:
            os.environ["WHISPER_CACHE_DIR"] = self.ruta_modelos
            self.modelo_whisper = whisper.load_model(
                modelo, 
                device="cpu",
                download_root=self.ruta_modelos
            )
            print(f"✅ Modelo Whisper cargado en {time.time()-inicio:.1f} segundos")
            return True
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            traceback.print_exc()
            return False
    
    # ------------------------------------------------------------
    # TRADUCCIÓN
    # ------------------------------------------------------------
    
    def traducir_texto(self, texto):
        """Traduce texto de inglés a español"""
        if not self.traductor_listo or not self.traductor:
            if len(texto) > 30:
                print(f"   ⚠️ Traductor no disponible, texto sin traducir: {texto[:30]}...")
            return texto
        
        try:
            resultado = self.traductor.translate(texto)
            if resultado == texto and len(texto) > 30:
                print(f"   ⚠️ Traducción devolvió mismo texto: {texto[:30]}...")
            return resultado
        except Exception as e:
            print(f"   ❌ Error traduciendo: {e}")
            return texto
    
    # ------------------------------------------------------------
    # EXTRACCIÓN DE AUDIO
    # ------------------------------------------------------------
    
    def extraer_audio(self, ruta_video):
        """Extrae audio usando FFmpeg"""
        print("🔊 Extrayendo audio del video...")
        
        if not self.ruta_ffmpeg:
            print("❌ FFmpeg no disponible")
            return None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                nombre_temp_video = "video_temp.mp4"
                ruta_temp_video = os.path.join(temp_dir, nombre_temp_video)
                print(f"📁 Copiando video a carpeta temporal...")
                shutil.copy2(ruta_video, ruta_temp_video)
                
                audio_temp = os.path.join(temp_dir, "audio_temp.wav")
                comando = [
                    self.ruta_ffmpeg,
                    "-i", ruta_temp_video,
                    "-vn",
                    "-acodec", "pcm_s16le",
                    "-ar", "16000",
                    "-ac", "1",
                    "-y",
                    audio_temp
                ]
                
                print(f"⚙️ Ejecutando FFmpeg...")
                subprocess.run(comando, check=True, capture_output=True, text=True, timeout=300)
                
                if os.path.exists(audio_temp):
                    tamaño = os.path.getsize(audio_temp) / (1024*1024)
                    print(f"✅ Audio extraído: {tamaño:.2f} MB")
                    
                    ruta_final_audio = os.path.join(
                        os.path.dirname(ruta_video),
                        os.path.basename(ruta_video).rsplit('.', 1)[0] + '_temp_audio.wav'
                    )
                    shutil.copy2(audio_temp, ruta_final_audio)
                    print(f"✅ Audio guardado en: {ruta_final_audio}")
                    return ruta_final_audio
                else:
                    print("❌ No se generó el archivo de audio")
                    return None
                    
            except subprocess.TimeoutExpired:
                print("❌ Timeout en FFmpeg")
                return None
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en FFmpeg: {e.stderr[:200] if e.stderr else 'Desconocido'}")
                return None
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                return None
    
    # ------------------------------------------------------------
    # PROCESAMIENTO PRINCIPAL
    # ------------------------------------------------------------
    
    def procesar_video(self, ruta_video, modelo="base"):
        """Procesa un video completo"""
        
        print("\n" + "="*60)
        print("🎬 INICIANDO PROCESAMIENTO")
        print("="*60)
        
        ruta_video = os.path.abspath(ruta_video)
        print(f"📹 Video: {ruta_video}")
        
        if not os.path.exists(ruta_video):
            print(f"❌ No existe el video")
            return None
        
        if not self.modelo_whisper:
            if not self.cargar_modelo_whisper(modelo):
                return None
        
        audio_path = self.extraer_audio(ruta_video)
        if not audio_path:
            return None
        
        print("📝 Transcribiendo audio...")
        inicio = time.time()
        
        try:
            resultado = self.modelo_whisper.transcribe(
                audio_path,
                language="en",
                task="transcribe",
                fp16=False,
                verbose=False
            )
            print(f"✅ Transcripción completada en {time.time()-inicio:.1f} segundos")
            print(f"   Se encontraron {len(resultado['segments'])} segmentos")
        except Exception as e:
            print(f"❌ Error transcribiendo: {e}")
            traceback.print_exc()
            self.limpiar_archivo(audio_path)
            return None
        
        print("🔄 Generando subtítulos traducidos...")
        srt_path = self.generar_srt(resultado, ruta_video)
        self.limpiar_archivo(audio_path)
        
        return srt_path
    
    # ------------------------------------------------------------
    # GENERACIÓN DE SRT
    # ------------------------------------------------------------
    
    def generar_srt(self, resultado, ruta_video):
        """Genera archivo SRT con traducción"""
        nombre_base = os.path.splitext(ruta_video)[0]
        srt_path = f"{nombre_base}_espanol.srt"
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            total = len(resultado['segments'])
            traducidos = 0
            no_traducidos = 0
            
            for i, segmento in enumerate(resultado['segments']):
                texto_original = segmento['text']
                texto_traducido = self.traducir_texto(texto_original)
                
                if texto_traducido == texto_original:
                    no_traducidos += 1
                else:
                    traducidos += 1
                
                inicio = self.formato_srt(segmento['start'])
                fin = self.formato_srt(segmento['end'])
                
                f.write(f"{i+1}\n")
                f.write(f"{inicio} --> {fin}\n")
                f.write(f"{texto_traducido}\n\n")
                
                if (i + 1) % 10 == 0 or (i + 1) == total:
                    print(f"   Progreso: {i+1}/{total} segmentos")
            
            print(f"   📊 Estadísticas: {traducidos} traducidos, {no_traducidos} sin traducir")
        
        return srt_path
    
    def formato_srt(self, segundos):
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segs = int(segundos % 60)
        milisegundos = int((segundos - int(segundos)) * 1000)
        return f"{horas:02d}:{minutos:02d}:{segs:02d},{milisegundos:03d}"
    
    def limpiar_archivo(self, ruta):
        try:
            if ruta and os.path.exists(ruta):
                os.remove(ruta)
        except:
            pass

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("="*60)
    print("🎥 TRADUCTOR DE VIDEOS PORTÁTIL - VERSIÓN FINAL CORREGIDA")
    print("="*60)
    print("\n📌 Correcciones aplicadas:")
    print("   • API correcta de Argos Translate (package vs translate)")
    print("   • Instalación automática de modelos")
    print("   • Manejo robusto de errores")
    
    # Verificar argumentos
    ruta_video = None
    if len(sys.argv) > 1:
        ruta_video = " ".join(sys.argv[1:]).strip('"\'')
        print(f"\n📂 Video recibido: {ruta_video}")
    
    # Crear traductor
    traductor = TraductorPortatil()
    
    # Verificar estado del traductor
    if not traductor.traductor_listo:
        print("\n" + "="*40)
        print("⚠️  EL TRADUCTOR NO ESTÁ FUNCIONANDO")
        print("="*40)
        print("\nPosibles soluciones:")
        print("1. Verificar conexión a internet (para descargar modelo)")
        print("2. Ejecutar: pip install --upgrade argostranslate")
        print("3. Verificar espacio en disco")
        
        continuar = input("\n¿Continuar de todas formas? (s/n): ").lower()
        if continuar != 's':
            return
    
    # Seleccionar modelo
    print("\n" + "-"*40)
    print("📊 MODELOS DISPONIBLES:")
    print("1. tiny   (más rápido, ~1GB RAM)")
    print("2. base   (recomendado, ~1GB RAM)")
    print("3. small  (mejor calidad, ~2GB RAM)")
    print("4. medium (alta calidad, ~5GB RAM)")
    print("5. large  (máxima calidad, ~10GB RAM)")
    
    opcion = input("\nElige modelo (1-5) [2]: ").strip() or "2"
    modelos = {'1': 'tiny', '2': 'base', '3': 'small', '4': 'medium', '5': 'large'}
    modelo = modelos.get(opcion, 'base')
    
    # Obtener video
    if not ruta_video:
        print("\n" + "-"*40)
        print("💡 Arrastra el video a esta ventana o escribe la ruta")
        ruta_video = input("📂 Ruta del video: ").strip().strip('"\'')
    
    # Limpiar ruta (PowerShell)
    if ruta_video.startswith("& "):
        ruta_video = ruta_video[2:].strip("'\"")
    
    # Verificar video
    if not os.path.exists(ruta_video):
        print(f"\n❌ ERROR: No encuentro el archivo: {ruta_video}")
        input("\nPresiona Enter para salir...")
        return
    
    # Mostrar información
    print(f"\n📁 Carpeta: {os.path.dirname(ruta_video)}")
    print(f"📄 Nombre: {os.path.basename(ruta_video)}")
    print(f"💾 Tamaño: {os.path.getsize(ruta_video) / (1024*1024):.2f} MB")
    
    # Procesar
    print(f"\n⏳ Procesando con modelo '{modelo}'...")
    inicio = time.time()
    
    try:
        resultado = traductor.procesar_video(ruta_video, modelo)
        
        if resultado:
            tiempo = time.time() - inicio
            print("\n" + "="*50)
            print("✅ ¡PROCESO COMPLETADO!")
            print("="*50)
            print(f"📁 Subtítulos: {resultado}")
            
            if os.path.exists(resultado):
                tamaño = os.path.getsize(resultado) / 1024
                print(f"📊 Tamaño: {tamaño:.1f} KB")
                
                print("\n📄 Vista previa:")
                with open(resultado, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()[:6]
                    for linea in lineas:
                        print(linea.strip())
            else:
                print("⚠️ El archivo de subtítulos no se encuentra")
            
            print(f"\n⏱️ Tiempo total: {tiempo:.1f} segundos")
        else:
            print("\n❌ Error durante el procesamiento")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Proceso cancelado")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        traceback.print_exc()
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        traceback.print_exc()
        input("\nPresiona Enter para salir...")