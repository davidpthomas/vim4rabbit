# Container environment for developing the vim4rabbit plugin

# TODO: optimize base image; ubuntu represents a full OS env but is overkill for this plugin
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg git build-essential ncurses-dev python3-dev \
    lua5.3 liblua5.3-dev ruby-dev libperl-dev pkg-config gettext sudo bash unzip wget \
    vim \
  && rm -rf /var/lib/apt/lists/*

# Install Node.js 18 (Claude Code requires Node.js 18+)
RUN apt-get update && apt-get install -y nodejs npm \
  && rm -rf /var/lib/apt/lists/*

# Build & install latest Vim from GitHub releases (stable)
# TODO: Keeping this config in case we need to custom configure a vim version
#RUN set -eux; \
#    latest_url=$(curl -sL https://api.github.com/repos/vim/vim/releases/latest |  grep '"tarball_url"' | head -n1 | sed -E 's/."([^"]+)"./\1/'); \
#    curl -L "$latest_url" -o /tmp/vim.tar.gz; \
#    mkdir -p /tmp/vim-src && tar -xzf /tmp/vim.tar.gz -C /tmp/vim-src --strip-components=1; \
#    cd /tmp/vim-src; \
#    ./configure --with-features=huge \
#                --enable-multibyte \
#                --enable-python3interp=yes \
#                --enable-perlinterp \
#                --enable-rubyinterp \
#                --enable-luainterp \
#                --enable-gui=no \
#                --without-x && \
#    make -j"$(nproc)" && make install; \
#    rm -rf /tmp/vim* /tmp/vim-src

# Install Claude Code CLI (npm global)
RUN npm install -g @anthropic-ai/claude-code

# Create non-root developer user
ARG USERNAME=dev
ARG UID=1001
RUN useradd -m -u ${UID} ${USERNAME} && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME}

USER ${USERNAME}
WORKDIR /home/${USERNAME}
ENV PATH="/usr/local/bin:${PATH}"

RUN mkdir -p /home/${USERNAME}/.vim/plugged /home/${USERNAME}/.vim/autoload
COPY config/vimrc /home/${USERNAME}/.vimrc
COPY config/plug.vim /home/${USERNAME}/.vim/autoload/plug.vim

CMD ["bash"]
