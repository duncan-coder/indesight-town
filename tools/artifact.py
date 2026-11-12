"""把 site/index.html 轉成 Claude 試玩頁用的片段（去掉 doctype、html、head、body 外殼）。"""
import sys
src = open(sys.argv[1], encoding='utf-8').read()
head, rest = src.split('<header>', 1)
head = head.split('<meta name="viewport"', 1)[1].split('>', 1)[1].replace('</head>', '').replace('<body>', '').strip()
body = rest.rsplit('</body>', 1)[0]
open(sys.argv[2], 'w', encoding='utf-8').write(head + '\n\n<header>' + body)
