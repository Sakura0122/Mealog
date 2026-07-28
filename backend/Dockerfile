FROM python:3.14 AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.25 /uv /bin/

COPY pyproject.toml uv.lock ./
# 完整版 Python 镜像提供 asyncmy 所需的编译工具，运行阶段仍使用 slim 镜像。
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv ./.venv
COPY src ./src

# 仅开放日志目录写权限，应用代码和依赖保持只读。
RUN useradd --no-create-home --user-group --uid 10001 appuser \
    && mkdir logs \
    && chown appuser:appuser logs

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips=*"]
