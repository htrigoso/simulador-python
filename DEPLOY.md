# Guía de Despliegue en Streamlit Community Cloud

## 📋 Checklist Pre-Deploy

✅ `requirements.txt` creado con dependencias necesarias
✅ `.gitignore` configurado para excluir archivos innecesarios
✅ README.md actualizado con instrucciones de instalación
✅ Código verificado y funcional localmente

## 🚀 Pasos para Publicar en Streamlit Community Cloud

### 1. Preparar el Repositorio en GitHub

```bash
# Inicializar Git (si no está inicializado)
git init

# Agregar archivos
git add .

# Hacer commit
git commit -m "Initial commit - EV Energy Simulator"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/captcha-v3.git
git branch -M main
git push -u origin main
```

### 2. Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Configura:
   - **Repository**: TU-USUARIO/captcha-v3
   - **Branch**: main
   - **Main file path**: main.py
5. Haz clic en "Deploy!"

### 3. Configuración Opcional

Si necesitas variables de entorno o secretos, créalos en:

- Settings → Secrets (formato TOML)

```toml
# Ejemplo (si fuera necesario)
[general]
app_name = "EV Energy Simulator"
```

### 4. URL de tu App

Tu app estará disponible en:

```
https://TU-USUARIO-captcha-v3-main.streamlit.app
```

## 🔧 Actualizar la App

Cada vez que hagas `git push` a la rama main, Streamlit Cloud actualizará automáticamente tu app.

```bash
# Hacer cambios en el código
git add .
git commit -m "Descripción de los cambios"
git push
```

## 📝 Notas Importantes

- **Plan gratuito**: Ilimitado para proyectos públicos
- **Recursos**: 1 GB RAM, CPU compartido
- **Límite**: 1 app por cuenta gratuita (puede variar)
- **Sleep mode**: La app se "despertará" cuando alguien la visite

## 🆘 Troubleshooting

### Error: "Requirements installation failed"

- Verifica que todas las dependencias en requirements.txt estén bien escritas
- Usa versiones compatibles (especificadas en requirements.txt)

### Error: "App is not responding"

- Revisa los logs en Streamlit Cloud
- Verifica que main.py no tenga errores de sintaxis

### La app es muy lenta

- Optimiza el código para usar cache con `@st.cache_data`
- Reduce cálculos pesados en cada interacción

## 🎉 Listo!

Una vez desplegado, actualiza el README.md con la URL real de tu app.
