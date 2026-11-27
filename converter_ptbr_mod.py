#!/usr/bin/env python3
"""Transforma a tradução PT-BR de Demon's Souls (StarKillerChief) já instalada no seu PC em um mod
para a pasta mods do Soulbrandt 0.2.0 ou mais novo. Assim a tradução não some a cada atualização.

    python converter_ptbr_mod.py                   cria/atualiza o mod PT-BR (padrão)
    python converter_ptbr_mod.py mod --so-fontes   cria um mod só com as 4 fontes (ex.: "PT-BR Fontes originais")
    python converter_ptbr_mod.py legendas          recoloca as legendas dos vídeos depois de uma atualização
    python converter_ptbr_mod.py tirar-legendas    volta o avcodec-62.dll oficial
    python converter_ptbr_mod.py estado            mostra o que foi encontrado, sem mudar nada

Opções: --program PASTA (a pasta do Soulbrandt.exe), --setup PASTA (a pasta de preparação do Soulbrandt,
onde fica ptbr-game), --mods PASTA (a pasta mods), --nome NOME (o nome da pasta do mod).

Este script não traz nenhum arquivo do jogo nem texto da tradução: ele só copia, no seu PC, os arquivos que o
instalador da tradução já gerou a partir da sua própria cópia do jogo, conferindo cada um pelo SHA-256.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

VERSAO = '1.0.0'
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
    program = a.program
    usr = achar_traducao(program, a.setup)
    if not usr:
        falha('não achei a tradução instalada (a pasta %s com %s\\manifest.json).\n'
              'Instale a tradução uma vez com "Tradução PT-BR.exe" (botão "Instalar tradução") e rode este '
              'script de novo. Se a pasta de preparação do Soulbrandt fica em outro lugar, use --setup PASTA.'
              % (OVERLAY, BACKUP))
    m = ler_manifesto(usr)
    mods = a.mods or pasta_mods(program)
    nome = a.nome or ('PT-BR Fontes' if a.so_fontes else 'PT-BR')
    destino = os.path.join(mods, nome)
    print('Tradução encontrada: %s' % usr)
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
            falha('falta o arquivo %s na tradução instalada. Reinstale a tradução e tente de novo.' % rel)
        if sha256(origem) != info.get('installed_sha256'):
            falha('o arquivo %s não é o que o instalador da tradução gerou (outro mod ou tradução mexeu '
                  'nele). Reinstale a tradução e tente de novo.' % rel)

    tmp = destino + '.novo'
    shutil.rmtree(tmp, ignore_errors=True)
    for rel, _info in arquivos:
        alvo = os.path.join(tmp, 'PS3_GAME', 'USRDIR', *rel.split('/'))
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        shutil.copyfile(os.path.join(usr, *rel.split('/')), alvo)
    with open(os.path.join(tmp, 'LEIA-ME.txt'), 'w', encoding='utf-8', newline='\r\n') as f:
        f.write("Tradução PT-BR de Demon's Souls, por Fábio (StarKillerChief): "
                "https://github.com/StarKillerChief/demons-souls-pt-br\n"
                "Convertida em mod do Soulbrandt pelo converter_ptbr_mod.py %s.\n\n"
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
    print('Abra o Soulbrandt e confira em Mods.')


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
        falha('não achei a pasta movie_subs (as legendas) ao lado do Soulbrandt.exe. Instale a tradução uma vez '
              'com "Tradução PT-BR.exe" para ela ser criada, e rode este comando de novo.')
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
    usr = achar_traducao(a.program, a.setup)
    print('Pasta do Soulbrandt: %s' % a.program)
    print('Pasta mods: %s' % (a.mods or pasta_mods(a.program)))
    if usr:
        m = ler_manifesto(usr)
        print('Tradução instalada: %s (versão %s, fontes %s)' % (usr, m.get('version', '?'), nome_fontes(m)))
    else:
        print('Tradução instalada: não encontrada')
    mods = a.mods or pasta_mods(a.program)
    for nome in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        if os.path.isdir(os.path.join(mods, nome)):
            print('  mod: %s' % nome)
    atual = os.path.join(a.program, DLL)
    if os.path.isfile(atual):
        print('Legendas dos vídeos: %s' % ('ligadas' if eh_nossa(atual) else 'desligadas (DLL oficial)'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('comando', nargs='?', default='mod', choices=['mod', 'legendas', 'tirar-legendas', 'estado'])
    ap.add_argument('--program', help='a pasta do Soulbrandt.exe (padrão: a pasta acima deste script)')
    ap.add_argument('--setup', help='a pasta de preparação do Soulbrandt, onde fica ptbr-game')
    ap.add_argument('--mods', help='a pasta mods do Soulbrandt')
    ap.add_argument('--nome', help='o nome da pasta do mod (padrão: PT-BR, ou "PT-BR Fontes" com --so-fontes)')
    ap.add_argument('--so-fontes', action='store_true', help='copiar só as 4 fontes')
    ap.add_argument('--pacote', help='a pasta PT-BR da tradução (para achar a DLL das legendas)')
    a = ap.parse_args()
    if not a.program:
        a.program = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    {'mod': criar_mod, 'legendas': legendas, 'tirar-legendas': tirar_legendas, 'estado': estado}[a.comando](a)


if __name__ == '__main__':
    main()
