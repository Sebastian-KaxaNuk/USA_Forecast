from cx_Freeze import setup, Executable
import os

# Detect platform-specific base
base = None
if os.name == "nt":
    base = "Console"  # Usa "Win32GUI" si es app con GUI (sin terminal)

executables = [
    Executable(
        script="__main__.py",
        base=base,
        target_name="USA_Forecast.exe",
        icon="assets/image_ico.ico",
    )
]

setup(
    name="USA_ForecastApp",
    version="1.0",
    description="Sistema de price targets",
    executables=executables,
    options={
        "build_exe": {
            "include_files": [
                ("assets", "assets"),
                ("Config", "Config"),
                ("Output", "Output"),
            ],
            "build_exe": "build_usa_forecast"
        }
    }
)
