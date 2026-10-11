#!/usr/bin/env python3
"""Quick end-to-end smoke test: synthetic images only, NOT aesthetic evaluation."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

MAIN = Path(__file__).with_name('photo_workflow.py')


def call(*args, success=True):
    p = subprocess.run([sys.executable, str(MAIN), *args],
                       encoding='utf-8', capture_output=True)
    if success and p.returncode:
        raise AssertionError(f'命令失败：{args}\n{p.stdout}\n{p.stderr}')
    if not success and p.returncode == 0:
        raise AssertionError(f'命令本应失败却成功：{args}')
    return p


def main():
    with tempfile.TemporaryDirectory(prefix='portrait_skill_selftest_') as temp:
        d = Path(temp)
        src, out = d / 'photos', d / 'result'
        (src / 'sub').mkdir(parents=True)
        for i, p in enumerate([src/'1.jpg', src/'sub'/'1.jpg', src/'3.png'], 1):
            im = Image.new('RGB', (1000, 750), (210-i*20, 210-i*10, 210-i*30))
            ImageDraw.Draw(im).ellipse((150, 150, 800, 630), outline=(120, 50, 90), width=15)
            im.save(p)
        call('prepare', '--input', str(src), '--output', str(out), '--batch-size', '3')
        call('verify', '--output', str(out), '--phase', 'review', success=False)
        batch = json.loads((out/'_work'/'batches'/'batch_001.json').read_text())['items']
        ids = [x['id'] for x in batch]
        a = {'id':ids[0], 'grade':'A', 'title':'测试A', 'verdict':'适合直出',
             'strengths':[{'observation':'画面明确', 'principle':'视觉引导', 'repeat':'多观察'}]*3,
             'next_shoot':['保持现有构图']}
        b = {'id':ids[1], 'grade':'B', 'title':'测试B', 'potential':'可修复',
             'issues':[{'observation':'背景干扰', 'impact':'注意力偏离', 'principle':'视觉重量',
                        'capture_prevention':'换机位'}],
             'xingtu':{'goal':'减少干扰', 'steps':[{'tool':'裁剪', 'action':'左侧缩小',
                        'start':'裁掉5%起试', 'reason':'集中注意力', 'check':'脸部不裁掉'}],
                        'avoid':['过度操作'], 'export':'保留原图'},
             'learning':[{'rule':'简化构图', 'applied':'用裁剪去除干扰', 'next_shoot':'避开杂乱元素'}],
             'reshoot':['移动机位']}
        c = {'id':ids[2], 'grade':'C'}
        review_file = out/'_work'/'reviews'/'batch_001.json'
        review_file.write_text(json.dumps({'items':[a,b,{**c,'reason':'禁止的C注释'}]}, ensure_ascii=False))
        call('verify', '--output', str(out), '--phase', 'review', success=False)
        review_file.write_text(json.dumps({'items':[a,b,c]}, ensure_ascii=False))
        call('verify', '--output', str(out), '--phase', 'review')
        call('detail', '--output', str(out), '--id', ids[2], '--size', '2300')
        call('finalize', '--output', str(out))
        v = call('verify', '--output', str(out), '--phase', 'final')
        assert (out/'A_可直接出片'/'A档_摄影优点与复现方法_第01册.docx').exists()
        assert (out/'B_后期可出片'/'B档_醒图修图步骤与摄影规则_第01册.docx').exists()
        assert list((out/'C_废片').glob('*.docx')) == []
        call('finalize', '--output', str(out), success=False)  # must not overwrite
        print('SELFTEST OK: prepared, rejected invalid C, verified grades, created docs, hashed files, blocked overwrite')
        print(v.stdout.strip())


if __name__ == '__main__':
    main()
