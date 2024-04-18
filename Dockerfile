FROM python:3.9

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que se ejecuta la aplicación
EXPOSE 8080

# Definir el comando para ejecutar la aplicación
CMD ["python", "main.py"]
