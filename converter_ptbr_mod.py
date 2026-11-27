#!/usr/bin/env python3
"""Instala a tradução PT-BR de Demon's Souls (de Fábio, StarKillerChief) como mod da pasta mods do Soulbrandt
0.2.0 ou mais novo. Assim a tradução não some a cada atualização do Soulbrandt.

    python converter_ptbr_mod.py [instalar]        gera a tradução da sua cópia do jogo e monta o mod PT-BR (padrão)
        --fontes original|hd                         fontes originais do jogo ou HD (padrão: hd)
        --legendas                                   liga também as legendas dos vídeos
    python converter_ptbr_mod.py mod               monta o mod a partir da tradução já instalada pelo instalador dela
    python converter_ptbr_mod.py legendas          religa as legendas dos vídeos depois de uma atualização
    python converter_ptbr_mod.py tirar-legendas    volta o avcodec-62.dll oficial
    python converter_ptbr_mod.py estado            mostra o que foi encontrado, sem mudar nada

Não precisa da tradução instalada antes: o comando instalar usa as ferramentas e os textos do pacote da tradução
(PT-BR-Soulbrandt.zip) para gerar os arquivos numa pasta temporária, a partir da sua própria cópia do jogo, sem
mexer no jogo nem na preparação do Soulbrandt. Este repositório não traz nenhum arquivo do jogo.
"""
import argparse
import hashlib
import json
import os
import shutil
import importlib.util
import subprocess
import sys
import tempfile

VERSAO = '2.0.0'
OVERLAY = 'ptbr-game'
BACKUP = '.ptbr-backup'
DLL, ORIG = 'avcodec-62.dll', 'avcodec-62.orig.dll'
MARCA_DLL = ORIG.encode()  # a DLL das legendas cita o nome do arquivo original; a oficial do FFmpeg não
FONTES = ('font/',)


def falha(msg):
    print('\nERRO: ' + msg)
    sys.exit(1)


def sha256(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(1 << 20), b''):
            h.update(bloco)
    return h.hexdigest()


def local_appdata():
    return os.environ.get('LOCALAPPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Local')


def roaming_appdata():
    return os.environ.get('APPDATA') or os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')


def tem_arquivos(pasta):
    for _raiz, _dirs, arqs in os.walk(pasta):
        if arqs:
            return True
    return False


# ---------------------------------------------------------------- onde ficam as coisas

def pasta_mods(program):
    """A pasta mods, achada como o Soulbrandt 0.2.0 acha a pasta de dados:
    instalação portátil -> data\\ ao lado do programa; instalação antiga -> %APPDATA%\\DemonsSoulsRecomp\\DemonsSouls
    (se tiver algum arquivo); instalação nova -> %LOCALAPPDATA%\\Soulbrandt."""
    if program and os.path.isfile(os.path.join(program, 'portable.txt')):
        return os.path.join(program, 'data', 'mods')
    antiga = os.path.join(roaming_appdata(), 'DemonsSoulsRecomp', 'DemonsSouls')
    if os.path.isdir(antiga) and tem_arquivos(antiga):
        return os.path.join(antiga, 'mods')
    return os.path.join(local_appdata(), 'Soulbrandt', 'mods')


def candidatos_setup(program):
    lista = []
    if program and os.path.isfile(os.path.join(program, 'portable.txt')):
        lista.append(os.path.join(program, 'data', 'setup-data'))
    usual = os.path.join(local_appdata(), 'DemonsSoulsRecomp')
    try:  # a pasta escolhida na tela de preparação do Soulbrandt ("Build folder")
        for linha in open(os.path.join(usual, 'setup-folder.txt'), encoding='utf-8-sig', errors='replace'):
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                lista.append(os.path.normpath(linha if os.path.isabs(linha) else os.path.join(usual, linha)))
    except OSError:
        pass
    lista += [usual, os.path.join(local_appdata(), 'Soulbrandt'), os.path.join(local_appdata(), 'Soulbrandt', 'setup')]
    return lista


def achar_traducao(program, setup):
    """A USRDIR da pasta que o instalador da tradução montou (ptbr-game), com o manifesto dele."""
    for base in ([setup] if setup else candidatos_setup(program)):
        usr = os.path.join(base, OVERLAY, 'PS3_GAME', 'USRDIR')
        if os.path.isfile(os.path.join(usr, BACKUP, 'manifest.json')):
            return usr
    return None


def ler_manifesto(usr):
    m = json.load(open(os.path.join(usr, BACKUP, 'manifest.json'), encoding='utf-8'))
    if m.get('pack') != 'demons-souls-ptbr' or not isinstance(m.get('files'), dict):
        falha('o manifesto em %s não é da tradução PT-BR do StarKillerChief.' % usr)
    return m


def nome_fontes(m):
    return {'original': 'originais', 'hd': 'HD', 'novas': 'HD (TeX Gyre Schola)'}.get(m.get('fonts'), m.get('fonts'))


def soulbrandt_aberto():
    if os.name != 'nt':
        return False
    r = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq Soulbrandt.exe', '/NH'],
                       capture_output=True, stdin=subprocess.DEVNULL)
    return b'Soulbrandt.exe' in (r.stdout or b'')


# ---------------------------------------------------------------- o mod

def ligar_no_load_order(mods, nome):
    """Põe 'on NOME' na primeira linha de mod do load_order.txt (a primeira linha ganha), sem mexer nas outras."""
    caminho = os.path.join(mods, 'load_order.txt')
    linhas = []
    if os.path.isfile(caminho):
        linhas = open(caminho, encoding='utf-8-sig', errors='replace').read().splitlines()
    comentarios, resto = [], []
    for l in linhas:
        partes = l.strip().split(' ', 1)
        if len(partes) == 2 and partes[0] in ('on', 'off') and partes[1].strip() == nome:
            continue  # a linha antiga deste mod sai; a nova vai para o topo
        (comentarios if (not resto and (not l.strip() or l.lstrip().startswith('#'))) else resto).append(l)
    if not comentarios:
        comentarios = ['# Soulbrandt: on/off, um espaço e o nome da pasta do mod. A primeira linha ganha.']
    novo = comentarios + ['on ' + nome] + resto
    tmp = caminho + '.new'
    with open(tmp, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(novo) + '\n')
    os.replace(tmp, caminho)


def criar_mod(a):
    """Comando 'mod': usa a tradução que o instalador original já montou (ptbr-game)."""
    usr = achar_traducao(a.program, a.setup)
    if not usr:
        falha('não achei a tradução instalada (a pasta %s com %s\\manifest.json).\n'
              'Use o "1 - Instalar traducao PT-BR.bat", que não precisa da tradução instalada antes.'
              % (OVERLAY, BACKUP))
    m = ler_manifesto(usr)
    print('Tradução encontrada: %s' % usr)
    gravar_mod(a, usr, m)


def gravar_mod(a, usr, m):
    """Confere os arquivos traduzidos de `usr` (pelo manifesto `m`) e monta o mod na pasta mods."""
    mods = a.mods or pasta_mods(a.program)
    nome = a.nome or ('PT-BR Fontes' if a.so_fontes else 'PT-BR')
    destino = os.path.join(mods, nome)
    print('  versão %s, fontes %s, %d arquivos' % (m.get('version', '?'), nome_fontes(m), len(m['files'])))
    print('Pasta mods: %s' % mods)
    if soulbrandt_aberto():
        falha('feche o Soulbrandt antes de continuar.')

    arquivos = [(rel, info) for rel, info in sorted(m['files'].items())
                if not a.so_fontes or rel.startswith(FONTES)]
    if not arquivos:
        falha('nenhum arquivo para copiar.')
    # confere tudo antes de escrever qualquer coisa
    for rel, info in arquivos:
        origem = os.path.join(usr, *rel.split('/'))
        if not os.path.isfile(origem):
            falha('falta o arquivo %s na tradução. Rode de novo.' % rel)
        if sha256(origem) != info.get('installed_sha256'):
            falha('o arquivo %s não é o que a tradução gerou (outro mod ou tradução mexeu nele).' % rel)

    tmp = destino + '.novo'
    shutil.rmtree(tmp, ignore_errors=True)
    for rel, _info in arquivos:
        alvo = os.path.join(tmp, 'PS3_GAME', 'USRDIR', *rel.split('/'))
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        shutil.copyfile(os.path.join(usr, *rel.split('/')), alvo)
    with open(os.path.join(tmp, 'LEIA-ME.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("Tradução PT-BR de Demon's Souls, por Fábio (StarKillerChief): "
                "https://github.com/StarKillerChief/demons-souls-pt-br\n"
                "Montada como mod do Soulbrandt pelo converter_ptbr_mod.py %s "
                "(https://github.com/Ronaud-Andrade/SoulBrandt_pt-br).\n\n"
                "Versão da tradução: %s. Fontes: %s.%s\n\n"
                "Estes arquivos foram gerados a partir da SUA cópia do jogo. Não compartilhe.\n"
                "Ligue ou desligue no menu Mods do Soulbrandt.\n"
                % (VERSAO, m.get('version', '?'), nome_fontes(m),
                   ' Só as fontes.' if a.so_fontes else ''))
    os.makedirs(mods, exist_ok=True)
    if os.path.isdir(destino):
        shutil.rmtree(destino)
    os.replace(tmp, destino)
    ligar_no_load_order(mods, nome)
    print('\nPronto: mod "%s" criado com %d arquivos e ligado no topo da lista.' % (nome, len(arquivos)))


# ---------------------------------------------------------------- instalar sem a tradução instalada antes

def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def achar_pacote(a):
    """A pasta PT-BR do pacote da tradução (o PT-BR-Soulbrandt.zip do StarKillerChief, extraído)."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    for base in ([a.pacote] if a.pacote else [os.path.join(aqui, 'PT-BR'), os.path.join(a.program, 'PT-BR'),
                                               os.path.join(aqui, '..', 'PT-BR')]):
        if base and os.path.isfile(os.path.join(base, 'pack', 'tools', 'install_ptbr.py')):
            return os.path.normpath(base)
    falha('não achei o pacote da tradução (a pasta PT-BR com pack\\tools\\install_ptbr.py). '
          'O "1 - Instalar traducao PT-BR.bat" baixa ele sozinho; ou use --pacote PASTA.')


def achar_jogo(a):
    """A USRDIR do jogo que o Soulbrandt usa: a linha game= do setup/ready.txt da preparação dele."""
    if a.jogo:
        jogo = a.jogo
    else:
        jogo = None
        for base in ([a.setup] if a.setup else candidatos_setup(a.program)):
            pronto = os.path.join(base, 'setup', 'ready.txt')
            if not os.path.isfile(pronto):
                continue
            for linha in open(pronto, encoding='utf-8-sig', errors='replace'):
                if linha.startswith('game='):
                    v = linha[5:].strip()
                    jogo = os.path.normpath(v if os.path.isabs(v) else os.path.join(base, v))
                    break
            if jogo:
                break
        if not jogo:
            falha('não achei o jogo do Soulbrandt. Abra o Soulbrandt uma vez e deixe ele preparar o jogo até o fim; '
                  'ou use --jogo PASTA (a pasta que tem PS3_GAME).')
    usr = jogo if os.path.basename(os.path.normpath(jogo)).upper() == 'USRDIR' else os.path.join(jogo, 'PS3_GAME', 'USRDIR')
    if not os.path.isdir(usr):
        falha('a pasta do jogo %s não tem PS3_GAME\\USRDIR.' % jogo)
    return usr


def instalar(a):
    """Comando 'instalar': gera a tradução direto da cópia do jogo, numa pasta temporária, e monta o mod.
    Não precisa da tradução instalada antes, e não mexe no jogo nem na preparação do Soulbrandt."""
    pacote = achar_pacote(a)
    usr_jogo = achar_jogo(a)
    tools = os.path.join(pacote, 'pack', 'tools')
    print('Pacote da tradução: %s' % pacote)
    print('Jogo: %s' % usr_jogo)
    if soulbrandt_aberto():
        falha('feche o Soulbrandt antes de continuar.')
    inst = carregar('install_ptbr', os.path.join(tools, 'install_ptbr.py'))
    fontes = {'original': 'original', 'hd': 'novas'}[a.fontes]
    with tempfile.TemporaryDirectory(prefix='ptbr_mod_') as tmp:
        raiz = os.path.join(tmp, 'jogo')
        usr = os.path.join(raiz, 'PS3_GAME', 'USRDIR')
        os.makedirs(usr)
        shutil.copyfile(os.path.join(os.path.dirname(usr_jogo), 'PARAM.SFO'), os.path.join(raiz, 'PS3_GAME', 'PARAM.SFO'))
        # só os arquivos que a tradução troca (e os gêmeos sem .dcx), lidos sem mexer no jogo; se a pasta do jogo
        # tiver uma tradução antiga instalada por cima, os originais guardados por ela são usados
        for rel in inst.TARGETS:
            for r in ([rel, rel[:-4]] if rel.endswith('.dcx') else [rel]):
                guardado = os.path.join(usr_jogo, BACKUP, *r.split('/'))
                origem = guardado if os.path.isfile(guardado) else os.path.join(usr_jogo, *r.split('/'))
                if os.path.isfile(origem):
                    alvo = os.path.join(usr, *r.split('/'))
                    os.makedirs(os.path.dirname(alvo), exist_ok=True)
                    shutil.copyfile(origem, alvo)
        print('\nGerando a tradução a partir da sua cópia do jogo (pode levar até 1 minuto)...\n', flush=True)
        try:
            inst.install(usr, inst.TEXT, fontes)
        except SystemExit as e:
            if e.code not in (None, 0):
                falha(str(e.code))
        m = inst.read_manifest(usr)
        print()
        gravar_mod(a, usr, m)
        if a.legendas:
            print()
            gerar_legendas(a, pacote, raiz)
    print('Abra o Soulbrandt e confira em Mods.')


def gerar_legendas(a, pacote, raiz_traduzida):
    """Cria a pasta movie_subs (as legendas dos vídeos) e liga a DLL das legendas."""
    program = a.program
    if not os.path.isfile(os.path.join(program, DLL)):
        print('Legendas dos vídeos: não achei %s na pasta do Soulbrandt (%s); seguindo sem elas.' % (DLL, program))
        return
    gerador = os.path.join(pacote, 'pack', 'tools', 'movie_subs', 'make_movie_subs.py')
    textos = os.path.join(pacote, 'pack', 'text', 'movies')
    if not os.path.isfile(gerador) or not os.path.isdir(textos):
        print('Legendas dos vídeos: este pacote da tradução não tem o gerador; seguindo sem elas.')
        return
    saida = os.path.join(program, 'movie_subs')
    shutil.rmtree(saida, ignore_errors=True)
    mk = carregar('make_movie_subs', gerador)
    argv = sys.argv
    sys.argv = ['make_movie_subs', '--game', raiz_traduzida, '--subs', textos, '--out', saida]
    try:
        mk.main()
    finally:
        sys.argv = argv
    a.pacote = pacote
    legendas(a)


# ---------------------------------------------------------------- legendas dos vídeos

def eh_nossa(caminho):
    try:
        return MARCA_DLL in open(caminho, 'rb').read()
    except OSError:
        return False


def achar_dll_legendas(program, pacote):
    for base in [pacote] if pacote else [os.path.join(program, 'PT-BR'),
                                         os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'PT-BR')]:
        if base:
            p = os.path.join(base, 'pack', 'tools', 'movie_subs', DLL)
            if os.path.isfile(p):
                return os.path.normpath(p)
    return None


def legendas(a):
    program = a.program
    atual = os.path.join(program, DLL)
    if not os.path.isfile(atual):
        falha('não achei %s em %s. Use --program com a pasta do Soulbrandt.exe.' % (DLL, program))
    if not os.path.isdir(os.path.join(program, 'movie_subs')):
        falha('não achei a pasta movie_subs (as legendas) ao lado do Soulbrandt.exe. Rode o '
              '"1 - Instalar traducao PT-BR.bat" e responda S quando ele perguntar das legendas.')
    nossa = achar_dll_legendas(program, a.pacote)
    if not nossa:
        falha('não achei a DLL das legendas (PT-BR\\pack\\tools\\movie_subs\\%s). Use --pacote PASTA com a pasta '
              'PT-BR da tradução.' % DLL)
    if soulbrandt_aberto():
        falha('feche o Soulbrandt antes de continuar.')
    if eh_nossa(atual):
        print('As legendas dos vídeos já estão ligadas.')
        return
    # a oficial (que a atualização trouxe) vira a .orig, e a DLL das legendas entra no lugar
    shutil.copyfile(atual, os.path.join(program, ORIG))
    shutil.copyfile(nossa, atual + '.tmp')
    os.replace(atual + '.tmp', atual)
    print('Pronto: legendas dos vídeos ligadas. A DLL oficial ficou guardada como %s.' % ORIG)
    print('Cada atualização do Soulbrandt desfaz isso; é só rodar este comando de novo.')


def tirar_legendas(a):
    program = a.program
    atual, orig = os.path.join(program, DLL), os.path.join(program, ORIG)
    if soulbrandt_aberto():
        falha('feche o Soulbrandt antes de continuar.')
    if eh_nossa(atual):
        if not os.path.isfile(orig):
            falha('a DLL oficial (%s) sumiu. Reinstale o Soulbrandt para recuperá-la.' % ORIG)
        os.replace(orig, atual)
        print('Pronto: o %s oficial voltou; os vídeos tocam sem legendas.' % DLL)
    else:
        print('O %s já é o oficial. Nada a fazer.' % DLL)


def estado(a):
    print('Pasta do Soulbrandt: %s' % a.program)
    print('Pasta mods: %s' % (a.mods or pasta_mods(a.program)))
    aqui = os.path.dirname(os.path.abspath(__file__))
    pacote = next((p for p in ([a.pacote] if a.pacote else [os.path.join(aqui, 'PT-BR'), os.path.join(a.program, 'PT-BR')])
                   if p and os.path.isfile(os.path.join(p, 'pack', 'tools', 'install_ptbr.py'))), None)
    print('Pacote da tradução: %s' % (pacote or 'ainda não baixado (o "1 - Instalar traducao PT-BR.bat" baixa)'))
    usr = achar_traducao(a.program, a.setup)
    if usr:
        m = ler_manifesto(usr)
        print('Instalação antiga da tradução (ptbr-game): %s (versão %s, fontes %s)'
              % (usr, m.get('version', '?'), nome_fontes(m)))
    mods = a.mods or pasta_mods(a.program)
    for nome in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        if os.path.isdir(os.path.join(mods, nome)):
            print('  mod: %s' % nome)
    atual = os.path.join(a.program, DLL)
    if os.path.isfile(atual):
        print('Legendas dos vídeos: %s' % ('ligadas' if eh_nossa(atual) else 'desligadas (DLL oficial)'))


def achar_programa():
    """A pasta do Soulbrandt.exe: a pasta acima deste script, a deste script, ou a mais recente que o próprio
    Soulbrandt anotou em game-folders.txt na pasta de dados dele."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(aqui, '..'), aqui):
        if os.path.isfile(os.path.join(p, 'Soulbrandt.exe')):
            return os.path.normpath(p)
    for dados in (os.path.join(roaming_appdata(), 'DemonsSoulsRecomp', 'DemonsSouls'),
                  os.path.join(local_appdata(), 'Soulbrandt')):
        try:
            for linha in open(os.path.join(dados, 'game-folders.txt'), encoding='utf-8-sig', errors='replace'):
                partes = linha.rstrip('\r\n').split('\t')
                if not linha.startswith('#') and len(partes) == 2 and os.path.isfile(os.path.join(partes[1], 'Soulbrandt.exe')):
                    return partes[1]   # a primeira linha é a mais recente
        except OSError:
            pass
    return os.path.normpath(os.path.join(aqui, '..'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('comando', nargs='?', default='instalar',
                    choices=['instalar', 'mod', 'legendas', 'tirar-legendas', 'estado'])
    ap.add_argument('--fontes', choices=['original', 'hd'], default='hd',
                    help='instalar: as fontes originais do jogo ou as fontes HD (padrão)')
    ap.add_argument('--legendas', action='store_true', help='instalar: ligar também as legendas dos vídeos')
    ap.add_argument('--program', help='a pasta do Soulbrandt.exe (padrão: achada sozinha)')
    ap.add_argument('--setup', help='a pasta de preparação do Soulbrandt (onde ficam setup\\ready.txt e ptbr-game)')
    ap.add_argument('--jogo', help='instalar: a pasta do jogo (a que tem PS3_GAME), se não for achada sozinha')
    ap.add_argument('--mods', help='a pasta mods do Soulbrandt')
    ap.add_argument('--nome', help='o nome da pasta do mod (padrão: PT-BR, ou "PT-BR Fontes" com --so-fontes)')
    ap.add_argument('--so-fontes', action='store_true', help='só as 4 fontes (para um segundo mod de fontes)')
    ap.add_argument('--pacote', help='a pasta PT-BR do pacote da tradução')
    a = ap.parse_args()
    if not a.program:
        a.program = achar_programa()
    {'instalar': instalar, 'mod': criar_mod, 'legendas': legendas, 'tirar-legendas': tirar_legendas,
     'estado': estado}[a.comando](a)


if __name__ == '__main__':
    main()
