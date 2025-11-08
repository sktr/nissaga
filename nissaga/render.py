from yamlns import namespace as ns
from .styles import applyStyles
import datetime

# グローバル locale 設定（デフォルト: 自動判定）
CURRENT_LOCALE = None

familyColors=[
    '#1abc9c',
    '#2ecc71',
    '#3498db',
    '#9b59b6',
    '#34495e',
    '#f1c40f',
    '#e67e22',
    '#e74c3c',
]

def escape(s):
    # TODO: review this
    if type(s)==str:
        return '"'+s+'"'
    return s

def detect_locale(text):
    """テキストから locale を自動判定
    
    Returns:
        'en': アルファベットを含む
        'ja': それ以外（日本語文字のみ）
    """
    if not text:
        return 'ja'
    
    for char in str(text):
        # アルファベット判定
        if char.isalpha() and ord(char) < 128:  # ASCII アルファベット
            return 'en'
    
    # アルファベットがない場合は日本語
    return 'ja'

def _detect_root_locale(root):
    """YAML データから最適な locale を自動判定
    
    全人物のフルネームを調査して、アルファベットが1つでもあれば 'en'、
    それ以外（漢字・ひらがな・カタカナのみ）なら 'ja' を返す
    
    Returns:
        'ja' または 'en'
    """
    if not root or not root.people:
        return 'ja'  # デフォルト
    
    # 全人物の name/fullname を集計
    for person in root.people.values():
        if person:
            name = person.fullname or person.name
            if name and detect_locale(name) == 'en':
                # 1つでもアルファベットがあれば 'en'
                return 'en'
    
    # すべて日本語の場合
    return 'ja'

def formatdate(date, locale='ja'):
    if not isinstance(date, datetime.date):
        return date
    
    if locale == 'en':
        # 英語：MMM DD, YYYY 形式
        return date.strftime('%b %d, %Y')
    else:
        # 日本語：和暦
        return to_wareki(date)

def to_wareki(date):
    """西暦を和暦に変換（簡易版）
    
    Returns:
        '昭和12年3月4日' 形式の文字列
    """
    if not isinstance(date, datetime.date):
        return date

    # 主な元号のみサポート（開始日を厳密に判定）
    eras = [
        (datetime.date(2019, 5, 1), '令和'),
        (datetime.date(1989, 1, 8), '平成'),
        (datetime.date(1926, 12, 25), '昭和'),
        (datetime.date(1912, 7, 30), '大正'),
        (datetime.date(1868, 1, 25), '明治'),
    ]

    for start_date, era_name in eras:
        if date >= start_date:
            era_year = date.year - start_date.year + 1
            year_str = '元' if era_year == 1 else str(era_year)
            return f"{era_name}{year_str}年{date.month}月{date.day}日"

    # 対応外（明治以前）は西暦表記で返す
    return f"{date.year}年{date.month}月{date.day}日"

def low(lines):
    "Reduces a level of sublisting"
    return sum((l for l in lines), [])

def indenter(lines, spacer='  '):
    "Considers each level of sublisting an indented block"

    def subindenter(lines, level=-1):
        if type(lines) == str:
            return [level*spacer + lines]
        return low(
            subindenter(element, level+1)
            for element in lines
        )

    return '\n'.join(subindenter(lines))

def render(root, locale=None):
    """DOT ファイルをレンダリング
    
    Args:
        root: Nissaga ルートオブジェクト
        locale: 言語設定 ('ja' / 'en')。None の場合は YAML データから自動判定
    """
    global CURRENT_LOCALE
    
    # locale の決定：CLI引数 > 自動判定
    if locale:
        CURRENT_LOCALE = locale
    else:
        # YAML データから自動判定
        CURRENT_LOCALE = _detect_root_locale(root)
    
    return indenter([
        'digraph G {', [
            'edge [',
                applyStyles(root, ':edge', locale=CURRENT_LOCALE),
            ']',
            '',
            'node [',
                applyStyles(root, ':node', locale=CURRENT_LOCALE),
            ']',
            '',
            ] + applyStyles(root, ':digraph', locale=CURRENT_LOCALE) + [
            '',
        ]+
        low(
            renderFamily(root, root, f, [str(i)])
            for i,f in enumerate(root.families or [])
        )+
        low(
            renderPerson(root, p, [str(n)])
            for i,(n,p) in enumerate((root.people or ns()).items())
        ),
        '}'
    ])


def renderFamily(root, house, family, path):

    def renderHousePrelude(family, path):
        if not family.house:
            return []
        return [
            '#'*76,
            f'# House {".".join(path)} - {family.house}',
            '#'*76,
            '',
            f'label=<<b>{family.house}</b>>',
            #f'labelhref="{family.links and family.links[0]}"',
            ] + applyStyles(root, ':house',
                post=dict(
                    color="#fafafa" if not len(path)&1 else "#f4f4f4"
                )
            ) + [
            '',
        ]

    def renderParents(family, id):
        if not family.parents:
            return ['# No parents']

        union = f'union_{id}'
        state = []

        # TODO: Pydantic in python 3.6 turns bools into ints
        married = formatdate(family.married)
        if married is False or married == 0:
            state.append('⚯')
        elif married is not True and married != 1:
            state.append(f'⚭ {married}')

        # TODO: Pydantic in python 3.6 turns bools into ints
        divorced = formatdate(family.divorced)
        if divorced is True or divorced == 1:
            state.append('⚮')
        elif divorced is not False and divorced != 0:
            state.append(f'⚮ {divorced}')

        state = '\n'.join(state)

        return [
            f'{union} [', (
                ([ f'xlabel="{state}"' ] if state else []) +
                applyStyles(root, ':union', pre=dict(
                    fillcolor=familyColor,
                ))
            ),
            ']',
            '',
        ] + ([
            f'{{{", ".join([escape(p) for p in family.parents])}}} -> {union} [',
            applyStyles(root, ':parent-link', pre=dict(
                color=familyColor,
            )),
            ']',
        ] if family.parents else [])

    def renderLink(family, id):
        if not family.parents: return []
        if not family.children: return []

        return [
          f'union_{id} -> siblings_{id} [',
            applyStyles(root,
                ':parent-child-link', 
                pre=dict(
                    color=familyColor
                ),
            ),
          ']',
        ]

    def renderKids(family, id):
        if not family.children:
            return ['# No children']

        kids = f'siblings_{id}'
        union = f'union_{id}'
        return [
            f'{kids} [',
            applyStyles(root, ':children', pre=dict(fillcolor=familyColor),
            ),
            ']',
        ] + [
            f'{kids} -> {{{", ".join([escape(p) for p in family.children])}}} [',
            applyStyles(root, ':child-link', pre=dict(color=familyColor)),
            ']',
        ]

    familyColor = familyColors[ int(path[-1]) % len(familyColors) ]
    slug='_'.join(str(p) for p in path)
    jointparents = ', '.join([p for p in family.parents or [] if p]) or "none"
    jointchildren = ', '.join([p for p in family.children or [] if p]) or "none"
    return [
        f'subgraph cluster_family_{slug} {{', [
            ] + applyStyles(root, ':family') + [
            '',
            ] +
            renderHousePrelude(family, path) +
            renderSubFamilies(root, family, path) +
            [
            f'# Family [{jointparents}] -> [{jointchildren}]', 
            '# ' + '-'*74,
            '',
            ] +
            renderParents(family, slug) +
            renderLink(family, slug) +
            renderKids(family, slug) +
            [],
        '}',
        '',
    ]


def renderPerson(root, person, path):
    id = path[-1]
    unknown = '????-??-??'

    if not person:
        person=ns(
            born=None,
            died=None,
            fullname=id,
            links=[],
            pics=[],
        )

    href = person.links and person.links[0]
    pic = person.pics and person.pics[0]

    # locale を自動判定（人物の fullname から、またはグローバル設定）
    global CURRENT_LOCALE
    locale = CURRENT_LOCALE or detect_locale(person.fullname or person.name or id)

    # TODO: Pydantic in python 3.6 turns bools into ints
    born = formatdate(person.born, locale=locale)
    if born is False or born == 0: born = '†*' # stillborn
    elif born is None: born = '' # just as True, the default
    elif born is True or born == 1: born = '' # born
    else:
        if locale == 'en':
            born = f"* {born}"
        else:
            born = f"{born}"

    # TODO: Pydantic in python 3.6 turns bools into ints
    died = formatdate(person.died, locale=locale)
    if died is None: died = '' # Not specified
    elif died is False or died == 0: died = '' # Explicit alive
    elif died is True or died == 1: died = "†" # Dead but no date
    else:
        if locale == 'en':
            died = f"† {died}"
        else:
            died = f"{died}"

    name = person and person.fullname or person.name or id
    
    # locale に応じて縦書き/横書きを切り替え
    if locale == 'en':
        # 英語：横書きレイアウト
        surname, firstname = ([' ']+name.split(','))[-2:]
        picsize = 40, 40 # TODO: configurable
        label = "\n".join([
          '<table align="center" border="0" cellpadding="0" cellspacing="1">',
          '<tr>',
          (
              f'<td rowspan="3" width="{picsize[0]}" height="{picsize[1]}" fixedsize="true"><img src="pics/{pic}" scale="TRUE"></img></td>'
              if pic else
              f'<td rowspan="3" width="{picsize[0]}" height="{picsize[1]}" fixedsize="true"></td>'
          ),
          f'<td colspan="2">{firstname}</td>',
          "</tr>",
          "<tr>",
          f'<td colspan="2"><font point-size="12" color="#ffffff">{surname}</font></td>',
          '</tr>',
          '<tr>',
          f'<td align="left" width="60"><font point-size="10" color="#ffffff"> {born} </font></td>',
          f'<td align="left" width="60"><font point-size="10" color="#ffffff"> {died} </font></td>',
          '</tr>',
          '</table>',
        ])
    else:
        # 日本語：縦書きレイアウト
        def vertical_text(text):
            if not text or text.strip() == '':
                return ''
            text = text.strip()
            # 各文字を<br/>で区切る
            return '<br/>'.join(text)
        
        name_display = vertical_text(name)
        born_display = vertical_text(born) if born else ''
        died_display = vertical_text(died) if died else ''
        
        picsize = 50, 50 # TODO: configurable
        
        # テーブル行を動的に構築（写真を一番上に配置）
        rows = [
          '<table align="center" border="0" cellpadding="2" cellspacing="0">',
          '<tr>',
          (
              f'<td width="{picsize[0]}" height="{picsize[1]}" fixedsize="true"><img src="pics/{pic}" scale="TRUE"></img></td>'
              if pic else
              f'<td width="{picsize[0]}" height="{picsize[1]}" fixedsize="true"></td>'
          ),
          '</tr>',
          '<tr>',
          f'<td><font point-size="10">{name_display}</font></td>',
          '</tr>',
        ]
        
        if born_display:
          rows.extend([
            '<tr>',
            f'<td><font point-size="8">{born_display}</font></td>',
            '</tr>',
          ])
        
        if died_display:
          rows.extend([
            '<tr>',
            f'<td><font point-size="8">{died_display}</font></td>',
            '</tr>',
          ])
        
        rows.append('</table>')
        
        label = "\n".join(rows)
    
    link = f'URL="{person.links[0]}"' if person.links else []
    return [
        f'{escape(id)} [', [
            link,
            low([
                applyStyles(root, cls)
                for cls in person.class_
            ]),
            f'label=<{label}>',
        ],']',
    ]

def renderSubFamilies(root, family, path):
    return low(
        renderFamily(root, family, f or {}, path+[str(i)])
        for i,f in enumerate(family.families or [])
    )


