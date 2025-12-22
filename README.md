# 🪙 Binance CryptoBox Wrapper
![binance_wrapper](https://github.com/user-attachments/assets/e0615cb7-43e1-457f-8b68-9262a9147920)

> **Automatización inteligente para capturar Crypto Boxes de Telegram en tiempo real.**

---

## ✨ Características Principales (v2.0.0)
* 🚀 **Rendimiento Optimizado:** Migración a `Telethon` para máxima velocidad.
* ⏱️ **Simulación Humana:** Delay inteligente de 1-5s para evitar baneos.
* 📊 **Consola Detallada:** Reportes en vivo de tokens, montos y estados.
* 🛡️ **Gestión de Errores:** Pausa automática en caso de saturación (timeouts).
* ⚙️ **Configuración Centralizada:** Todo se edita en `core/config.py`.

---

## 🛠️ Instalación y Configuración

1. **Requisitos:** Instala [Python 3.11+](https://www.python.org/downloads/) y [Git](https://git-scm.com/).
2. **Clonar:** `git clone https://github.com/devbutlazy/Binance-RedPacket-Wrapper`
3. **Dependencias:** Entra a la carpeta y ejecuta `pip install -r requirements.txt`
4. **Telegram API:** Pon tu `API_HASH` y `API_ID` (de my.telegram.org) en `core/config.py`.
5. **Binance Cookies:** - Ve a [Binance Crypto Box](https://www.binance.com/uk-UA/my/wallet/account/payment/cryptobox) y pulsa `F12`.
   - Canjea un código, busca la petición `grabV2` en **Network**.
   - Copia los headers (`cookie`, `device-info`, etc.) a `core/config.py`.

---

## 🚀 Uso y Compilación

**Para correrlo:** `python main.py`

**Para crear un EXE:**
Usa los archivos en la carpeta `BUILD/`. Recuerda configurar el `config.py` **antes** de compilar.

---

## 🤝 Créditos y Personalización
Este repositorio está basado originalmente en el trabajo de **devbutlazy**. 
He añadido mejoras personalizadas y optimizaciones adicionales para mejorar la experiencia y la estabilidad del bot.

---

## 📜 Licencia
* **Licencia:** MIT | **Base original por:** devbutlazy
