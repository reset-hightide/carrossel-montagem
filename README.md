# carrossel-montagem

Skill para o [Claude Code](https://docs.claude.com/en/docs/claude-code) que produz carrosséis de Instagram para clientes,
do briefing ao design editável no Canva.

Você digita `/post` (ou clica no atalho da área de trabalho), responde uma entrevista curta, uma pergunta por vez, sobre a marca e a campanha,
e o fluxo faz o resto:

1. **Coleta**: site, produtos e preços, identidade visual (brandbook, pasta do Drive, Canva Brand Kit ou, na falta,
   o próprio site e o Instagram da marca).
2. **Estratégia e texto**: pesquisa de campanhas que funcionaram, escolha dos produtos, contas de economia,
   roteiro dos slides, capas alternativas e legenda. A linguagem passa por uma revisão no ChatGPT.
3. **Boas práticas do Instagram**: capa curta, segundo slide como "segunda capa", gatilhos de salvar/enviar,
   CTA único, até 5 hashtags, texto alternativo.
4. **Design**: montagem editorial (colagem, recortes, números grandes, blocos de destaque) com as fontes, cores e logo
   da marca. Gera um `.pptx` com cada foto e texto em camada separada.
5. **Revisão**: diretor de criação + uma reunião simulada com o cliente, depois uma rodada de ajustes.
6. **Conferência legal**: preços conferidos no site na hora, fotos comparadas com a galeria oficial de cada produto,
   aviso de "preços sujeitos a alteração".
7. **Canva**: importa o `.pptx` (vira design editável), sobe as fotos em Uploads e guarda a versão anterior ao feedback.

Junto vem a skill `copywriting-ptbr` (em `extras/`), que o instalador também coloca: copywriting **localizado** para o
português do Brasil (não traduzido) a partir de [boraoztunc/skills](https://github.com/boraoztunc/skills), com CDC,
CONAR e cuidados com alegação de saúde. O `skill/references/instagram-playbook.md` é uma localização das skills de
[sergebulaev/instagram-skills](https://github.com/sergebulaev/instagram-skills) (MIT).

Ferramentas de colagem: `build_pptx.py` faz sublinhado e bloco de destaque agrupados com o texto e medidos com a fonte
real (não escorregam no Canva). `colagem.py` gera sombras suaves no tamanho certo de cada foto e tem `checar`, que
aponta PNG com sombra cortada na borda.

Cada marca atendida ganha um perfil em `~/.claude/carrossel-marcas/`, então o próximo post da mesma marca pede bem menos informação.

## Requisitos

- Claude Code instalado e logado (`claude` no terminal).
- Python 3.10+.
- Para a parte de navegador (Canva, ChatGPT, Instagram, WhatsApp): Google Chrome com a extensão Claude in Chrome,
  logado nesses serviços. Sem ela, a skill entrega os `.pptx` e as fotos para você subir no Canva.
- Opcional: `rclone` configurado com o Google Drive, para baixar a pasta de identidade visual direto.

## Instalação

Linux, macOS ou Steam Deck:

```bash
git clone https://github.com/reset-hightide/carrossel-montagem.git
cd carrossel-montagem
bash install.sh
```

Windows (PowerShell):

```powershell
git clone https://github.com/reset-hightide/carrossel-montagem.git
cd carrossel-montagem
powershell -ExecutionPolicy Bypass -File install.ps1
```

O instalador:

- copia a skill para `~/.claude/skills/carrossel-montagem` e cria o comando `/post`;
- cria um ambiente Python em `~/.venvs/post` com python-pptx, Pillow, rembg e scipy;
- põe um atalho **Novo carrossel** na área de trabalho, que abre o terminal já com `claude --chrome "/post"`.

Opções do `install.sh` (ex.: `bash install.sh --link`): `--link` (usa link simbólico para o repositório, bom para quem vai editar a skill) e
`--no-shortcut`.

## Uso

Clique em **Novo carrossel** ou, dentro do Claude Code, digite:

```
/post
/post Black Friday da loja X, foco em cafeteiras
```

Os projetos ficam em `~/Posts/<marca>-<campanha>/`:

```
BRIEFING.md       resumo do pedido e da identidade
site/ brand/      dados do site e arquivos da marca
fotos/            fotos oficiais dos produtos
copy/             pesquisa, contas, roteiro, capas, legenda
design/           specs, geradores, assets, revisões e conferência legal
out/              .pptx finais e previews
versao-1-.../     versão congelada antes do feedback do cliente
```

## Scripts

Ficam em `skill/scripts/` e podem ser usados sozinhos:

| Script | O que faz |
|---|---|
| `build_pptx.py spec.json saida.pptx` | monta o `.pptx` a partir de um JSON (imagens, retângulos, textos, linhas) |
| `preview.py spec.json pasta/` | renderiza PNGs e um contact sheet para revisar, avisando texto que estoura |
| `cutout.py foto.jpg saida` | recorta o produto (rembg + preenchimento do fundo) e gera a versão "sticker" |
| `optimize_pptx.py in.pptx out.pptx --max 1600` | reduz o `.pptx` para menos de 10 MB sem perda visível |
| `parse_fbits.py pagina.html ...` | extrai produtos e preços de lojas Tray/Fbits |

## Personalizar

- `skill/references/estilo-referencia.md`: a gramática visual padrão. Troque pela do seu estúdio.
- `skill/references/licoes.md`: aprendizados acumulados; a skill acrescenta novos a cada post.
- `skill/references/prompt-*.md`: os papéis do time (estrategista, designer, cliente simulado).

## Licença

MIT
