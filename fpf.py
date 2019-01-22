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
    # 現在の辞書を読み出す（forceオプションが有効な場合は新規辞書を作成する（未実装））
    filedict = load_filedict(root)
    # キーのリストを作成しておく（ファイルの変更や消去を調べるため）
    hashkeys = list(filedict.keys())
    print('updating...')
    for (path, dirs, files) in os.walk(root):
        cwd = path.replace(root, '')
        if '.git' in cwd:
            continue
        for filename in files:
            # .fdictファイルは無視する
            if filename=='.fdict':
                continue
            # ファイルのフルパスとショートパスを取得する
            file_fullpath  = path+'/'+filename
            file_shortpath = cwd+'/'+filename
            # ファイルのハッシュ値を計算する
            hasher = hashlib.blake2b()
            with open(file_fullpath, 'rb') as fobj:
                hasher.update(fobj.read())
            digest = hasher.hexdigest()
            # キーをハッシュ値としてファイルを辞書に追加する
            # 計算したハッシュ値が今までのfdictに存在する場合
            if digest in filedict:
                # キーのリストからdigestを削除しておく
                hashkeys.remove(digest) # ← バグってる
                # 同じハッシュ値のファイルが存在したらファイルパスを確認する
                if file_shortpath!=filedict[digest]['filepath']:
                    # ファイルのパスが違う場合は確認
                    print("same file exist: {}, {}".format(file_shortpath, filedict[digest]['filepath']))
            # 計算したハッシュ値が今までのfdictに存在しない場合
            # fdictのfilepathを用いて検査中のファイルが過去に登録されていたかを確認
            #   filepathに重複が存在しない場合：未登録のファイルである
            #   filepathに重複が存在する場合　：ファイルの内容が変更された
            else:
                filedict[digest] = {
                                    'filename': filename,
                                    'filepath': file_shortpath,
                                   }
    # 更新した辞書を保存する
    save_filedict(root, filedict=filedict)
    print('done.')

# subcommands
def init(args):
    root = os.getcwd()
    if not os.path.exists(root+'/'+'.fdict'):
        save_filedict(root)
        print('initialize .fdict')
    else:
        print('.fdict already exist')

def print_filedict(args):
    root = os.getcwd()
    filedict = load_filedict(root)
    for h in filedict:
        print(filedict[h])

def update(args):
    root = os.getcwd()
    make_filedict(root)



def main():
    import argparse
    # パーサとサブパーサの作成
    parser = argparse.ArgumentParser(description='This is File ProFiler')
    subparsers = parser.add_subparsers()

    # init command
    parser_init = subparsers.add_parser('init', help='initialize .fdict file')
    parser_init.set_defaults(handler=init)

    # print command
    parser_print = subparsers.add_parser('print', help='print all data in .fdict')
    parser_print.set_defaults(handler=print_filedict)

    # update command
    parser_update = subparsers.add_parser('update', help='update .fdict')
    # forceオプションを実装したい
    parser_update.set_defaults(handler=update)

    # コマンドライン引数のパースを行いハンドラ関数を実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)


if __name__ == "__main__":
    main()
