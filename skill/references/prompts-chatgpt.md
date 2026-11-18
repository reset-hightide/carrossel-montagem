# Prompts para o ChatGPT (chatgpt.com, aba nova no Chrome)

## A. Linguagem natural (copy dos slides + legenda)
```
Você é redator de redes sociais brasileiro, especialista em [NICHO]. Vou colar o texto de um carrossel de Instagram
(10 slides) e a legenda da marca [MARCA] (@[ARROBA]). Reescreva para soar como alguém do ramo conversando com outro
apaixonado pelo assunto: frases curtas, palavras do dia a dia, ritmo de fala. Regras:
- NÃO mude nenhum número, preço, porcentagem, nome de produto ou data.
- NÃO invente fatos, prazos, brindes ou estoques.
- Sem clichê de varejo: nada de "imperdível", "corre", "aproveite já", "oportunidade única", "não fique de fora".
- Títulos: no máximo 8 palavras, com uma virada. Textos de apoio: no máximo 25 palavras.
- Mantenha a estrutura (Slide 1..10, kicker/título/texto) e devolva no mesmo formato.
- No fim, liste em tópicos o que você mudou e por quê.
[COLAR TEXTO]
```
Depois: comparar número por número com o original; aceitar só o que melhora.

## B. Edição de foto ultra-realista (quando a foto oficial não serve)
```
Edite esta foto mantendo o produto EXATAMENTE como está: mesmo modelo, proporções, logotipos, letras, botões,
manômetros, reflexos e textura do metal/aço inox. Mudança pedida: [ex.: trocar o fundo por uma bancada de madeira
escura numa cafeteria com luz quente lateral de fim de tarde / estender o fundo para formato 4:5].
Estilo: fotografia de produto real, lente 50mm, profundidade de campo natural, grão sutil, sem aspecto de render,
sem brilho artificial, sem objetos extras. A edição deve ser impossível de perceber.
```

## C. Upscale preservando realismo
```
Aumente a resolução desta foto para o máximo possível sem reinterpretar nada: mesmos detalhes, textos, logotipos,
reflexos e texturas, sem suavizar, sem plastificar, sem mudar cores. Apenas mais nitidez e definição real.
```
Conferir no zoom: logo e letras da peça iguais ao original? Se não, descartar e usar o original.
Baixar a imagem: o download do ChatGPT pode cair como `.com.google.Chrome.*` em ~/Downloads; renomear.

## D. Remoção de fundo (PADRÃO para TODO recorte — desde 18/11/2026)
O rembg/cutout.py sozinho não dá qualidade suficiente. Todo recorte (produto, pessoa, objeto) é feito no ChatGPT
com o prompt abaixo, colado SEM alterar. Fluxo:
1. Aba nova em chatgpt.com, conversa nova. Anexar a foto ORIGINAL na maior resolução disponível (nunca miniatura/print).
2. Colar o prompt e enviar. Uma foto por mensagem (várias na mesma conversa podem, uma de cada vez).
3. Baixar o PNG (o download pode cair como `.com.google.Chrome.*` em ~/Downloads; renomear para `<produto>_recorte.png`).
4. Conferir: `cutout.py <png> <saida>` tem que dizer "alfa real detectado". Se avisar "sem alfa real" (veio fundo
   branco ou quadriculado PINTADO), pedir de novo: "O arquivo veio sem transparência real. Exporte de novo em PNG com
   canal alfa verdadeiro, fundo 100% transparente." Olhar no zoom: produto idêntico ao original (logo, letras,
   cor, proporção), sem halo, sem parte comida. Se o ChatGPT redesenhou o produto, descartar e pedir de novo.
5. O `cutout.py` então só apara e gera o `_sticker.png` (contorno + sombra) a partir do recorte do ChatGPT.
Plano B (ChatGPT fora/limite): `cutout.py` com a foto original (rembg) e registrar em `design/pendencias_ia.md`.

```
**TAREFA: REMOÇÃO DE FUNDO COM PRESERVAÇÃO INTEGRAL DA IMAGEM ORIGINAL**

Remova exclusivamente o fundo da imagem fornecida, substituindo-o por transparência real (canal alfa). Esta é uma tarefa de recorte e isolamento, NÃO de recriação, restauração ou transformação da fotografia.

**1. PRESERVAÇÃO ABSOLUTA DO ORIGINAL**

- Preserve integralmente o sujeito ou objeto fotografado, sem modificar absolutamente nenhuma característica visual.
- Mantenha exatamente as mesmas proporções, dimensões, posição, perspectiva, geometria, expressão, cores, iluminação, sombras próprias, contraste e tonalidades.
- Preserve todas as texturas originais: poros da pele, fios de cabelo, tecidos, fibras, rugosidades, granulação fotográfica, reflexos e pequenas imperfeições naturais.
- Não reconstrua, redesenhe, substitua, invente ou interprete nenhuma parte da imagem.
- Não aplique filtros de beleza, suavização, retoque de pele, redução agressiva de ruído ou efeitos de inteligência artificial.

**2. RECORTE DE PRECISÃO PROFISSIONAL**

- Identifique os limites exatos do sujeito, preservando detalhes delicados como fios soltos de cabelo, pelos, transparências, bordas irregulares e elementos muito finos.
- Remova completamente o fundo, inclusive resíduos de cor, halos, contornos brancos, sombras projetadas exclusivamente no fundo e artefatos de recorte.
- Preserve transições naturais de transparência e antialiasing nas bordas, sem deixá-las serrilhadas, duras, desfocadas ou artificialmente suavizadas.
- Não elimine partes legítimas do sujeito, mesmo que sejam muito pequenas ou tenham cores semelhantes às do fundo.
- Preserve detalhes sem criar bordas falsas ou contornos artificiais.

**3. NITIDEZ E QUALIDADE FOTOGRÁFICA**

- Mantenha a máxima resolução e a máxima fidelidade possíveis em relação ao arquivo original.
- Preserve a nitidez óptica natural da fotografia, incluindo microtexturas e detalhes finos.
- Evite completamente aparência borrada, plastificada, encerada, excessivamente lisa ou artificialmente nítida.
- Não aplique sharpening excessivo, clareza artificial, HDR, super-resolução generativa ou reconstrução de detalhes.
- Preserve o grão fotográfico e as características naturais da captura.
- Caso seja necessário algum ajuste técnico, limite-o exclusivamente à máscara de transparência, sem modificar os pixels internos do sujeito.

**4. ENTREGA FINAL**

- Exporte em PNG de alta qualidade com fundo 100% transparente (canal alfa verdadeiro).
- Preserve as dimensões originais, sem cortes, reenquadramentos ou redimensionamentos.
- Não adicione fundo branco, preto, cinza, quadriculado ou qualquer outra cor.
- Não altere a composição original.
- Priorize fidelidade absoluta ao arquivo fornecido, mesmo que isso signifique não aplicar qualquer melhoria estética.

**REGRA FUNDAMENTAL:**

O resultado deve ser visualmente idêntico à fotografia original em todos os pixels pertencentes ao sujeito. A única diferença permitida é a remoção do fundo. Não gere uma nova versão da fotografia. Apenas isole o conteúdo original com um recorte preciso, natural e profissional.
```
