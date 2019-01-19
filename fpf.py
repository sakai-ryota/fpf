#!/usr/bin/env python3

# fpf: File ProFiler
# dictionary configuration
#   key:    filename: str
#   value:  dictionary
#       dictionary_attr:
#               * hash of file: str
#               * filepath: str
#               * (author): str
#               * (publication year): int
#               * (journal): str
#               * (keywords): [str]
#           (hoge) is optional

import os
import hashlib
import pickle

# save and load dictionary functions
def save_filedict(root, filedict={}):
    # 辞書をファイルへと書き出す
    with open(root+'/'+'.fdict', 'wb') as f:
        pickle.dump(filedict, f)

def load_filedict(root):
    # 辞書を呼び出して返す
    # 辞書ファイルが存在しない場合はエラー
    import sys
    if os.path.exists(root+'/'+'.fdict'):
        with open(root+'/'+'.fdict', 'rb') as f:
            filedict = pickle.load(f)
        return filedict
    else:
        print('.fdict file not exist')
        sys.exit(1)

# complex function
def make_filedict(root):
    # 現在の辞書を読み出す
    filedict = load_filedict(root)
    print('updating...')
    for (path, dirs, files) in os.walk(root):
        for filename in files:
            # .fdictファイルは無視する
            if filename=='.fdict':
                continue
            # ファイルのフルパスを取得する
            file_fullpath = path+'/'+filename
            # ファイルのハッシュ値を計算する
            hasher = hashlib.md5()
            with open(file_fullpath, 'rb') as fobj:
                while True:
                    chunk = fobj.read(2048*hasher.block_size)
                    if len(chunk) == 0:
                        break
                    hasher.update(chunk)
            digest = hasher.hexdigest()
            # キーをハッシュ値としてファイルを辞書に追加する
            # 同じハッシュ値をもつファイルに出会ったときの処理をまだ考えていない．
            filedict[filename] = {
                                'hash': digest,
                                'filepath': file_fullpath.replace(root+'/', ''),
                               }
    # 更新した辞書を保存する
    save_filedict(root, filedict=filedict)
    print('done.')

# get root
def get_root(args):
    if args.d == None:
        return os.getcwd()
    else:
        return args.d

# subcommands
def init(args):
    root = get_root(args)
    if not os.path.exists(root+'/'+'.fdict'):
        save_filedict(root)
        print('initialize .fdict')
    else:
        print('.fdict already exist')

def print_filedict(args):
    root = get_root(args)
    filedict = load_filedict(root)
    for h in filedict:
        print(filedict[h])

def update(args):
    root = get_root(args)
    make_filedict(root)



def main():
    import argparse
    # パーサとサブパーサの作成
    parser = argparse.ArgumentParser(description='This is File ProFiler')
    parser.add_argument('-d', help='working directory')
    subparsers = parser.add_subparsers()

    # init command
    parser_init = subparsers.add_parser('init', help='initialize .fdict file')
    parser_init.set_defaults(handler=init)

    # print command
    parser_print = subparsers.add_parser('print', help='print all data in .fdict')
    parser_print.set_defaults(handler=print_filedict)

    # update command
    parser_update = subparsers.add_parser('update', help='update .fdict')
    parser_update.set_defaults(handler=update)

    # コマンドライン引数のパースを行いハンドラ関数を実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)


if __name__ == "__main__":
    main()
