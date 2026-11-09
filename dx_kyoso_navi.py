"""DX共創ナビ(モック)

既存のDX情報を「探す」から「つながり、試す」へ。
3本柱(01 情報を探す / 02 企業とつながる / 03 試す・判断する)と、
経産省・支援機関向けの集計画面を操作できる発表用モック。

実行方法:
    pip install streamlit pandas
    streamlit run dx_kyoso_navi.py

※ 企業・事例・相談先・数値はすべて架空です。
"""

import random

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# データ(すべて架空)
# ------------------------------------------------------------
FIELDS = [
    ("effect", "効果"), ("cond", "前提条件"), ("invest", "費用"), ("period", "期間"),
    ("team", "体制"), ("first", "最初の一歩"), ("fail", "つまずき"),
]
CASES = [
    dict(id="a", co="金属加工 A社", ind="製造業", size="51〜100名", pref="福岡県", src="DXセレクション",
         kind="取組事例", year=2025, title="熟練工の見積ノウハウをデータ化し、見積回答を3日から当日に",
         tags=["見積", "属人化", "リードタイム"], kpi_type="実績",
         effect="見積回答 3日→0.5日", cond="工程ごとの実績データを3か月ためた", invest="500〜2,000万円",
         period="約2年", team="兼任1名から開始", first="紙の作業日報をタブレット入力に替えた", fail=None,
         partner=True, url="DXセレクション2025 公表資料 p.12(架空)"),
    dict(id="b", co="板金 B社", ind="製造業", size="21〜50名", pref="大分県", src="DX認定",
         kind="戦略・体制", year=2025, title="単価表をクラウドで共有し、誰でも見積を出せる体制へ",
         tags=["見積", "属人化"], kpi_type="目標",
         effect="見積作成時間を40%削減(目標)", cond="品目ごとの単価表を整備", invest=None,
         period="3年計画", team="社長直轄・兼任1名", first=None, fail=None,
         partner=True, url="DX認定 公表情報(架空)"),
    dict(id="c", co="樹脂成形 C社", ind="製造業", size="21〜50名", pref="山口県", src="DX認定",
         kind="戦略・体制", year=2026, title="設備稼働の見える化で、段取り替えの時間を短縮",
         tags=["生産", "人手不足", "品質"], kpi_type="目標",
         effect="段取り時間を30%短縮(目標)", cond="古い設備に後付けセンサー", invest="100〜500万円",
         period=None, team="兼任1名", first=None, fail=None,
         partner=False, url="DX認定 公表情報(架空)"),
    dict(id="d", co="精密部品 D社", ind="製造業", size="101〜300名", pref="熊本県", src="DXセレクション",
         kind="取組事例", year=2026, title="受注データを統合し、見積と生産計画を連動",
         tags=["見積", "リードタイム", "生産"], kpi_type="実績",
         effect="納期遵守率 88%→97%", cond="受発注データの入力ルールを統一", invest=None,
         period="約3年", team="専任2名", first=None, fail="拠点ごとに形式が違い、統一に1年かかった",
         partner=True, url="DXセレクション2026 公表資料 p.30(架空)"),
    dict(id="e", co="食品製造 E社", ind="食料品製造業", size="51〜100名", pref="佐賀県", src="DXセレクション",
         kind="取組事例", year=2024, title="検査記録のクラウド化で、取引先への品質報告を自動化",
         tags=["品質", "事務"], kpi_type="実績",
         effect="報告書作成 月40時間→4時間", cond=None, invest=None, period=None, team=None,
         first="検査票1種類だけをタブレット化", fail=None,
         partner=False, url="DXセレクション2024 公表資料 p.8(架空)"),
]
CASE_BY_ID = {c["id"]: c for c in CASES}
KEYWORDS = [
    ("見積", "見積"), ("単価", "見積"), ("ベテラン", "属人化"), ("属人", "属人化"), ("あの人しか", "属人化"),
    ("遅", "リードタイム"), ("時間", "リードタイム"), ("人手", "人手不足"), ("人が足り", "人手不足"),
    ("不良", "品質"), ("品質", "品質"), ("段取り", "生産"), ("設備", "生産"), ("書類", "事務"), ("報告", "事務"),
]
ALL_TAGS = ["見積", "属人化", "リードタイム", "人手不足", "品質", "生産", "事務"]
INDUSTRIES = ["製造業", "食料品製造業", "建設業", "卸売業・小売業"]
SIZES = ["〜20名", "21〜50名", "51〜100名", "101〜300名", "301名〜"]
PEERS = [
    dict(id="p1", name="鋳造 F社", info="21〜50名・福岡県", note="見積の属人化を検討中。クラウド見積を比較している"),
    dict(id="p2", name="金型 G社", info="21〜50名・大分県", note="単価表の整備を試行中(2か月目)"),
]
VENDORS = [
    dict(id="v1", name="クラウド見積サービス X", note="月額制。単価表の取り込み支援あり"),
    dict(id="v2", name="生産管理ソフト Y", note="見積から工程管理までを一体で管理"),
    dict(id="v3", name="地元ITベンダー Z", note="既存の表計算を活かした小規模な改修"),
]
CONSULT_STEPS = ["申し込み", "支援機関が内容を確認", "日程の調整", "相談の実施"]
JOURNEY = [("compare", "事例を比較"), ("consult", "先行企業に相談"), ("match", "相手が決まる(マッチング)"),
           ("trial", "共同で試す"), ("decide", "判断する")]
STOP_REASONS = ["費用の見通しが立たない", "社内の人手が足りない", "効果が分からない", "必要な情報が足りない", "その他"]
GO_REASONS = ["効果が数字で確認できた", "先行企業の話で不安が減った", "補助金で費用の目処が立った", "その他"]
BASE_MISSING = {"費用": 18, "最初の一歩": 14, "期間": 11, "つまずき": 9, "体制": 7}
PAGES = ["01 情報を探す", "02 企業とつながる", "03 試す・判断する"]


# ------------------------------------------------------------
# 状態とロジック
# ------------------------------------------------------------
def init_state() -> None:
    order = [0, 1, 2]
    random.shuffle(order)
    defaults = dict(
        view="経営者の画面", page=PAGES[0],
        text="見積を出すのに時間がかかる。単価を判断できるのがベテラン1人だけで、その人が休むと止まってしまう。",
        tags=["見積", "属人化", "リードタイム"], ind="製造業", size="21〜50名", src="すべて",
        compare=["a", "b"], asks=[], partner=None, consult_step=-1, attend=True,
        trial=dict(goal="見積回答を3日以内→当日に", measure="見積1件あたりの作成時間(分)", period="2か月",
                   subsidy=True, saved=False),
        decision=None, reason="", memo="", consent=True, vendor_order=order,
        done=dict(compare=True, consult=False, match=False, trial=False, decide=False),
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def analyze(text: str) -> list[str]:
    found = []
    for word, tag in KEYWORDS:
        if word in text and tag not in found:
            found.append(tag)
    return found


def score(case: dict, s) -> tuple[int, list[str]]:
    overlap = [t for t in case["tags"] if t in s.tags]
    pts = min(45, len(overlap) * 18)
    if case["ind"] == s.ind:
        pts += 25
    elif "製造" in case["ind"] and "製造" in s.ind:
        pts += 10
    d = abs(SIZES.index(case["size"]) - SIZES.index(s.size))
    pts += 25 if d == 0 else 12 if d == 1 else 0
    return min(99, pts), overlap


def next_step() -> str | None:
    for key, _ in JOURNEY:
        if not st.session_state.done[key]:
            return key
    return None


def partner_name(pid: str | None) -> str:
    if pid is None:
        return ""
    if pid in CASE_BY_ID:
        return CASE_BY_ID[pid]["co"]
    for p in PEERS + VENDORS:
        if p["id"] == pid:
            return p["name"]
    return ""


def go(page: str) -> None:
    st.session_state.page = page
    st.session_state.view = "経営者の画面"


def toggle_ask(cid: str, label: str) -> None:
    key = f"{cid}:{label}"
    asks = st.session_state.asks
    hit = [a for a in asks if a["key"] == key]
    if hit:
        asks.remove(hit[0])
    else:
        asks.append(dict(key=key, label=label, text=f"{CASE_BY_ID[cid]['co']}の「{label}」を教えてください"))
        st.toast("相談リストに追加しました")


def toggle_compare(cid: str) -> None:
    sel = st.session_state.compare
    if st.session_state[f"cmp_{cid}"]:
        if len(sel) >= 3:
            st.session_state[f"cmp_{cid}"] = False
            st.toast("比較できるのは3件までです")
            return
        sel.append(cid)
    elif cid in sel:
        sel.remove(cid)
    if len(sel) >= 2:
        st.session_state.done["compare"] = True


def choose_partner(pid: str) -> None:
    st.session_state.partner = pid
    st.session_state.done["match"] = True
    st.toast("相談相手を選びました")


# ------------------------------------------------------------
# 01 情報を探す
# ------------------------------------------------------------
def page_find() -> None:
    s = st.session_state
    st.caption("01|情報の中身を整える")
    st.header("困りごとから、近い会社の事例を探す")
    st.write("DX認定の公表情報(戦略・体制)とDXセレクションの取組事例を、性質を分けて表示します。"
             "公開資料にない項目は推測で埋めず、「記載なし」と示します。")

    st.subheader("いま困っていること")
    s.text = st.text_area("困りごと", value=s.text, label_visibility="collapsed")
    if st.button("AIで整理する", type="primary"):
        tags = analyze(s.text)
        if tags:
            s.tags = tags
            st.session_state["tags_widget"] = tags
            st.toast("課題を整理しました")
        else:
            st.toast("分類できる言葉が見つかりませんでした。課題を選んでください")
    st.session_state.setdefault("tags_widget", s.tags)
    s.tags = st.multiselect("AIの読み取り(違っていれば直してください)", ALL_TAGS, key="tags_widget")

    c1, c2, c3 = st.columns(3)
    s.ind = c1.selectbox("業種", INDUSTRIES, index=INDUSTRIES.index(s.ind))
    s.size = c2.selectbox("従業員規模", SIZES, index=SIZES.index(s.size))
    srcs = ["すべて", "DXセレクション", "DX認定"]
    s.src = c3.selectbox("情報の出典", srcs, index=srcs.index(s.src))

    rows = [c for c in CASES if s.src == "すべて" or c["src"] == s.src]
    ranked = sorted(((c, *score(c, s)) for c in rows), key=lambda x: -x[1])
    st.subheader(f"近い順の事例({len(ranked)}件)")
    for case, sc, overlap in ranked:
        with st.container(border=True):
            left, right = st.columns([1, 7])
            left.metric("適合度", sc)
            with right:
                st.caption(f"【{case['kind']}】{case['src']} {case['year']}|{case['co']}|"
                           f"{case['ind']}・{case['size']}・{case['pref']}")
                st.markdown(f"**{case['title']}**")
                if overlap:
                    st.caption("一致した課題:" + "・".join(overlap))
            cols = st.columns(4)
            for i, (k, label) in enumerate(FIELDS):
                with cols[i % 4]:
                    if case[k]:
                        name = f"{label}({case['kpi_type']})" if k == "effect" else label
                        st.markdown(f"<small>{name}</small><br>**{case[k]}**", unsafe_allow_html=True)
                    else:
                        added = any(a["key"] == f"{case['id']}:{label}" for a in s.asks)
                        st.markdown(f"<small>{label}</small><br>:orange[記載なし]", unsafe_allow_html=True)
                        st.button("追加済み(外す)" if added else "相談で確かめる",
                                  key=f"ask_{case['id']}_{k}", on_click=toggle_ask, args=(case["id"], label))
            f1, f2 = st.columns([3, 1])
            f1.caption(f"出典:{case['url']}")
            st.session_state.setdefault(f"cmp_{case['id']}", case["id"] in s.compare)
            f2.checkbox("比較に追加", key=f"cmp_{case['id']}", on_change=toggle_compare, args=(case["id"],))

    st.subheader("比較")
    sel = [CASE_BY_ID[i] for i in s.compare]
    if len(sel) >= 2:
        df = pd.DataFrame({f"{c['co']}({c['kind']})": {label: (c[k] or "記載なし") for k, label in FIELDS}
                           for c in sel})
        st.dataframe(df, width="stretch")
    else:
        st.info("事例を2件以上「比較に追加」すると、ここに並びます。")
    st.button("足りない情報を相談する(02へ)→", type="primary", on_click=go, args=(PAGES[1],))


# ------------------------------------------------------------
# 02 企業とつながる
# ------------------------------------------------------------
def person_card(col, pid: str, kind: str, name: str, info: str, note: str) -> None:
    selected = st.session_state.partner == pid
    with col.container(border=True):
        st.caption(kind)
        st.markdown(f"**{name}**")
        st.caption(info)
        st.write(note)
        st.button("相談相手に選択中" if selected else "この相手に相談する", key=f"partner_{pid}",
                  type="primary" if selected else "secondary", on_click=choose_partner, args=(pid,),
                  width="stretch")


def page_connect() -> None:
    s = st.session_state
    st.caption("02|企業同士をつなぐ")
    st.header("先行企業や同じ課題の会社に、支援機関の仲立ちで相談する")
    st.write("このナビは、取引先の信用金庫(架空)から紹介されました。相談の申し込みは紹介元の担当者が受け取り、"
             "日程調整と当日の同席を行います。")

    st.subheader("相談できる相手")
    people = [(c["id"], "先行企業", c["co"], f"{c['ind']}・{c['size']}・{c['pref']}|{c['kind']}", c["title"])
              for c in CASES if c["partner"]]
    people += [(p["id"], "同じ課題の企業", p["name"], p["info"], p["note"]) for p in PEERS]
    cols = st.columns(3)
    for i, args in enumerate(people):
        person_card(cols[i % 3], *args)

    st.markdown("**DX支援企業**(表示順は毎回入れ替わります)")
    cols = st.columns(3)
    for col, idx in zip(cols, s.vendor_order):
        v = VENDORS[idx]
        person_card(col, v["id"], "DX支援企業", v["name"], "支援企業", v["note"])
    st.warning("中立性のルール:支援企業は必ず複数社を表示し、特定の会社を推薦しません。"
               "相談で知った連絡先への営業目的の連絡は禁止です。")

    st.subheader("相談の内容")
    c1, c2 = st.columns(2)
    c1.text_input("相談相手", value=partner_name(s.partner) or "上の一覧から選んでください", disabled=True)
    c2.text_input("紹介元の担当者", value="取引先の信用金庫 法人営業担当(架空)", disabled=True)
    if s.asks:
        for i, a in enumerate(list(s.asks)):
            q1, q2 = st.columns([6, 1])
            q1.write(f"・{a['text']}")
            if q2.button("外す", key=f"delq_{a['key']}"):
                s.asks.pop(i)
                st.rerun()
    else:
        st.info("01の事例で「相談で確かめる」を押すと、質問がここに入ります。")
    n1, n2 = st.columns([5, 1])
    newq = n1.text_input("質問を追加", placeholder="例:社内の反対はどう乗り越えましたか", label_visibility="collapsed")
    if n2.button("追加"):
        if newq.strip():
            s.asks.append(dict(key=f"free:{len(s.asks)}:{newq}", label="その他", text=newq.strip()))
            st.rerun()
        else:
            st.toast("質問を入力してください")
    s.attend = st.checkbox("支援機関の担当者に同席してもらう", value=s.attend)
    st.caption("取引先名・価格など機密にあたる情報は、相談の場で話す範囲を事前に決めておきましょう。")
    if st.button("申し込み済み" if s.consult_step >= 0 else "支援機関に申し込む", type="primary",
                 disabled=s.partner is None or s.consult_step >= 0):
        s.consult_step = 0
        st.toast("紹介元の信用金庫に申し込みました")
        st.rerun()

    st.subheader("相談の進み具合")
    if s.consult_step < 0:
        st.info("まだ申し込んでいません。")
        return
    cols = st.columns(4)
    for i, (col, name) in enumerate(zip(cols, CONSULT_STEPS)):
        if i < s.consult_step:
            col.success(f"{i + 1}. {name}")
        elif i == s.consult_step:
            col.warning(f"{i + 1}. {name}")
        else:
            col.info(f"{i + 1}. {name}")
    if s.consult_step < 3:
        if st.button("次の段階へ進める(デモ)"):
            s.consult_step += 1
            if s.consult_step == 3:
                s.done["consult"] = True
                st.toast("相談を実施しました")
            st.rerun()
    else:
        st.button("共同で試す(03へ)→", type="primary", on_click=go, args=(PAGES[2],))


# ------------------------------------------------------------
# 03 試す・判断する
# ------------------------------------------------------------
def page_act() -> None:
    s = st.session_state
    st.caption("03|届けた成果を測る")
    st.header("小さく試して、導入するか判断する")
    st.write("試す前に「期待する成果」と「測り方」を決めておくと、判断がしやすくなります。見送りも立派な判断として記録します。")

    st.subheader("共同で試す計画")
    t = s.trial
    c1, c2, c3 = st.columns(3)
    goal = c1.text_input("期待する成果", value=t["goal"])
    measure = c2.text_input("測り方", value=t["measure"])
    periods = ["1か月", "2か月", "3か月"]
    period = c3.selectbox("試す期間", periods, index=periods.index(t["period"]))
    subsidy = st.checkbox("使える補助金(デジタル化・AI導入補助金など)を支援機関に確認する", value=t["subsidy"])
    if st.button("計画を更新する" if t["saved"] else "この計画で試す", type="primary"):
        s.trial = dict(goal=goal, measure=measure, period=period, subsidy=subsidy, saved=True)
        s.done["trial"] = True
        st.toast("試行の計画を記録しました")
        st.rerun()

    st.subheader("判断する")
    options = ["導入する", "追加で試す", "見送る"]
    decision = st.radio("判断", options, horizontal=True, label_visibility="collapsed",
                        index=options.index(s.decision) if s.decision in options else None,
                        captions=["本格的に入れる", "条件を変えてもう一度", "今回はやめておく"])
    reasons = GO_REASONS if decision == "導入する" else STOP_REASONS
    label = "決め手になったこと" if decision == "導入する" else "止まった理由・迷っている理由"
    reason = st.selectbox(label, reasons, index=reasons.index(s.reason) if s.reason in reasons else None,
                          placeholder="選んでください")
    memo = st.text_area("メモ(任意)", value=s.memo,
                        placeholder="例:作成時間は半分になったが、単価表の更新を誰がやるかが決まっていない")
    if st.button("判断を記録する", type="primary", disabled=decision is None):
        s.decision, s.reason, s.memo = decision, reason or "", memo
        s.done["decide"] = True
        st.toast(f"「{decision}」を記録しました")
        st.rerun()

    st.subheader("行動データの提供")
    consent = st.checkbox("比較・相談・試行・判断の記録を、匿名で集計に使うことに同意する", value=s.consent)
    if consent != s.consent:
        s.consent = consent
        st.toast("集計への提供に同意しました" if consent else "同意を取り消しました。記録は集計に含めません")
    st.caption("会社名や相談内容は集計に含めません。同意はいつでも取り消せます。集計結果は、事例の内容や支援策の改善に使われます。")

    st.subheader("これまでの記録")
    nxt = next_step()
    for i, (key, name) in enumerate(JOURNEY, 1):
        if s.done[key]:
            st.markdown(f":green[✓] **{name}**  \n<small>記録済み</small>", unsafe_allow_html=True)
        elif key == nxt:
            st.markdown(f":orange[{i}] **{name}**  \n<small>次のステップ</small>", unsafe_allow_html=True)
        else:
            st.markdown(f":gray[{i}] {name}  \n<small>未着手</small>", unsafe_allow_html=True)


# ------------------------------------------------------------
# 経産省・支援機関の画面
# ------------------------------------------------------------
def page_gov() -> None:
    s = st.session_state
    st.caption("03|届けた成果を測る(行政・支援機関向け)")
    st.header("どこで検討が止まり、どの情報が足りないか")
    st.write("初期実証の2グループを比べる集計画面のイメージです。同意を得た企業の行動だけを、匿名で集計します。"
             "**数値はすべて架空のサンプルです。**")

    k1, k2, k3 = st.columns(3)
    k1.metric("相談に進んだ割合(検索+交流)", "67%", "検索のみ 27%より +40pt")
    k2.metric("試行に進んだ割合(検索+交流)", "40%", "検索のみ 13%より +27pt")
    k3.metric("判断(導入・追加試行・見送り)まで", "5社", "うち見送り 2社", delta_color="off")

    st.subheader("段階ごとの到達社数(各グループ15社)")
    stages = ["1 比較", "2 相談", "3 試行", "4 判断"]
    funnel = pd.DataFrame({"事例検索のみ": [12, 4, 2, 2], "検索+交流支援": [13, 10, 6, 5]}, index=stages)
    st.bar_chart(funnel, stack=False, color=["#8a96a0", "#087f84"], y_label="社数")
    st.caption("差が開くのは「相談」の段階です。少数の結果なので一般化はせず、対象や機能の見直しに使います。")

    st.subheader("試行・判断の前で止まった理由(検索+交流支援)")
    stall = pd.DataFrame({"社数": [5, 4, 3, 2]},
                         index=["費用の見通しが立たない", "社内の人手が足りない", "効果が分からない", "必要な情報が足りない"])
    st.bar_chart(stall, horizontal=True, color="#15324d")

    st.subheader("「記載なし」で相談に回された項目")
    from_cases = [a for a in s.asks if a["label"] != "その他"]
    added = {}
    for a in from_cases:
        added[a["label"]] = added.get(a["label"], 0) + 1
    labels = sorted(set(BASE_MISSING) | set(added), key=lambda l: -(BASE_MISSING.get(l, 0) + added.get(l, 0)))
    missing = pd.DataFrame({"これまでの集計": [BASE_MISSING.get(l, 0) for l in labels],
                            "今回の操作": [added.get(l, 0) for l in labels]}, index=labels)
    st.bar_chart(missing, horizontal=True, color=["#15324d", "#e0a400"])
    if from_cases:
        st.caption(f"経営者の画面で「相談で確かめる」を押した{len(from_cases)}件が「今回の操作」として反映されています。")
    else:
        st.caption("経営者の画面で「相談で確かめる」を押すと、この集計に反映されます。")
    st.caption("上位の項目は、次年度のDXセレクション応募様式で記入必須にする根拠になります。")

    st.subheader("サンプル精工(架空)の状況")
    nxt = next_step()
    if not s.consent:
        st.write("同意なし(集計に含めない)")
    elif nxt is None:
        st.write("現在地:**判断まで完了**")
    else:
        st.write(f"現在地:**{dict(JOURNEY)[nxt]}の手前**")


# ------------------------------------------------------------
# メイン
# ------------------------------------------------------------
def sidebar() -> None:
    s = st.session_state
    with st.sidebar:
        st.title("DX共創ナビ")
        st.caption("「探す」から「つながり、試す」へ")
        st.radio("画面", ["経営者の画面", "経産省・支援機関の画面"], key="view")
        st.divider()
        if s.view == "経営者の画面":
            st.radio("3本柱", PAGES, key="page")
            st.caption("紹介元:取引先の信用金庫(架空)")
            st.caption("株式会社サンプル精工|代表取締役")
            st.divider()
            st.markdown("**あなたの進み具合**")
            nxt = next_step()
            for key, name in JOURNEY:
                mark = ":green[●]" if s.done[key] else ":orange[●]" if key == nxt else ":gray[●]"
                st.markdown(f"{mark} {name}")
            st.markdown("**相談リスト**")
            if s.asks:
                for a in s.asks[:5]:
                    st.caption("・" + a["text"])
            else:
                st.caption("「記載なし」の項目から追加できます。")
        else:
            st.caption("運営:経産省・IPA(案)")
            st.markdown("**連携先**")
            st.caption("・信用金庫・商工会議所(紹介と同席)\n\n・よろず支援拠点\n\n・デジタル化・AI導入補助金")
        st.divider()
        st.caption("**モック**|企業・事例・相談先・数値はすべて架空です。")


def main() -> None:
    st.set_page_config(page_title="DX共創ナビ", layout="wide")
    init_state()
    sidebar()
    if st.session_state.view == "経産省・支援機関の画面":
        page_gov()
    else:
        {PAGES[0]: page_find, PAGES[1]: page_connect, PAGES[2]: page_act}[st.session_state.page]()


if __name__ == "__main__":
    main()
