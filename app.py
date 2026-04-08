import streamlit as st

# シーンデータ
scenes = [
    {
        "title": "登校中",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/School_route.jpg/640px-School_route.jpg",
        "audio_text": "カラスの鳴き声、遠くの車の音、靴の音がコツコツと響く。",
        "flavor": None,
        "description": "朝、みんなと同じように学校へ向かう。ランドセルが肩に食い込む重さ、風の冷たさ——体の感覚は同じだ。"
    },
    {
        "title": "教室",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/School_classroom.jpg/640px-School_classroom.jpg",
        "audio_text": "先生の声、教室のざわめき、チャイムの音。",
        "flavor": None,
        "description": "黒板の文字を追いながら、ノートをとる。授業中の空気、隣の友達の気配——ここにいる、ということは同じだ。"
    },
    {
        "title": "給食",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/School_lunch_Japan.jpg/640px-School_lunch_Japan.jpg",
        "audio_text": "スプーンが皿に当たる音、話し声、笑い声。",
        "flavor": "カレーの甘さとスパイス、噛んだときの野菜の感触……\nでも飲み込むと、喉を通るのは唾液だけ。",
        "description": "みんなが「おいしい！」と言っている。においはする。でも、口から食べることができない。チューブで栄養をとりながら、同じテーブルに座っている。"
    },
    {
        "title": "休み時間",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Kids_playing_in_the_schoolyard.jpg/640px-Kids_playing_in_the_schoolyard.jpg",
        "audio_text": "子どもたちの歓声、ボールを蹴る音、遠くのブランコの軋み。",
        "flavor": None,
        "description": "校庭を走り回る友達を眺めながら、日当たりのいいベンチに座る。体を動かせる日もあれば、そうでない日もある。"
    },
    {
        "title": "帰り道",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Autumn_school_road.jpg/640px-Autumn_school_road.jpg",
        "audio_text": "木の葉がざわめく音、自転車のベルの音、遠くの踏切。",
        "flavor": None,
        "description": "今日も一日が終わる。疲れた足を引きずりながら家へ向かう。空の色が夕焼けに染まっている。"
    },
    {
        "title": "夕食",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Japanese_family_dinner.jpg/640px-Japanese_family_dinner.jpg",
        "audio_text": "お箸の音、テレビの音、家族の話し声。",
        "flavor": "お味噌汁の湯気が鼻をくすぐる。豆腐のやわらかさ、だしのうまみ……\nでも今夜も、チューブの向こうに届く。",
        "description": "家族みんなで食卓を囲む。一緒にいること、話すこと——それは同じようにできる。"
    },
]

st.set_page_config(page_title="出腸口目シミュレーター", layout="centered")

st.title("出腸口目シミュレーター")
st.caption("経腸栄養（チューブ栄養）で生活する子どもの日常を、五感で体験するシミュレーターです。")

st.divider()

# セッションステートでインデックスを管理
if "scene_index" not in st.session_state:
    st.session_state.scene_index = 0

total = len(scenes)
index = st.session_state.scene_index
scene = scenes[index]

# シーン表示
st.subheader(f"シーン {index + 1} / {total}：{scene['title']}")
st.image(scene["image"], use_container_width=True)

st.markdown(scene["description"])

st.markdown(f"🔊 **[音]** {scene['audio_text']}")
if scene["flavor"]:
    st.markdown(f"👅 **[味覚]**\n\n{scene['flavor']}")

st.divider()

# ナビゲーションボタン
col_prev, col_next = st.columns(2)
with col_prev:
    if st.button("◀ 前のシーン", disabled=(index == 0), use_container_width=True):
        st.session_state.scene_index -= 1
        st.rerun()
with col_next:
    if st.button("次のシーン ▶", disabled=(index == total - 1), use_container_width=True):
        st.session_state.scene_index += 1
        st.rerun()

# プログレスバー
st.progress((index + 1) / total)
