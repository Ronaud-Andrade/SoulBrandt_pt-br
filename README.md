# Demon's Souls PT-BR como mod do Soulbrandt

Instala a **tradução PT-BR de Demon's Souls feita por Fábio – [StarKillerChief](https://github.com/StarKillerChief/demons-souls-pt-br)** como um **mod da pasta `mods` do [Soulbrandt](https://github.com/JonathanDC64/Soulbrandt) 0.2.0** (o port de PC de Demon's Souls), com **um clique**.

- **A tradução não some mais quando o Soulbrandt atualiza.**
- **Não precisa instalar a tradução antes**, nem Python, nem nada: o `.bat` baixa o pacote da tradução e faz tudo.
- Você liga ou desliga a tradução no menu **Mods** do jogo, e o online continua funcionando.

> **Este repositório não tem nenhum arquivo do jogo nem o texto da tradução.** A tradução é gerada no seu PC, a partir da **sua própria cópia** do jogo, com as ferramentas e os textos do pacote oficial do StarKillerChief.

---

## Como instalar

**Você precisa de:** Windows 10 ou 11 e o **Soulbrandt 0.2.0 ou mais novo** com o jogo já preparado (abra ele uma vez e deixe preparar até o fim). Versão americana do jogo, **BLUS30443**, a única que a tradução suporta.

1. **Baixe este repositório:** botão verde **Code > Download ZIP**.
2. **Extraia** a pasta onde quiser. O mais fácil é dentro da pasta do `Soulbrandt.exe`.
3. **Feche o Soulbrandt** e dê dois cliques em **`1 - Instalar traducao PT-BR.bat`**.
4. Responda as duas perguntas:
   - **Fonte:** `1` para as **Fontes HD** (recomendado) ou `2` para as **fontes originais** do jogo.
   - **Legendas dos vídeos:** `S` ou `N`.
5. Espere aparecer **"Pronto"** (leva até 1 minuto). Abra o Soulbrandt e vá em **Mods**: o **PT-BR** aparece ligado, no topo da lista.

É só isso. Nas próximas atualizações do Soulbrandt a tradução continua lá.

> Se o Windows mostrar "O Windows protegeu o computador", clique em **Mais informações > Executar assim mesmo**.

### O que o `.bat` faz

1. Procura a pasta `PT-BR` do pacote da tradução (dentro desta pasta ou ao lado do `Soulbrandt.exe`). Se não achar, **baixa o `PT-BR-Soulbrandt.zip` mais recente** da [página de Releases do StarKillerChief](https://github.com/StarKillerChief/demons-souls-pt-br/releases) e extrai aqui. O pacote já traz o Python que o script usa.
2. Acha o jogo que o Soulbrandt usa (pela preparação dele, em `setup\ready.txt`) e **copia só os arquivos que a tradução troca** para uma pasta temporária. O jogo original não é alterado.
3. Roda as **ferramentas da própria tradução** nessa pasta temporária: fontes com acentos, textos, letreiros (VOCÊ MORREU, DEMÔNIO DESTRUÍDO…), telas de carregamento e a caixa do nome da área.
4. Confere o SHA-256 de cada arquivo gerado e monta o mod em `mods\PT-BR\PS3_GAME\USRDIR\`, com a linha `on PT-BR` no topo do `mods\load_order.txt`.
5. Se você pediu, gera as legendas dos vídeos e liga a DLL delas (veja abaixo).

### Onde o mod fica

O script acha a pasta `mods` do mesmo jeito que o Soulbrandt acha a pasta de dados:

| Instalação | Pasta `mods` |
|---|---|
| Portátil (`portable.txt` ao lado do programa) | `data\mods` ao lado do `Soulbrandt.exe` |
| Vinda de uma versão antiga (0.1.x) | `%APPDATA%\DemonsSoulsRecomp\DemonsSouls\mods` |
| Nova (0.2.0 em diante) | `%LOCALAPPDATA%\Soulbrandt\mods` |

Use **`Ver estado.bat`** para ver o que foi encontrado.

## Por que um mod

O instalador original da tradução monta uma cópia traduzida do jogo (`ptbr-game`) e aponta o Soulbrandt para ela. **Cada atualização do Soulbrandt aponta de volta para o jogo original**, e a tradução some. O Soulbrandt 0.2.0 trouxe a **pasta `mods`**: cada mod substitui arquivos do jogo sem mexer no original, e as atualizações não tocam nela.

| | Instalador original | Este mod |
|---|---|---|
| Atualização do Soulbrandt | apaga a tradução | a tradução continua |
| Precisa instalar a tradução antes | – | não |
| Ligar/desligar | rodar o instalador | menu **Mods** do jogo |
| Jogo online | funciona | funciona (mod só visual: texto, fontes e menus) |
| Legendas dos vídeos | sim | sim, mas religar depois de cada atualização |

## Trocar a fonte

Rode o `1 - Instalar traducao PT-BR.bat` de novo e escolha a outra fonte. O mod é refeito do zero.

## Legendas dos vídeos

As legendas dos vídeos **não podem ir para a pasta `mods`**. Elas funcionam com uma DLL da tradução (`avcodec-62.dll`) que fica ao lado do `Soulbrandt.exe`, repassa o vídeo para a DLL oficial e desenha as legendas por cima. O sistema de mods só troca arquivos do jogo, não DLLs do programa. E **cada atualização do Soulbrandt coloca o `avcodec-62.dll` oficial de volta**.

- **`2 - Ligar legendas dos videos.bat`**: guarda a DLL oficial como `avcodec-62.orig.dll` e coloca a das legendas no lugar. **Rode depois de cada atualização do Soulbrandt.**
- **`3 - Desligar legendas dos videos.bat`**: volta a DLL oficial.

Se os vídeos ficarem com tela preta ou travarem na abertura, use o `3`.

## Voltar ao inglês

Desligue o **PT-BR** no menu **Mods** (ou apague a pasta `mods\PT-BR`) e rode o `3 - Desligar legendas dos videos.bat`. O jogo original nunca foi alterado.

## Atualizar a tradução

Quando sair uma versão nova da tradução do StarKillerChief, apague a pasta `PT-BR` que o `.bat` baixou e rode o `1 - Instalar traducao PT-BR.bat` de novo: ele baixa a versão mais recente.

Se a própria tradução passar a se instalar na pasta `mods` do Soulbrandt (isso foi discutido na [issue #404 do Soulbrandt](https://github.com/JonathanDC64/Soulbrandt/issues/404)), **prefira a versão oficial** e apague este mod.

## Para quem quer mais controle

Tudo é feito pelo `converter_ptbr_mod.py` (`--help` mostra tudo). Rode com o Python da pasta `PT-BR`:

```
PT-BR\python\python.exe converter_ptbr_mod.py instalar --fontes original --legendas
PT-BR\python\python.exe converter_ptbr_mod.py instalar --fontes original --so-fontes --nome "PT-BR Fontes originais"
PT-BR\python\python.exe converter_ptbr_mod.py mod      (monta o mod a partir da tradução já instalada pelo instalador dela)
```

O segundo exemplo cria um mod só com as 4 fontes, no topo da lista: ligado, ele troca a fonte do `PT-BR` sem precisar refazer nada. Outras opções: `--program`, `--setup`, `--jogo`, `--mods`, `--pacote`.

## Perguntas

**Posso compartilhar a pasta do mod pronta?**
Não. Ela contém arquivos gerados a partir da sua cópia do jogo. Compartilhe só este repositório: cada pessoa gera o mod no próprio PC.

**Funciona no RPCS3?**
Não precisa: no RPCS3 use o instalador original da tradução, que troca os arquivos direto no jogo. O RPCS3 não tem as atualizações que apagam a tradução.

**Eu já tinha instalado a tradução pelo instalador original. E agora?**
Pode rodar o `1 - Instalar traducao PT-BR.bat` normalmente. Se o jogo ainda estiver apontando para a cópia traduzida (`ptbr-game`), o script usa os arquivos originais que o instalador guardou. Para deixar tudo limpo, clique antes em **Desinstalar** no `Tradução PT-BR.exe` e depois rode o `1 - Instalar traducao PT-BR.bat` (o desinstalador dela também apaga as legendas dos vídeos).

**Precisa de internet?**
Só na primeira vez, para o `.bat` baixar o pacote da tradução (uns 18 MB) do GitHub do StarKillerChief. Se a pasta `PT-BR` já estiver ao lado, nada é baixado.

**E a versão europeia (BLES00932)?**
A tradução original ainda não suporta, então este mod também não.

**O que continua em inglês?**
O mesmo que na tradução original: o launcher do Soulbrandt e os menus do próprio port (F1), que estão dentro do `Soulbrandt.exe`.

## Créditos

- **Tradução PT-BR, fontes com acentos, letreiros, telas de carregamento, legendas dos vídeos e o instalador:** Fábio – **[StarKillerChief](https://github.com/StarKillerChief)**, no projeto [demons-souls-pt-br](https://github.com/StarKillerChief/demons-souls-pt-br). Todo o trabalho de tradução é dele; este repositório só muda a forma de instalar. As ferramentas dele são MIT, e o texto é uma tradução de fãs, gratuita e sem fins lucrativos (veja o `NOTICE.md` do projeto dele).
- **Soulbrandt**, o port de PC de Demon's Souls, e o sistema de mods: **[JonathanDC64](https://github.com/JonathanDC64)** e colaboradores, em [Soulbrandt](https://github.com/JonathanDC64/Soulbrandt), feito sobre o [ps3recomp](https://github.com/sp00nznet/ps3recomp) de sp00nznet.
- **Fontes usadas pela tradução original** (geradas no seu PC pelo instalador dela, não incluídas aqui): TeX Gyre Schola (GUST Font License), na opção HD, e EB Garamond (SIL Open Font License), nas telas de carregamento.
- **Demon's Souls** é da FromSoftware, Sony Interactive Entertainment e Atlus.
- **Instalação como mod da pasta `mods`:** [Ronaud Andrade](https://github.com/Ronaud-Andrade).

## Licença e aviso

O código deste repositório (o script e os `.bat`) está sob a licença **MIT** (veja [`LICENSE`](LICENSE)).

Projeto de fã, sem fins lucrativos, sem vínculo com FromSoftware, Sony, Atlus, Bandai Namco, Bluepoint, o autor do Soulbrandt ou o autor da tradução. Nenhum arquivo do jogo é distribuído aqui. Se algum detentor de direitos pedir, o repositório sai do ar.
