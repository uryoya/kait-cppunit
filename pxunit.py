#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from xml.sax.saxutils import *

class PXUnit:
    """
    xUnitもどきクラス
    """
    def __init__(self, testee_path, answer_path, testinput_path=None):
        self._testee = testee_path
        with open(answer_path, 'r', encoding='shift-jis') as f:
            self.answer = f.read()
        self._testinput_path = testinput_path
        if not testinput_path:
            self.testinput = None
        else:
            with open(testinput_path, 'r', encoding='shift-jis') as f:
                self.testinput = f.read()

    def run(self):
        """
        テストの実行
        """
        # テストを実行するサブプロセスを作成
        if self.testinput: # 入力ケースがあった場合
            cmd = 'echo "{}" | {}'.format(self.testinput, self._testee)
            #print(cmd)
        else:
            cmd = [self._testee]
        result = subprocess.run(cmd,
                                stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True)

        # 標準出力を受け取る
        self.output = str(result.stdout, encoding='utf-8')
        for line in self.output.split("\n"):
            print("output>", line)
        print("")
        for line in self.answer.split("\n"):
            print("answer>", line)
        print("")
        
        # テストケースと比較する
        if self.answer.lower() == self.output.lower():
            print("result> success!");
            return True
        else:
            print("result> failure!");
            return False


def doing_test(base_dir):
    """
    全てのテストケースに対してテストを実行する
    """
    # テスト対象の実行ファイルを見つける
    testee_path = "{}{}".format(base_dir, os.path.dirname(base_dir))

    # 全てのテストケースを取得
    testcase_answer = sorted([str(p) for p in Path(base_dir).glob('./answer*.txt')])
    testcase_input = sorted([str(p) for p in Path(base_dir).glob('./input*.txt')])
    result = []
    for i, answer_path in enumerate(testcase_answer):
        print()
        print('-' * 40) # draw split line
        print("Testing: {}".format(answer_path))
        if not testcase_input:
            unit = PXUnit(testee_path, answer_path)
        else:
            unit = PXUnit(testee_path, answer_path, testcase_input[i])
        is_success = unit.run()

        result.append({ # テスト結果の記録
            'number': i+1,
            'input': unit.testinput,
            'output': unit.output,
            'answer': unit.answer,
            'is_success': is_success,
        })
    return result


if __name__ == '__main__':
    base_dirs = [path + '/' for path in sys.argv[1:]]
    config_file = 'config.txt'
    env = Environment(loader=FileSystemLoader('./', encoding='utf8'))
    templete = env.get_template('templete.html')

    # ユーザ情報の取得
    user = {}
    with open(config_file, 'r') as f:
        user['gakuseki'] = f.readline().strip()
        user['realname'] = f.readline().strip()
    user['name'] = 'mox'
    user['domain'] = 'mox'
    user['computer_name'] = 'kafu-chino'

    # すべての対象に対してテストを実行
    dir_par_results = {'success':[], 'failure':[]}
    for base_dir in base_dirs:
        report_file = base_dir + 'report.html'
        source_file = [str(p) for p in Path(base_dir).glob('./*.cpp')][0]
        with open(source_file, 'r') as f:
            source_code = f.read()
        # テストの実行
        print("Start Unit Text!")
        results = doing_test(base_dir)
        all_success = True
        for result in results:
            if not result['is_success']:
                all_success = False
                break
        if all_success:
            print()
            print("All test cases was through.")
            dir_par_results['success'] = base_dir[:-1]
        else:
            print()
            print("Same test cases was failure.")
            dir_par_results['failure'] = base_dir[:-1]
        print("End!")

        # HTMLに記録する値の設定
        d = {
            'kadai_name': base_dir[:-1],
            'user': user,
            'date': datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            'source_code': escape(source_code),
            'results': results,
        }
        # HTMLの生成
        html = str(templete.render(d))
        # report.htmlの保存
        with open(report_file, 'w', encoding="shift_jis") as f:
            f.write(html)

    # 結果の表示
    if len(base_dirs) > 1:
        print()
        if len(dir_par_results['failure']) > 0:
            print("failure cases is", dir_par_results['failure'])
        else:
            print("all cases is success")

