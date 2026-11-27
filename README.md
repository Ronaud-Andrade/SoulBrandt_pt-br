# Demon's Souls PT-BR como mod do Soulbrandt

Um conversor que transforma a **tradução PT-BR de Demon's Souls feita pelo [StarKillerChief](https://github.com/StarKillerChief/demons-souls-pt-br)** em um **mod da pasta `mods` do [Soulbrandt](https://github.com/JonathanDC64/Soulbrandt) 0.2.0** (o port de PC de Demon's Souls).

Resultado: **a tradução não some mais quando o Soulbrandt atualiza**, e você liga ou desliga ela no menu **Mods** do jogo.

> **Este repositório não tem nenhum arquivo do jogo nem o texto da tradução.** Ele só tem um script que, no seu PC, copia os arquivos que o instalador da tradução já gerou a partir da **sua própria cópia** do jogo. Você precisa ter o jogo e a tradução original.

---

## Por que isso existe

O instalador da tradução (versão 0.1.2) funciona assim: ele monta uma cópia traduzida do jogo numa pasta própria (`ptbr-game`) e aponta o Soulbrandt para ela. Só que **cada atualização do Soulbrandt aponta de volta para o jogo original**, e a tradução some até você instalar de novo.

O Soulbrandt 0.2.0 trouxe uma **pasta `mods`**: cada mod é uma pasta que substitui arquivos do jogo sem mexer no original, e as atualizações não tocam nela. Este conversor pega os arquivos traduzidos e monta um mod com eles.

| | Instalador original | Este mod |
|---|---|---|
| Atualização do Soulbrandt | apaga a tradução | a tradução continua |
| Ligar/desligar | rodar o instalador | menu **Mods** do jogo |
| Jogo online | funciona | funciona (mod só visual: texto, fontes e menus) |
| Legendas dos vídeos | sim | à parte (veja abaixo) |

## O que você precisa

- **Soulbrandt 0.2.0 ou mais novo**, com o jogo já preparado (versão americana **BLUS30443**, a única que a tradução suporta).
- A **tradução PT-BR do StarKillerChief** ([Releases](https://github.com/StarKillerChief/demons-souls-pt-br/releases)), instalada **pelo menos uma vez** com o `Tradução PT-BR.exe`.
- Windows 10 ou 11. Não precisa instalar Python: o script usa o Python que já vem dentro da pasta `PT-BR` da tradução.

## Como usar

1. **Instale a tradução original uma vez**, como manda o LEIA-ME dela: extraia o `PT-BR-Soulbrandt.zip` dentro da pasta do `Soulbrandt.exe`, abra `PT-BR\Tradução PT-BR.exe`, escolha a fonte e clique em **Instalar tradução**. Feche.
2. **Baixe este repositório** (botão verde **Code > Download ZIP**) e extraia a pasta **dentro da pasta do `Soulbrandt.exe`**, ao lado da pasta `PT-BR`. Fica assim:
   ```
   Soulbrandt\
   ├── Soulbrandt.exe
   ├── PT-BR\                 (a tradução original)
   └── PT-BR-Mod\             (este repositório)
       ├── 1 - Criar mod PT-BR.bat
       ├── 2 - Ligar legendas dos videos.bat
       └── ...
   ```
3. Com o jogo **fechado**, dê dois cliques em **`1 - Criar mod PT-BR.bat`**.
4. Abra o Soulbrandt e vá em **Mods** (no menu ou na tela inicial): o **PT-BR** aparece ligado, no topo da lista.

Pronto. Daqui pra frente, as atualizações do Soulbrandt não apagam a tradução.

> Depois de criar o mod, **não precisa mais rodar o "Instalar tradução"**. Se rodar, não quebra nada (os arquivos são os mesmos), mas a tradução fica aplicada por dois caminhos.

### Onde o mod fica

O script acha a pasta `mods` do mesmo jeito que o Soulbrandt acha a pasta de dados:

| Instalação | Pasta `mods` |
|---|---|
| Portátil (`portable.txt` ao lado do programa) | `data\mods` ao lado do `Soulbrandt.exe` |
| Vinda de uma versão antiga (0.1.x) | `%APPDATA%\DemonsSoulsRecomp\DemonsSouls\mods` |
| Nova (0.2.0 em diante) | `%LOCALAPPDATA%\Soulbrandt\mods` |

O mod fica em `mods\PT-BR\PS3_GAME\USRDIR\...`, e o script põe a linha `on PT-BR` no topo do `mods\load_order.txt` (a primeira linha ganha quando dois mods mexem no mesmo arquivo). Use **`Ver estado.bat`** para ver o que foi encontrado.

## Fontes: originais ou HD

O mod sai com a fonte que estava instalada quando você rodou o script (originais ou HD). Para ter **as duas** e trocar pelo menu **Mods**:

1. No `Tradução PT-BR.exe`, clique em **Trocar fonte** e escolha a outra.
2. Rode no Prompt de Comando, dentro da pasta `PT-BR-Mod`:
   ```
   ..\PT-BR\python\python.exe converter_ptbr_mod.py mod --so-fontes --nome "PT-BR Fontes originais"
   ```
   (troque o nome para `"PT-BR Fontes HD"` se a fonte trocada for a HD).
3. Esse mod de fontes vai para o topo da lista. Ligado, ele vence o `PT-BR`; desligado, vale a fonte do `PT-BR`.

## Legendas dos vídeos

As legendas dos vídeos **não podem ir para a pasta `mods`**. Na tradução original elas funcionam com uma DLL própria (`avcodec-62.dll`) que fica ao lado do `Soulbrandt.exe`, repassa o vídeo para a DLL oficial e desenha as legendas por cima. O sistema de mods só troca arquivos do jogo, não DLLs do programa.

E cada atualização do Soulbrandt coloca o `avcodec-62.dll` oficial de volta. Para religar:

- **`2 - Ligar legendas dos videos.bat`**: guarda a DLL oficial da versão atual como `avcodec-62.orig.dll` e coloca a das legendas no lugar. Rode de novo depois de cada atualização.
- **`3 - Desligar legendas dos videos.bat`**: volta a DLL oficial.

Se os vídeos ficarem com tela preta ou travarem na abertura, use o `3`.

## Voltar ao inglês

Desligue o **PT-BR** no menu **Mods** (ou apague a pasta `mods\PT-BR`) e rode o `3 - Desligar legendas dos videos.bat`. O jogo original nunca foi alterado.

## Atualizar a tradução

Quando sair uma versão nova da tradução do StarKillerChief: instale a nova com o `Tradução PT-BR.exe` e rode o `1 - Criar mod PT-BR.bat` de novo. O mod é refeito do zero.

Se a própria tradução passar a suportar a pasta `mods` do Soulbrandt (a mudança para a pasta `mods` foi discutida na [issue #404 do Soulbrandt](https://github.com/JonathanDC64/Soulbrandt/issues/404)), **prefira a versão oficial** e apague este mod.

## Como funciona (técnico)

- O instalador da tradução monta a pasta `<preparação do Soulbrandt>\ptbr-game` (normalmente `%LOCALAPPDATA%\DemonsSoulsRecomp\ptbr-game`), com cópias reais de `font`, `msg` e `menu`, e guarda em `PS3_GAME\USRDIR\.ptbr-backup\manifest.json` a lista dos arquivos que trocou, com o SHA-256 de cada um.
- O script lê esse manifesto, **confere o SHA-256 de cada arquivo traduzido** e só então copia os 25 arquivos para `mods\PT-BR\PS3_GAME\USRDIR\`:
  - `font\na_english\` – `dsfont24` e `talkfont24` (`.ccm.dcx` e `.tpf.dcx`): as fontes com acentos;
  - `msg\na_english\` – `item.msgbnd.dcx` e `menu.msgbnd.dcx`: todos os textos;
  - `menu\` – `menu.tpf.dcx`, `menu.drb` e `00`–`16.tpf.dcx`: letreiros (VOCÊ MORREU, DEMÔNIO DESTRUÍDO…) e telas de carregamento.
- Se algum arquivo não bater (outro mod ou tradução mexeu nele), o script para sem escrever nada.
- O mod é montado numa pasta temporária e trocado de uma vez; o `load_order.txt` é escrito numa cópia `.new` e renomeado, como o próprio Soulbrandt faz.
- Opções: `converter_ptbr_mod.py --help` (`--program`, `--setup`, `--mods`, `--nome`, `--so-fontes`, `--pacote`).

## Perguntas

**Posso compartilhar a pasta do mod pronta?**
Não. Ela contém arquivos gerados a partir da sua cópia do jogo. Compartilhe só este repositório: cada pessoa gera o mod no próprio PC.

**Funciona no RPCS3?**
Não precisa: no RPCS3 o instalador original já troca os arquivos direto no jogo, e o RPCS3 não tem as atualizações que apagam a tradução.

**E a versão europeia (BLES00932)?**
A tradução original ainda não suporta, então este mod também não.

**O que continua em inglês?**
O mesmo que na tradução original: o launcher do Soulbrandt e os menus do próprio port (F1), que estão dentro do `Soulbrandt.exe`.

## Créditos

- **Tradução PT-BR, fontes com acentos, letreiros, telas de carregamento, legendas dos vídeos e o instalador:** Fábio – **[StarKillerChief](https://github.com/StarKillerChief)**, no projeto [demons-souls-pt-br](https://github.com/StarKillerChief/demons-souls-pt-br). Todo o trabalho de tradução é dele; este repositório só muda a forma de instalar. As ferramentas dele são MIT, e o texto é uma tradução de fãs, gratuita e sem fins lucrativos (veja o `NOTICE.md` do projeto dele).
- **Soulbrandt**, o port de PC de Demon's Souls, e o sistema de mods: **[JonathanDC64](https://github.com/JonathanDC64)** e colaboradores, em [Soulbrandt](https://github.com/JonathanDC64/Soulbrandt), feito sobre o [ps3recomp](https://github.com/sp00nznet/ps3recomp) de sp00nznet.
- **Fontes usadas pela tradução original** (geradas no seu PC pelo instalador dela, não incluídas aqui): TeX Gyre Schola (GUST Font License), na opção HD, e EB Garamond (SIL Open Font License), nas telas de carregamento.
- **Demon's Souls** é da FromSoftware, Sony Interactive Entertainment e Atlus.
- **Conversor para a pasta `mods`:** [Ronaud Andrade](https://github.com/Ronaud-Andrade).

## Licença e aviso

O código deste repositório (o script e os `.bat`) está sob a licença **MIT** (veja [`LICENSE`](LICENSE)).

Projeto de fã, sem fins lucrativos, sem vínculo com FromSoftware, Sony, Atlus, Bandai Namco, Bluepoint, o autor do Soulbrandt ou o autor da tradução. Nenhum arquivo do jogo é distribuído aqui. Se algum detentor de direitos pedir, o repositório sai do ar.
