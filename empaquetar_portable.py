import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("🎁 EMPAQUETADOR - VERSIÓN CORREGIDA")
    print("=" * 60)

    # Verificar que estamos en la carpeta correcta
    carpeta_actual = os.getcwd()
    print(f"\n📂 Carpeta actual: {carpeta_actual}")

    # Buscar el archivo principal
    archivo_principal = None
    posibles_nombres = ["traductor_portable.py", "traductor_Portable.py", "TraductorPortable.py"]

    for nombre in posibles_nombres:
        if os.path.exists(nombre):
            archivo_principal = nombre
            print(f"✅ Archivo principal encontrado: {archivo_principal}")
            break

    if not archivo_principal:
        print("❌ ERROR: No encuentro el archivo principal")
        print(f"   Archivos encontrados: {os.listdir('.')}")
        return

    # Verificar ffmpeg
    ruta_ffmpeg = None
    posibles_ffmpeg = [
        os.path.join("ffmpeg", "bin", "ffmpeg.exe"),
        "ffmpeg.exe",
        os.path.join("bin", "ffmpeg.exe")
    ]

    for ruta in posibles_ffmpeg:
        if os.path.exists(ruta):
            ruta_ffmpeg = ruta
            print(f"✅ FFmpeg encontrado: {ruta_ffmpeg}")
            break

    if not ruta_ffmpeg:
        print("❌ No encuentro ffmpeg.exe")
        print("   Buscando en todo el directorio...")
        for root, dirs, files in os.walk("."):
            if "ffmpeg.exe" in files:
                ruta_ffmpeg = os.path.join(root, "ffmpeg.exe")
                print(f"✅ Encontrado en: {ruta_ffmpeg}")
                break
        else:
            print("❌ No se encontró ffmpeg.exe")
            return

    # Crear comando de empaquetado
    comando = [
        "pyinstaller",
        "--onefile",
        "--name", "TraductorVideosPortable",
        "--add-data", f"{ruta_ffmpeg};.",
        "--hidden-import", "whisper",
        "--hidden-import", "whisper.audio",
        "--hidden-import", "whisper.normalizers",
        "--hidden-import", "whisper.normalizers.basic",
        "--hidden-import", "whisper.normalizers.english",
        "--hidden-import", "argostranslate",
        "--hidden-import", "argostranslate.package",
        "--hidden-import", "argostranslate.translate",
        "--hidden-import", "torch",
        "--hidden-import", "torch._C",
        "--hidden-import", "torch.utils",
        "--hidden-import", "torch.utils.data",
        "--hidden-import", "torch.nn",
        "--hidden-import", "torch.nn._functions",
        "--hidden-import", "torch.nn.modules",
        "--hidden-import", "torch.nn.parallel",
        "--hidden-import", "torch.optim",
        "--hidden-import", "torch.serialization",
        "--hidden-import", "numpy",
        "--collect-all", "whisper",
        "--collect-all", "argostranslate",
        "--collect-all", "torch",
        "--clean",
        "--noconfirm",
        archivo_principal
    ]

    print("\n⚙️ Comando a ejecutar:")
    print(" ".join(comando))
    print("\n🕐 Empaquetando... (esto toma varios minutos)")

    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        print("\n✅ ¡EMPAQUETADO COMPLETADO!")

        exe_path = os.path.join("dist", "TraductorVideosPortable.exe")
        if os.path.exists(exe_path):
            tamaño = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n📁 Ejecutable creado: {exe_path}")
            print(f"📦 Tamaño: {tamaño:.1f} MB")
            print(f"\n🔍 Verifica que el traductor funcione antes de distribuir")
        else:
            print("\n❌ No se encontró el ejecutable")

    except subprocess.CalledProcessError as e:
        print("\n❌ Error durante el empaquetado")
        print("\n📋 Detalles del error:")
        if e.stderr:
            lineas = e.stderr.split('\n')
            for linea in lineas[-20:]:
                print(linea)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()