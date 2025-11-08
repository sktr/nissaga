from yamlns import namespace as ns

default_styles = ns.loads("""
  # エッジ（矢印の線）のデフォルトスタイル
  ':edge':
    dir: 'none'             # 矢印なし
    color: '#cccccc'        # 薄いグレーの線

  # 家系（グループ）のラベル表示用サブグラフ（例：家名や背景ボックス）
  ':house':
    style: 'filled'         # 塗りつぶしスタイル
    color: '#fafafa'        # 非常に淡いグレー
    labeljust: 'l'          # ラベルを左寄せ
    fontname: 'Helvetica, Arial, sans-serif'  # 使用フォント
    fontsize: 16            # フォントサイズ
    fontcolor: '#ffffff'  # ラベルの文字色
    margin: 10              # 内側の余白
    fillcolor: '#016d3e80'  # 背景色 （変更した）

  # 派生または特殊な家系グループ用スタイル
  ':house-2':
    color: '#ffffff'        # 背景白

  # 家族を囲う透明なサブグラフ（視覚的には表示されないがグルーピングに使う）
  ':family':
    label: ''               # ラベルなし
    style: 'invis'          # 完全に非表示
    margin: 0               # 余白なし

  # ノード（個人など）の基本スタイル
  ':node':
    shape: 'box'            # 四角形
    style: 'filled'         # 塗りつぶし
    fontname: 'Helvetica, Arial, sans-serif'
    fontcolor: '#ffffff'  # 文字色
    width: 0                # 自動サイズにする
    fillcolor: '#016d3e'
    color: '#ffffff'        # 枠線の色（薄いグレー）
    margin: 0               # 内側の余白なし

  # 全体グラフ（digraph）の設定
  ':digraph':
    rankdir: 'TB'           # 上から下に並べる（縦並び）
    ranksep: 0.4            # ランク間のスペース
    splines: 'ortho'        # 直角線のルーティング
    # bgcolor: '#016d3e80'
    bgcolor: transparent


  # 結婚やパートナーシップを示す結合点（ノード）用スタイル
  ':union':
    shape: 'circle'         # 円形
    style: 'filled'
    penwidth: 1             # 線の太さ
    color: 'white'          # 背景白
    label: ''               # ラベルなし
    height: 0.11
    width: 0.11
    fontname: 'Helvetica, Arial, sans-serif'
    fontsize: 9
    fontcolor: '#660000'    # 赤茶っぽい文字色（ただしラベルなしなので使われない）

  # 子供ノードへの結合点の記号（三角形）
  ':children':
    shape: triangle
    orientation: 90         # 下向き三角形
    style: 'filled'
    label: ''               # ラベルなし
    penwidth: 0             # 枠線なし
    height: 0.1
    width: 0.1

  # 親1のリンクスタイル（優先度高め）
  ':parent-link':
    weight: 2               # レイアウトの優先度（高くするとまっすぐにしやすい）

  # 親2のリンクスタイル（通常 dashed で表す）
  ':parent2-link':
    style: 'dashed'         # 破線
    penwidth: 0.25          # 線の細さ
    weight: 1               # 優先度低め

  # 親子間の連結線スタイル（中継ノードを通す）
  ':parent-child-link':
    weight: 3               # 強い優先度（直線的にしたい）

  # 子供への直接リンク
  ':child-link':
    dir: 'forward'          # 矢印あり
    arrowhead: 'tee'        # T字の矢印（Graphviz の tee 記号）
    arrowsize: 2            # 矢印のサイズ
    weight: 2
    tailport: se            # 親ノードの southeast から出る（位置指定）

  # サブ的な子供リンク（例：離婚した場合など）
  ':child2-link':
    style: 'dashed'
    penwidth: 0.25
    weight: 1
""")


def escape(s):
    # TODO: review this
    if type(s)==str:
        return '"'+s+'"'
    return s

def renderStyle(styles):
    return [
        f"{name}={escape(value)}"
        for name, value in styles.items()
        if value is not None
    ]

def combineStyles(tree, *classes, pre={}, post={}, **additional):
    result = ns(pre)
    for clss in classes:
        result.update(default_styles.get(clss, {}))
        result.update((tree.styles or {}).get(clss, {}))
    result.update(post)
    return result

def applyStyles(tree, *classes, pre={}, post={}, **additional):
    return renderStyle(
        combineStyles(tree, *classes, pre=pre, post=post, **additional)
    )

