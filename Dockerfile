FROM python:3.13-slim


# Instalar curl y dependencias
RUN apt-get update && apt-get install -y curl nodejs npm \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*


# Verifica si el binario se encuentra en .cargo y hazlo accesible globalmente
RUN find / -name uv -type f -executable -exec cp {} /usr/local/bin/uv \; || echo "uv not found"

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock* ./

# Usar el comando uv (ya en /usr/local/bin)
RUN uv sync --no-cache

# Copiar el resto del código
COPY . .
