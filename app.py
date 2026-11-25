import streamlit as st

# 1. 계산 기능을 담당하는 def 함수 정의
def calculate_electricity(devices, power_rates, hours_list):
    usage_list = []       # 기기별 계산된 전력량(Wh)을 담을 리스트
    formula_parts = []    # 계산식 문자열을 담을 리스트

    # 2. for 반복문을 사용해 각 기기의 전력량 계산
    for i in range(len(devices)):
        wh = power_rates[i] * hours_list[i]
        usage_list.append(wh)  # 리스트 함수 append()
        formula_parts.append(f"{power_rates[i]}W×{hours_list[i]}h")

    # 리스트 함수 sum()으로 총 사용량 계산
    total_wh = sum(usage_list)
    total_kwh = total_wh / 1000

    # 스트림릿 화면에 계산식 및 결과 출력 (print 대신 st.write / st.info 사용)
    formula_str = " + ".join(formula_parts)
    st.divider()
    st.subheader("📊 계산 결과")
    st.write(f"**[계산식]** `({formula_str}) ÷ 1000`")
    st.info(f"**[총 전기 사용량]** 하루 **{total_kwh:.2f} kWh** ({total_wh:.0f} Wh)")

    # 3. if 조건문으로 평균 대비 사용량 평가
    if total_kwh <= 2.0:
        st.success("결과: 매우 훌륭합니다! 전기를 아주 아껴 쓰고 계시네요.")
    elif total_kwh <= 4.0:
        st.warning("결과: 평균적인 수준으로 적당히 잘 사용하고 있습니다.")
    else:
        st.error("결과: 평균보다 사용량이 많습니다. 안 쓰는 기기의 전원을 꺼보세요!")


# --- 스트림릿 화면 구성 영역 ---
st.title("⚡ 나의 하루 전기 사용량 계산기")

# 기본 기기 리스트
device_names = ["핸드폰 충전", "TV", "컴퓨터", "방 불(조명)"]
watts = [15, 150, 300, 40]

# 추가 기기 입력 섹션
st.subheader("1. 추가 기기 등록")
add_count = st.number_input("추가할 기기 개수 (없으면 0)", min_value=0, max_value=10, value=0, step=1)

for i in range(int(add_count)):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(f"추가 기기 {i+1} 이름", key=f"name_{i}")
    with col2:
        watt = st.number_input(f"추가 기기 {i+1} 소비전력(W)", min_value=0, value=100, step=10, key=f"watt_{i}")
    
    # 이름이 입력되었을 때만 리스트에 추가
    if name:
        device_names.append(name)
        watts.append(watt)

# 사용 시간 입력 섹션
st.subheader("2. 하루 사용 시간(시간) 입력")
hours_input_list = []

for i in range(len(device_names)):
    h = st.number_input(
        f"{device_names[i]} ({watts[i]}W) 사용 시간", 
        min_value=0.0, max_value=24.0, value=0.0, step=0.5, 
        key=f"hour_{i}"
    )
    hours_input_list.append(h)

# 계산 버튼 클릭 시 def 함수 실행
if st.button("전기 사용량 계산하기", type="primary"):
    calculate_electricity(device_names, watts, hours_input_list)
