---
name: carrossel-montagem
description: Cria carrosséis de Instagram nível agência para qualquer marca (cliente), com montagem/colagem editorial, dados e narrativa, sempre na identidade visual da marca. Começa com um QUESTIONÁRIO guiado (marca, identidade visual, campanha, produtos, referência de estilo, entrega), monta um time de agentes (estrategista de emoção e desejo, revisor ex-Meta, designer, diretor de criação, cliente simulado), refina a linguagem no ChatGPT, gera .pptx editável no backend e importa no Canva (fotos soltas e em Uploads), com arquivo separado de capas. Use quando pedirem carrossel, post de campanha (Black Friday, lançamento, data comemorativa), "post para cliente", "/carrossel-montagem" ou "/post".
---

# Carrossel montagem

Objetivo: carrossel no nível de uma agência premium. A **gramática visual** (montagem/colagem) vem da referência de estilo;
**fontes, logos e cores vêm SEMPRE da marca do cliente**. Nada de dado inventado: todo número tem fonte e data.

Python das ferramentas: `~/.venvs/post/bin/python` (Windows: `~/.venvs/post/Scripts/python.exe`). Scripts em `scripts/`
desta skill. Se o venv não existir, rode o `install.sh`/`install.ps1` do repositório.

## 0. Questionário (sempre primeiro)

Cumprimente em 1 linha e verifique se há perfil salvo em `~/.claude/carrossel-marcas/` (lista as marcas já atendidas).
Se a marca já tem perfil, mostre o resumo e pergunte só o que mudou.

Peça os itens abaixo numa mensagem só (o usuário responde em texto livre; links e arquivos são bem-vindos). Depois use
AskUserQuestion (máx. 4 por rodada) para as escolhas que faltarem. O que tiver padrão, assuma e diga.

```
NOVO CARROSSEL — me manda o que tiver:
1. Marca: nome, @ do Instagram, site
2. Identidade visual (o melhor que tiver): pasta do Drive / brandbook PDF / Canva Brand Kit / arquivos de logo e fontes.
   Se não tiver nada, eu extraio do site e do Instagram.
3. Campanha: tema, objetivo (vender, educar, autoridade, lançamento), link da página da campanha/produtos
4. Produtos e regras: quais destacar (ou "escolhe os melhores"), prazo da campanha, entrega, parcelamento, o que não pode prometer
5. Público: quem compra e o que desperta desejo nele
6. Referência de estilo: link de post que você ama (padrão: colagem editorial)
7. Formato: nº de slides (padrão 10) + arquivo de capas (padrão 10 opções)
8. Avisar onde quando terminar (ex.: WhatsApp "Lembrete") e quem aprova (cliente real?)
```
Escolhas (AskUserQuestion), com padrões:
- Preços no post: de/por com data nas notas (padrão) | só % | sem preço
- Fotos: oficiais do site/fabricante (padrão) | banco da marca | edição/upscale realista no ChatGPT
- Entrega: PPTX → Canva + Uploads (padrão) | só PPTX
- Revisão de linguagem no ChatGPT: sim (padrão) | não

Ao fim, salve/atualize o perfil da marca em `~/.claude/carrossel-marcas/<marca>.md` (site, @, onde está a identidade,
fontes, paleta, logos, tom, regras, contatos de aprovação, histórico de posts com links do Canva).

## 1. Coleta (backend primeiro, navegador só se precisar)
- Pasta do projeto: `~/Posts/<marca>-<campanha>/` com `site/ brand/ fotos/ copy/ design/ out/` + `BRIEFING.md`
  (modelo em `references/briefing-modelo.md`).
- Site: `curl -sL -A "Mozilla/5.0 Chrome/130"` (o Chrome pode negar leitura de domínio sem permissão). Lojas Tray/Fbits:
  parser em `scripts/parse_fbits.py` (`?pagina=N`). Outras plataformas: procurar JSON-LD (`"@type":"Product"`, `"price"`).
- Identidade: Drive via `rclone` (se configurado) ou navegador; baixar só logos, fontes, paleta, fotos e brandbook
  (pular vídeos). Instalar fontes no sistema e montar um contact sheet das paletas/logos para OLHAR.
  Sem identidade formal: extrair cores do logo/site (hex), fontes do CSS do site, tom do Instagram.
- Instagram da marca: rolar o grid e anotar estilo (fotos reais? títulos sobre foto? destaques?). Use zoom na região.
- Referência de estilo: `references/estilo-referencia.md` (padrão) ou estudar o post enviado e escrever `design/estilo.md`.

## 2. Time de agentes (Agent, general-purpose; um de cada vez, passando arquivos)
1. **Estrategista** (emoção + desejo + razão): `references/prompt-agente-estrategista.md`. Pesquisa de mercado com fonte,
   análise de ofertas com contas, fotos certas do modelo certo, roteiro, capas, legenda, revisão de linguagem no ChatGPT.
2. **Revisor ex-Meta** (antes do design): `references/meta-boas-praticas.md`. Capa ≤ 8 palavras, slide 2 como 2ª capa,
   gatilhos de envio/salvamento, CTA único, ≤ 5 hashtags, alt text, marcação de produto/collab.
3. **Designer**: `references/prompt-agente-designer.md`. Gera `design/spec_carrossel.json` e `spec_capas.json`
   para `scripts/build_pptx.py`, recortes com `scripts/cutout.py`, revisa com `scripts/preview.py`.
4. **Congelar versão 1** (ver "Versões").
5. **Diretor de criação** (checklist da seção 4) **+ cliente simulado** (`references/prompt-cliente-simulado.md`), em paralelo.
6. **Rodada 2**: o mesmo designer (SendMessage) aplica os obrigatórios dos dois; você decide os conflitos.
Avise o usuário em 1 linha a cada etapa concluída.

## 3. ChatGPT (Chrome, usuário logado em chatgpt.com)
Sempre aba nova. Prompts em `references/prompts-chatgpt.md`: linguagem natural, edição de foto ultra-realista, upscale.
Conferir número a número depois. Nunca usar IA para inventar o produto: modelo e cor têm que bater com o site.

## 4. Checklist de qualidade
- [ ] Todo número confere com o site/fonte e tem data nas notas do slide.
- [ ] Foto de cada produto é do modelo, cor e versão certos.
- [ ] Variedade visual: nenhum slide com o mesmo layout do anterior.
- [ ] Fontes/cores/logo da marca; gramática da referência.
- [ ] Último slide = resumo + CTA; legenda com pergunta, "salva e manda" e fontes.
- [ ] Texto natural e enxuto (≤ ~30 palavras por slide interno). Sem "ARRASTA" na capa/slide 2.

## 5. Build e Canva
- `scripts/build_pptx.py spec.json out.pptx` → `scripts/optimize_pptx.py out.pptx "<nome> (canva).pptx" --max 1600` (< 10 MB).
- Fontes no spec pelo NOME DA FAMÍLIA + bold (o Canva ignora peso no nome: "Poppins Black" vira Poppins fino).
- Canva (Chrome): na home, JS hook para o seletor nativo não abrir:
  `HTMLInputElement.prototype.click` → se `type=file`, anexa o input ao body e retorna. Criar > "Fazer upload" (scroll_to + click)
  > `find` "input type=file" > `file_upload`. A aba vai para /design/<ID>/edit.
- Fotos e recortes em Uploads: no editor, aba Uploads > file-input > `file_upload` em lotes < 9 MB (refazer o find a cada lote).
- Nomes: "<Marca> <Campanha> - FINAL - Carrossel" / "- FINAL - Capas" / "- V1 antes do cliente - …".
- Edições pequenas depois (texto, foto, título): conector Canva (`read-design` com transaction → `edit-design` → commit
  só depois de mostrar o preview, ou quando o pedido do usuário já é exatamente aquela mudança).
- Conferência visual: `export-design` (jpg, width 540) e olhar; screenshot do editor costuma travar.

## 6. Conferência legal (obrigatória antes de entregar)
1. Preços AO VIVO: baixar a página de cada produto e comparar com cada número em slides, capas e legenda; refazer somas.
2. Aviso no último slide e na legenda: "Preços à vista do site, sujeitos a alteração e ao estoque. Valem os preços do site na compra."
3. Fotos: sheet lado a lado "post x galeria oficial" por produto. Foto de ambiente não pode mostrar modelo/plaqueta de produto
   fora da promoção quando o texto fala de preço. Registrar em `design/conferencia_legal_<data>.md`.

## Versões (obrigatório)
Antes de cada rodada de feedback, congelar em `<projeto>/versao-N-<descricao>/` (copy/, design/ com geradores, specs e
CÓPIA dos assets, out/ com pptx, previews e o feedback). No Canva, manter "V1 antes do cliente" e "FINAL".

## Regras fixas
- Sem "ARRASTA →"/"deslize" na capa e no slide 2.
- Não citar IA/Claude nos materiais do cliente.
- Mensagens para terceiros (cliente, WhatsApp) só com pedido explícito do usuário.

## 7. Entrega e melhoria contínua
Resumo final: links do Canva (FINAL e V1), pasta local, legenda pronta, pendências para o cliente real.
Acrescente em `references/licoes.md` o que deu certo/errado (com data) e atualize o perfil da marca.
Pergunte uma nota de 0 a 10 e o que faltou para 10.
