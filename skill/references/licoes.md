# Lições de uso (acrescente a cada post, com data)

## Visual
- Repetir o mesmo fundo/faixa em todos os slides foi rejeitado. Variar o tipo de visual em cada slide e seguir a identidade da marca.
- Números pouco claros e post que "acaba do nada" foram rejeitados: dado sempre com pergunta, explicação e conclusão; fechar com resumo + CTA.
- NÃO usar "ARRASTA →" na capa nem no slide 2: fica padronizado demais. O gancho vem do texto.
- O Canva importa PPTX mapeando FAMÍLIA + negrito: "Poppins Black" vira Poppins fino. Usar "Poppins" com bold=true.
  Fontes que não existem no Canva (ex.: serifadas exclusivas de logo) só entram como PNG do logo.
- Recorte com rembg sozinho "come" peças cromadas/brancas em foto de catálogo; usar o modo híbrido do cutout.py.

## Conteúdo e conformidade
- O cliente simulado pegou riscos reais: histórico de preço que expõe promoção anterior mais barata, preço "de" inflado
  (risco Procon), promessa de prazo incompatível com a entrega, comparação que desvaloriza o próprio público. Rodar SEMPRE.
- Payback longo desanima: preferir "custo por uso com o produto incluso" e deixar o prazo de retorno nas notas.
- Foto de ambiente não pode mostrar plaqueta/modelo de produto que não está na promoção quando o texto fala de preço.
- Conferir preços AO VIVO no site antes de entregar e pôr aviso "sujeitos a alteração" no último slide e na legenda.
- O ChatGPT exagera causalidade e às vezes troca números: conferir número a número depois de cada revisão de linguagem.

## Ferramentas
- Instagram devolve 429 depois de ~700 requisições de /p/; ir devagar (1 req/2 s).
- Imagens de lojas Tray/Fbits: `fbitsstatic.net/img/p/<slug>/<id>-N.jpg` sem `?w=` vêm no tamanho original.
- Fabricantes costumam ter fotos oficiais maiores que o varejista (ex.: CDN do fabricante sem parâmetros de resize).
- Screenshot do editor do Canva trava (timeout); conferir pelo export (conector Canva) ou abrir o design numa aba nova.
- Limite de 5 hashtags por post no Instagram (desde dez/2025).
- Versões: congelar a versão antes de cada rodada de feedback (o designer sobrescreve out/).
- (13/11/2026) preview.py quebra linha a cada run: parágrafo com negrito no meio sai errado no preview.
  Usar 1 run por parágrafo (negrito vira parágrafo próprio). Fonte variável (Libre Franklin) e arquivo "-Regular"
  (DM Serif Text) precisam de wrapper: ver <projeto>/design/render.py (também corrige imagem girada fora do centro).
- (13/11/2026) Sublinhado/bloco de destaque: gerar o spec por script que mede o texto com a fonte real e quebra linhas
  explícitas (1 parágrafo por linha); assim o rect cai no lugar certo também no Canva.

## 13/11/2026 — marca de orgânicos (Orgânico x Convencional)
- Questionário UMA pergunta por vez (pedido do usuário). Ele prefere responder em texto; popups de escolha às vezes viram "quero esclarecer".
- Roteiro do cliente → entregar 2 versões: FIEL (só ortografia, com lista do que corrigiu) e FINAL (melhor post, antes→depois). Manter nº de cartelas pedido.
- Fotos de Drive compartilhado (não público, gdown 401): ver miniaturas no Chrome (zoom 0.3 + overlay com thumbs), escolher, montar UM .zip no próprio navegador (zip "store" em JS a partir das thumbs =w2400) → 1 download só. Fetch para localhost trava (Chrome pede permissão de rede local) e vários downloads pedem permissão: evitar. Download do Chrome Flatpak cai no ~/Desktop.
- Canva: NÃO tinha "DM Serif Text" (vira Arimo). A conta permite "Faça upload de uma fonte" (seletor de fontes > fim da lista; confirmar declaração de direito — fontes OFL ok). Subir o .ttf ANTES de importar o pptx: o import mapeia pelo nome da família.
- Canva editor roda num iframe same-origin de tela cheia: hook de input/file não pega. Para Uploads: criar <input type=file> no documento de cima, file_upload nele, recriar os File no realm do iframe (new w.File([buf], nome, {type})) e disparar dragenter/dragover/drop no painel de Uploads do iframe. File de outro realm = "arquivo incompatível".
- Nunca digitar com o canvas focado: letras viram atalhos (R = retângulo). Focar a busca de fontes antes de digitar.
- Revisor Meta pegou citação legal errada (Lei 10.831 não fala de agrotóxico; é Decreto 6.323/2007 + Portaria MAPA 52/2021). Sempre conferir a lei citada no texto.
- Foto de cliente com placa de carro legível: tirar (LGPD/imagem). Diretor e cliente simulado pegaram.
- Import de pptx NÃO usa fonte carregada (cai em Arimo mesmo com o nome certo). Correção: abrir o design, clicar num texto em Arimo, escolher a fonte carregada no seletor → aparece "Alterar tudo: Arimo → X" → "Todas as páginas". Funciona porque as fontes nativas (ex.: Libre Franklin) mapeiam certo e só as que faltam viram Arimo.
- Feedback do usuário (13/11): sublinhados fora do lugar e sombras com "corte seco" em cima/embaixo.
  Causas: (1) traço = retângulo solto medido com a fonte local; no Canva a quebra/medida muda. (2) sombra.png quadrada
  esticada até o tamanho da foto; cartões com margem menor que deslocamento+3σ do desfoque; cutout.py usava
  ImageChops.offset (dá a volta: a sombra de baixo aparecia no topo) e margem 3×contorno.
  Correções na skill: build_pptx/preview com "sub"/"bloco" (caixa de 1 linha, medida com a fonte real e agrupada),
  scripts/colagem.py (sombra no tamanho certo, cartão com margem, `checar` bordas), cutout.py com margem 7× e sem wrap,
  preview acha fontes via fontconfig e aplica peso em fonte variável.
