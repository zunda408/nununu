import streamlit as st

# シーンデータ
scenes = [
    {
        "title": "登校中",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/School_route.jpg/640px-School_route.jpg",
        "audio_text": "カラスの鳴き声、遠くの車の音、靴の音がコツコツと響く。",
        "flavor": None
    },
    {
        "title": "教室",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/School_classroom.jpg/640px-School_classroom.jpg",
        "audio_text": "先生の声、教室のざわめき、チャイムの音。",
        "flavor": None
    },
    {
        "title": "給食",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/School_lunch_Japan.jpg/640px-School_lunch_Japan.jpg",
        "audio_text": "スプーンが皿に当たる音、話し声、笑い声。",
        "flavor": "カレーの甘さとスパイス、噛んだときの野菜の感触……\nでも飲み込むと、喉を通るのは唾液だけ。"
    }
]

st.title("出ちょう口目シミュレーター")

index = st.number_input("シーンを選んでください (0〜2)", 0, len(scenes)-1, 0)

scene = scenes[index]
st.subheader(scene["title"])
st.image(scene["image"], use_column_width=True)
st.markdown(f"**[音]**\n{scene['audio_text']}")
if scene["flavor"]:
    st.markdown(f"**[味覚]**\n{scene['flavor']}")
