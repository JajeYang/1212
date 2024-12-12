import streamlit as st
import tempfile
import subprocess
import os
import json


RANKING_FILE = 'ranking.json'


def load_rankings():
    """랭킹 데이터를 파일에서 불러옵니다."""
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_rankings(rankings):
    """랭킹 데이터를 파일에 저장합니다."""
    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(rankings, f, ensure_ascii=False, indent=4)


def get_pylint_score(code: str) -> float:
    """
    주어진 파이썬 코드를 파일로 저장한 후 pylint를 실행하여 점수를 반환합니다.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        # pylint를 실행하고 결과를 캡처합니다.
        result = subprocess.run(
            ['pylint', temp_path, '--score=y'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # pylint 점수를 파싱합니다.
        for line in result.stdout.split('\n'):
            if line.startswith("Your code has been rated at"):
                score_str = line.split(" ")[6]
                score = float(score_str.split('/')[0])
                return score
        return 0.0
    except Exception as e:
        st.error(f"Pylint 실행 중 오류 발생: {e}")
        return 0.0
    finally:
        os.remove(temp_path)


def update_rankings(rankings, developer, score):
    """개발자의 점수를 랭킹에 갱신합니다."""
    rankings[developer] = score
    return rankings


def display_rankings(rankings):
    """현재 랭킹을 표시합니다."""
    if not rankings:
        st.info("랭킹 데이터가 없습니다.")
        return

    st.markdown("---")
    st.header("현재 랭킹 🏆")

    # 랭킹을 점수 기준으로 정렬
    sorted_rankings = sorted(rankings.items(), key=lambda x: x[1], reverse=True)

    for idx, (dev, score) in enumerate(sorted_rankings, start=1):
        st.write(f"{idx}. **{dev}** - **{score:.2f}/10**")


def main():
    st.title("개발자 전투력 측정기 🥊")

    st.markdown("""
    두 개발자의 파이썬 코드를 입력하고 **Pylint** 점수를 기준으로 우승자를 가리며, 점수를 통해 랭킹을 확인할 수 있습니다.
    """)

    # 랭킹 데이터 불러오기
    rankings = load_rankings()

    # 개발자 이름 입력
    col_names = st.columns(2)
    with col_names[0]:
        dev_a = st.text_input("개발자 A의 이름", value="Developer A", key="dev_a")
    with col_names[1]:
        dev_b = st.text_input("개발자 B의 이름", value="Developer B", key="dev_b")

    # 코드 입력
    col1, col2 = st.columns(2)

    with col1:
        st.header(f"{dev_a}의 코드")
        code_a = st.text_area("코드 입력", height=300, key="code_a")

    with col2:
        st.header(f"{dev_b}의 코드")
        code_b = st.text_area("코드 입력", height=300, key="code_b")

    if st.button("전투 시작! 🥇"):
        if not code_a.strip() and not code_b.strip():
            st.warning("두 개발자의 코드 중 적어도 하나를 입력해주세요.")
            return

        st.markdown("---")
        st.header("전투 결과")

        score_a = None
        score_b = None
        review_a = ""
        review_b = ""

        if code_a.strip():
            score_a = get_pylint_score(code_a)
            st.subheader(f"{dev_a}의 점수: {score_a:.2f}/10")
            rankings = update_rankings(rankings, dev_a, score_a)
        else:
            st.subheader(f"{dev_a}의 코드가 입력되지 않았습니다.")

        if code_b.strip():
            score_b = get_pylint_score(code_b)
            st.subheader(f"{dev_b}의 점수: {score_b:.2f}/10")
            rankings = update_rankings(rankings, dev_b, score_b)
        else:
            st.subheader(f"{dev_b}의 코드가 입력되지 않았습니다.")

        # 우승자 결정
        if score_a is not None and score_b is not None:
            if score_a > score_b:
                st.success(f"🥇 {dev_a}(이)가 우승했습니다!")
            elif score_b > score_a:
                st.success(f"🥇 {dev_b}(이)가 우승했습니다!")
            else:
                st.info("무승부입니다!")
        elif score_a is not None:
            st.success(f"{dev_a}만 코드가 제출되어 자동으로 우승합니다!")
        elif score_b is not None:
            st.success(f"{dev_b}만 코드가 제출되어 자동으로 우승합니다!")

        # 랭킹 저장
        save_rankings(rankings)

        # 코드 리뷰 표시
        st.markdown("### 전문적인 코드 리뷰(유료)")
        if review_a:
            st.markdown(f"**{dev_a}의 코드 리뷰:**\n\n{review_a}")
        if review_b:
            st.markdown(f"**{dev_b}의 코드 리뷰:**\n\n{review_b}")

        # 현재 랭킹 표시
        display_rankings(rankings)


if __name__ == "__main__":
    main()
