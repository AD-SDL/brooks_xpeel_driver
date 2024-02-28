FROM ghcr.io/ad-sdl/wei

LABEL org.opencontainers.image.source=https://github.com/AD-SDL/brooks_xpeel_module
LABEL org.opencontainers.image.description="Drivers and REST API's for the brooks_xpeel peeler"
LABEL org.opencontainers.image.licenses=MIT

#########################################
# Module specific logic goes below here #
#########################################

RUN mkdir -p brooks_xpeel_module

COPY ./brooks_xpeel_driver brooks_xpeel_module/brooks_xpeel_driver
COPY ./scripts brooks_xpeel_module/scripts
COPY ./README.md brooks_xpeel_module/README.md
COPY ./pyproject.toml brooks_xpeel_module/pyproject.toml
COPY ./tests brooks_xpeel_module/tests

RUN --mount=type=cache,target=/root/.cache \
    pip install -e ./brooks_xpeel_module

CMD ["python", "brooks_xpeel_module/scripts/brooks_xpeel_rest_node.py"]

#########################################
