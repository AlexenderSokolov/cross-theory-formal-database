from pathlib import Path
import copy,importlib.util,json
import convert_drops_html as current
lane=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('previous_converter',lane/'convert_drops_html-before-svg.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
p=lane/'sources/ccc2025-24'
parser=current.Parser();parser.feed((p/'published.html').read_text())
actual=next(current.nodes(parser.root,'object'))
old_parser=previous.Parser();old_parser.feed((p/'published.html').read_text())
assert previous.render(next(previous.nodes(old_parser.root,'object'))).strip()==''
ledger=json.loads((p/'svg-asset-ledger.json').read_text())
current.GRAPHICS.update({x['html_data']:Path(x['target']).name for x in ledger['objects']})
assert current.render(actual).count(r'\includegraphics')==1
assert Path(ledger['objects'][0]['target']).name in current.render(actual)
fallback=copy.deepcopy(actual)
fallback.c.append(current.N('img',[('src',actual.a['data'])]))
assert current.render(fallback).count(r'\includegraphics')==1
print('PASS: real SVG object was omitted before; declared PDF included once after repair, including fallback img.')
