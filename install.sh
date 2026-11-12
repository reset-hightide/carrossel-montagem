#!/usr/bin/env bash
# Instala a skill carrossel-montagem no Claude Code (Linux / macOS / Steam Deck).
# Uso: ./install.sh            -> copia a skill, cria o comando /post, o venv e o atalho
#      ./install.sh --link     -> usa link simbólico (quem vai editar a skill no próprio repo)
#      ./install.sh --no-shortcut
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MODE=copy; SHORTCUT=1
for a in "$@"; do case "$a" in --link) MODE=link;; --no-shortcut) SHORTCUT=0;; esac; done

mkdir -p "$CLAUDE_DIR/skills" "$CLAUDE_DIR/commands" "$CLAUDE_DIR/carrossel-marcas" "$HOME/Posts"
DEST="$CLAUDE_DIR/skills/carrossel-montagem"
if [ -e "$DEST" ] && [ ! -L "$DEST" ]; then mkdir -p "$CLAUDE_DIR/skills-backup"; mv "$DEST" "$CLAUDE_DIR/skills-backup/carrossel-montagem.$(date +%Y%m%d%H%M%S)"; echo "backup da skill antiga em $CLAUDE_DIR/skills-backup"; fi
rm -f "$DEST" 2>/dev/null || true
if [ "$MODE" = link ]; then ln -s "$HERE/skill" "$DEST"; else cp -r "$HERE/skill" "$DEST"; fi
cp "$HERE/commands/post.md" "$CLAUDE_DIR/commands/post.md"
echo "skill instalada em $DEST ($MODE) e comando /post criado"

# Ambiente Python das ferramentas (pptx, recorte, preview)
PY=python3; command -v $PY >/dev/null || { echo "Instale Python 3 e rode de novo."; exit 1; }
if [ ! -x "$HOME/.venvs/post/bin/python" ]; then $PY -m venv "$HOME/.venvs/post"; fi
"$HOME/.venvs/post/bin/pip" install -q --upgrade pip >/dev/null
"$HOME/.venvs/post/bin/pip" install -q -r "$HERE/requirements.txt"
echo "venv pronto em ~/.venvs/post"

[ "$SHORTCUT" = 1 ] || exit 0
CLAUDE_BIN="$(command -v claude || echo "$HOME/.local/bin/claude")"
case "$(uname)" in
  Darwin)
    F="$HOME/Desktop/Novo carrossel.command"
    printf '#!/bin/bash\ncd "$HOME"\n"%s" --chrome "/post"\n' "$CLAUDE_BIN" > "$F"; chmod +x "$F" ;;
  *)
    DESK="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
    mkdir -p "$HOME/.local/bin"
    L="$HOME/.local/bin/novo-carrossel"
    printf '#!/usr/bin/env bash\ncd "$HOME"\n"%s" --chrome "/post"\nexec bash\n' "$CLAUDE_BIN" > "$L"; chmod +x "$L"
    if command -v konsole >/dev/null; then TERM_CMD="konsole --workdir $HOME -e $L"
    elif command -v gnome-terminal >/dev/null; then TERM_CMD="gnome-terminal -- $L"
    else TERM_CMD="x-terminal-emulator -e $L"; fi
    F="$DESK/novo-carrossel.desktop"
    sed -e "s#@EXEC@#$TERM_CMD#" -e "s#@ICON@#$HERE/launchers/icone.png#" "$HERE/launchers/novo-carrossel.desktop.in" > "$F"
    chmod +x "$F"; command -v gio >/dev/null && gio set "$F" metadata::trusted true 2>/dev/null || true ;;
esac
echo "atalho criado: $F"
