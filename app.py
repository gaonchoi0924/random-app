def add_custom_devices(devices, power_rates):
    print("\n[추가 기기 등록] 기본 기기 외에 추가할 가전제품이 있나요?")
    
    # 몇 개를 추가할지 입력받아 for 반복문 실행
    count = int(input("추가할 기기 개수를 입력하세요 (없으면 0 입력): "))
    
    for i in range(count):
        name = input(f"  {i+1}번째 추가 기기 이름: ")
        watt = int(input(f"  '{name}'의 소비전력(W)을 입력하세요: "))
        
        # 리스트 함수 append()를 사용해 기존 리스트에 새 항목 추가
        devices.append(name)
        power_rates.append(watt)
        print(f"  -> '{name}({watt}W)' 등록 완료!\n")


# 2. 전체 전기 사용량을 계산하고 판별하는 def 함수 정의
def calculate_electricity(devices, power_rates):
    usage_list = []       # 기기별 계산된 전력량(Wh)을 담을 리스트
    formula_parts = []    # 계산식 문자열을 담을 리스트

    print("\n[사용 시간 입력]")
    # 기본 기기 + 추가된 기기까지 전체 리스트 길이만큼 for문 반복
    for i in range(len(devices)):
        hours = float(input(f"{devices[i]} 하루 사용 시간(시간)을 입력하세요: "))
        
        # 전력량(Wh) = 소비전력(W) × 사용시간(h)
        wh = power_rates[i] * hours
        usage_list.append(wh)
        formula_parts.append(f"{power_rates[i]}W×{hours}h")

    # 리스트 함수 sum()으로 총합 계산
    total_wh = sum(usage_list)
    total_kwh = total_wh / 1000

    # 계산식 및 총 사용량 출력
    formula_str = " + ".join(formula_parts)
    print("\n" + "=" * 50)
    print(f"[계산식] ({formula_str}) ÷ 1000")
    print(f"[총 전기 사용량] 하루 {total_kwh:.2f} kWh ({total_wh:.0f} Wh)")
    print("=" * 50)

    # if 조건문으로 평균 대비 사용량 평가
    if total_kwh <= 2.0:
        print("결과: 매우 훌륭합니다! 전기를 아주 아껴 쓰고 계시네요.")
    elif total_kwh <= 4.0:
        print("결과: 평균적인 수준으로 적당히 잘 사용하고 있습니다.")
    else:
        print("결과: 평균보다 사용량이 많습니다. 안 쓰는 기기의 전원을 꺼보세요!")


# --- 프로그램 실행 영역 ---

# 기본 기기 이름과 소비전력(W) 리스트
device_names = ["핸드폰 충전", "TV", "컴퓨터", "방 불(조명)"]
watts = [15, 150, 300, 40]

print("=== 나의 하루 전기 사용량 계산기 ===")

# 1단계: 사용자 기기 추가 함수 호출
add_custom_devices(device_names, watts)

# 2단계: 최종 리스트로 전기 사용량 계산 함수 호출
calculate_electricity(device_names, watts)
