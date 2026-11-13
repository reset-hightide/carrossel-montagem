---
name: carrossel-montagem
description: Cria carrosséis de Instagram nível agência para qualquer marca (cliente), com montagem/colagem editorial, dados e narrativa, sempre na identidade visual da marca. Começa com um QUESTIONÁRIO guiado (marca, identidade visual, campanha, produtos, referência de estilo, entrega), monta um time de agentes (estrategista de emoção e desejo, revisor ex-Meta, designer, diretor de criação, cliente simulado), refina a linguagem no ChatGPT, gera .pptx editável no backend e importa no Canva (fotos soltas e em Uploads), com arquivo separado de capas. Use quando pedirem carrossel, post de campanha (Black Friday, lançamento, data comemorativa), "post para cliente", "/carrossel-montagem" ou "/post".
---

# Carrossel montagem

Objetivo: carrossel no nível de uma agência premium. A **gramática visual** (montagem/colagem) vem da referência de estilo;
**fontes, logos e cores vêm SEMPRE da marca do cliente**. Nada de dado inventado: todo número tem fonte e data.

Python das ferramentas: `~/.venvs/post/bin/python` (Windows: `~/.venvs/post/Scripts/python.exe`). Scripts em `scripts/`
desta skill. Se o venv não existir, rode o `install.sh`/`install.ps1` do repositório.

## 0. Questionário (sempre primeiro, UMA pergunta por vez)

Cumprimente em 1 linha e verifique se há perfil salvo em `~/.claude/carrossel-marcas/` (e na memória). Se a marca já
tem perfil, mostre o resumo em 3 linhas e pergunte só o que mudou.

**Formato: entrevista.** Faça UMA pergunta por mensagem, espere a resposta, registre na hora e só então faça a próxima.
Nunca mande a lista inteira de uma vez. Cada pergunta: curta, numerada ("3/12"), com o padrão entre parênteses
("Enter/ok = padrão"). Perguntas de escolha fechada vão por AskUserQuestion (1 pergunta por chamada); as abertas, em
texto. Depois de cada resposta: confirme em meia linha o que anotou, grave no `BRIEFING.md` (crie a pasta do projeto
assim que souber marca + campanha) e pule as perguntas que a resposta já cobriu ou que dá para descobrir sozinho
(site, @, cores). Se o usuário disser "o resto padrão", assuma os padrões e siga.

Ordem (texto livre, salvo indicação):
1. Qual é a marca? (nome; se já tiver perfil, só confirmar)
2. @ do Instagram e site (se não souber, eu procuro)
3. Identidade visual: tem Drive, brandbook, Brand Kit do Canva ou logo/fontes? (padrão: extraio do site e do Instagram)
4. Tema da campanha
5. Objetivo — AskUserQuestion: vender (padrão) | educar | autoridade | lançamento
6. Link da página da campanha/produtos
7. Quais produtos destacar? (padrão: escolho os melhores)
8. Regras: prazo da campanha, entrega, parcelamento, o que não pode prometer
9. Público: quem compra e o que desperta desejo nele
10. Referência de estilo: link de post que você ama (padrão: colagem editorial)
11. Formato — AskUserQuestion: 10 slides + 10 capas (padrão) | 7 slides + 5 capas | outro
12. Preços no post — AskUserQuestion: de/por com data nas notas (padrão) | só % | sem preço
13. Fotos — AskUserQuestion: oficiais do site/fabricante (padrão) | banco da marca | edição/upscale realista no ChatGPT
14. Entrega — AskUserQuestion: PPTX → Canva + Uploads (padrão) | só PPTX. Se o cliente mandou roteiro, perguntar também se quer a versão "FIEL" (roteiro 100%, só ortografia) além da "FINAL" (melhor post possível) e das capas
15. Revisão de linguagem no ChatGPT — AskUserQuestion: sim (padrão) | não
16. Onde aviso quando terminar (padrão: WhatsApp "Lembrete") e quem aprova (cliente real?)

No fim, mostre o briefing completo em até 10 linhas e pergunte "posso começar?".
Salve/atualize o perfil da marca em `~/.claude/carrossel-marcas/<marca>.md` (site, @, onde está a identidade,
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
1. **Estrategista** (emoção + desejo + razão): `references/prompt-agente-estrategista.md`. Para TODO texto, seguir a skill `copywriting-ptbr` (`~/.claude/skills/copywriting-ptbr/`): localizar, não traduzir; roteiro do cliente se preserva, mudança só com ANTES → DEPOIS. Formato e gancho pelo `references/instagram-playbook.md`. Pesquisa de mercado com fonte,
   análise de ofertas com contas, fotos certas do modelo certo, roteiro, capas, legenda, revisão de linguagem no ChatGPT.
2. **Revisor ex-Meta** (antes do design): `references/meta-boas-praticas.md` + `references/instagram-playbook.md` (algoritmo, formatos C1–C4, legenda, hashtags BR, humanizador pt-BR). Capa ≤ 8 palavras, slide 2 como 2ª capa,
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
- [ ] Sombras suaves (`scripts/colagem.py checar design/assets` sem "CORTE SECO") e sublinhados/blocos como destaque agrupado de 1 linha (`"sub"`/`"bloco"` no spec), conferidos no Canva.
- [ ] Pré-entrega do `references/instagram-playbook.md` (seção 9) e humanizador pt-BR (seção 6).

## 5. Build e Canva
- `scripts/build_pptx.py spec.json out.pptx` → `scripts/optimize_pptx.py out.pptx "<nome> (canva).pptx" --max 1600` (< 10 MB).
- Fontes no spec pelo NOME DA FAMÍLIA + bold (o Canva ignora peso no nome: "Poppins Black" vira Poppins fino).
- ANTES do build: confirmar no seletor de fontes do Canva que cada família existe (ex.: "DM Serif Text" não é nativa → vira Arimo). Se faltar: seletor de fontes > "Faça upload de uma fonte" com o .ttf (licença livre/da marca), e, depois do import (que cai em Arimo), selecionar um texto em Arimo > escolher a fonte carregada > "Alterar tudo" > "Todas as páginas". Depois do import, clicar num título e conferir o nome da fonte na barra.
- Canva (Chrome): na home, JS hook para o seletor nativo não abrir:
  `HTMLInputElement.prototype.click` → se `type=file`, anexa o input ao body e retorna. Criar > "Fazer upload" (scroll_to + click)
  > `find` "input type=file" > `file_upload`. A aba vai para /design/<ID>/edit.
- Fotos e recortes em Uploads: o editor roda num iframe same-origin de tela cheia (o hook não pega). Criar um `<input type=file multiple>` no documento de cima, `file_upload` nele (lotes < 9 MB), recriar cada File no realm do iframe (`new w.File([await f.arrayBuffer()], f.name, {type})`) e disparar dragenter/dragover/drop num ancestral do botão "Fazer upload de arquivos" dentro do iframe. Nunca digitar com o canvas focado (letras = atalhos).
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
