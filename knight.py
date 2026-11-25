Python
import pygame
import random
import math
import sys

# 초기화
pygame.init()

# 화면 설정
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DELTARUNE - THE ROARING KNIGHT (Fan Mini-Game)")
clock = pygame.time.Clock()

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (160, 32, 240)
DARK_PURPLE = (60, 0, 100)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)

# 폰트 설정
font_main = pygame.font.SysFont("malgungothic", 20, bold=True)
font_small = pygame.font.SysFont("malgungothic", 15)
font_title = pygame.font.SysFont("arial", 28, bold=True)

# 게임 상태
STATE_PLAYER_TURN = 0
STATE_ATTACK_BAR = 1
STATE_ENEMY_TURN = 2
STATE_GAME_OVER = 3
STATE_VICTORY = 4

# 플레이어(영혼) 설정
soul_size = 14
soul_x = WIDTH // 2
soul_y = 320
soul_speed = 4
player_hp = 90
player_max_hp = 90
tp = 0  # Tension Points (0 ~ 100)

# 보스(나이트) 설정
boss_hp = 500
boss_max_hp = 500
boss_name = "ROARING KNIGHT"

# 전투 박스 설정
box_width, box_height = 180, 140
box_x = WIDTH // 2 - box_width // 2
box_y = 240

# 메뉴 및 공격 게이지 설정
menu_options = ["FIGHT", "ACT", "ITEM", "DEFEND"]
selected_menu = 0
attack_bar_x = 120
attack_bar_speed = 7
message_text = "* 어둠의 기사가 앞을 가로막았다!"

# 탄막 리스트
bullets = []
enemy_turn_timer = 0
attack_pattern = 0


def draw_heart(surface, x, y, color=RED):
    """픽셀 느낌의 하트 그리기"""
    pts = [
        (x, y - 4), (x - 4, y - 8), (x - 8, y - 4),
        (x - 8, y + 1), (x, y + 8), (x + 8, y + 1),
        (x + 8, y - 4), (x + 4, y - 8)
    ]
    pygame.draw.polygon(surface, color, pts)


def draw_knight(surface, x, y, tick):
    """나이트(보스) 스프라이트 도형으로 그리기"""
    float_y = y + math.sin(tick * 0.05) * 6  # 둥실둥실 떠다니는 연출

    # 망토 (어두운 보라색)
    pygame.draw.polygon(surface, DARK_PURPLE, [
        (x, float_y - 30), (x - 45, float_y + 50), (x + 45, float_y + 50)
    ])
    # 갑옷 몸통
    pygame.draw.polygon(surface, WHITE, [
        (x, float_y - 35), (x - 22, float_y + 10), (x, float_y + 35), (x + 22, float_y + 10)
    ])
    # 투구 및 뿔
    pygame.draw.circle(surface, BLACK, (x, int(float_y - 42)), 14)
    pygame.draw.polygon(surface, WHITE, [(x - 10, float_y - 48), (x - 25, float_y - 75), (x - 4, float_y - 52)])
    pygame.draw.polygon(surface, WHITE, [(x + 10, float_y - 48), (x + 25, float_y - 75), (x + 4, float_y - 52)])
    # 빛나는 바이저(눈)
    pygame.draw.line(surface, CYAN, (x - 8, float_y - 42), (x + 8, float_y - 42), 3)
    # 대검 (Dark Blade)
    sword_offset = math.cos(tick * 0.05) * 4
    pygame.draw.polygon(surface, CYAN, [
        (x + 35, float_y - 20 + sword_offset),
        (x + 42, float_y - 20 + sword_offset),
        (x + 38, float_y + 60 + sword_offset)
    ])


def spawn_bullets(pattern, timer):
    """나이트의 탄막 패턴 생성"""
    if pattern == 0:
        # 패턴 1: 위에서 떨어지는 어둠의 칼날 비
        if timer % 15 == 0:
            bx = random.randint(box_x + 10, box_x + box_width - 10)
            bullets.append({"x": bx, "y": box_y - 20, "vx": 0, "vy": 3.5, "w": 6, "h": 18, "color": WHITE})
    elif pattern == 1:
        # 패턴 2: 양옆에서 교차로 날아오는 횡베기
        if timer % 25 == 0:
            side = random.choice([-1, 1])
            bx = box_x - 20 if side == 1 else box_x + box_width + 20
            by = random.randint(box_y + 15, box_y + box_height - 15)
            bullets.append({"x": bx, "y": by, "vx": side * 4, "vy": 0, "w": 22, "h": 5, "color": CYAN})
    elif pattern == 2:
        # 패턴 3: 중앙을 향해 조여오는 원형 검기
        if timer % 35 == 0:
            angle = random.uniform(0, math.pi * 2)
            dist = 130
            bx = (box_x + box_width // 2) + math.cos(angle) * dist
            by = (box_y + box_height // 2) + math.sin(angle) * dist
            vx = -math.cos(angle) * 2.8
            vy = -math.sin(angle) * 2.8
            bullets.append({"x": bx, "y": by, "vx": vx, "vy": vy, "w": 10, "h": 10, "color": PURPLE})


# 메인 게임 루프
state = STATE_PLAYER_TURN
tick = 0
invincible_timer = 0

while True:
    tick += 1
    screen.fill(BLACK)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # 1. 플레이어 메뉴 선택 턴
            if state == STATE_PLAYER_TURN:
                if event.key == pygame.K_LEFT:
                    selected_menu = (selected_menu - 1) % len(menu_options)
                elif event.key == pygame.K_RIGHT:
                    selected_menu = (selected_menu + 1) % len(menu_options)
                elif event.key in (pygame.K_z, pygame.K_RETURN):
                    choice = menu_options[selected_menu]
                    if choice == "FIGHT":
                        state = STATE_ATTACK_BAR
                        attack_bar_x = 120
                    elif choice == "ACT":
                        if tp >= 25:
                            tp -= 25
                            player_hp = min(player_max_hp, player_hp + 30)
                            message_text = "* 영혼의 빛으로 HP를 30 회복했다! (TP -25%)"
                        else:
                            message_text = "* 나이트의 갑옷은 차가운 어둠으로 덮여있다. (회복은 TP 25% 필요)"
                        state = STATE_ENEMY_TURN
                        enemy_turn_timer = 240
                        attack_pattern = random.randint(0, 2)
                        soul_x, soul_y = box_x + box_width // 2, box_y + box_height // 2
                    elif choice == "ITEM":
                        player_hp = min(player_max_hp, player_hp + 40)
                        message_text = "* 다크버거를 먹었다! HP가 40 회복되었다."
                        state = STATE_ENEMY_TURN
                        enemy_turn_timer = 240
                        attack_pattern = random.randint(0, 2)
                        soul_x, soul_y = box_x + box_width // 2, box_y + box_height // 2
                    elif choice == "DEFEND":
                        tp = min(100, tp + 20)
                        message_text = "* 방어 태세를 취했다! TP가 20% 올랐다."
                        state = STATE_ENEMY_TURN
                        enemy_turn_timer = 240
                        attack_pattern = random.randint(0, 2)
                        soul_x, soul_y = box_x + box_width // 2, box_y + box_height // 2

            # 2. 공격 타이밍 게이지 턴
            elif state == STATE_ATTACK_BAR:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    # 중앙(320)에 가까울수록 높은 데미지
                    dist = abs(320 - attack_bar_x)
                    damage = max(20, int(120 - dist * 0.6))
                    boss_hp -= damage
                    tp = min(100, tp + 10)
                    if boss_hp <= 0:
                        boss_hp = 0
                        state = STATE_VICTORY
                    else:
                        message_text = f"* 나이트에게 {damage}의 데미지를 입혔다!"
                        state = STATE_ENEMY_TURN
                        enemy_turn_timer = 260
                        attack_pattern = random.randint(0, 2)
                        soul_x, soul_y = box_x + box_width // 2, box_y + box_height // 2

            # 게임 오버 / 승리 시 재시작
            elif state in (STATE_GAME_OVER, STATE_VICTORY):
                if event.key == pygame.K_r:
                    player_hp = player_max_hp
                    boss_hp = boss_max_hp
                    tp = 0
                    bullets.clear()
                    state = STATE_PLAYER_TURN
                    message_text = "* 어둠의 기사가 다시 나타났다!"

    # --- 상태별 업데이트 ---
    if state == STATE_ATTACK_BAR:
        attack_bar_x += attack_bar_speed
        if attack_bar_x > 520:
            message_text = "* 공격이 빗나갔다!"
            state = STATE_ENEMY_TURN
            enemy_turn_timer = 240
            attack_pattern = random.randint(0, 2)
            soul_x, soul_y = box_x + box_width // 2, box_y + box_height // 2

    elif state == STATE_ENEMY_TURN:
        enemy_turn_timer -= 1
        if invincible_timer > 0:
            invincible_timer -= 1

        # 플레이어 이동 (Shift 누르면 저속 이동)
        keys = pygame.key.get_pressed()
        current_speed = soul_speed * 0.5 if (keys[pygame.K_LSHIFT] or keys[pygame.K_x]) else soul_speed
        if keys[pygame.K_LEFT]:
            soul_x -= current_speed
        if keys[pygame.K_RIGHT]:
            soul_x += current_speed
        if keys[pygame.K_UP]:
            soul_y -= current_speed
        if keys[pygame.K_DOWN]:
            soul_y += current_speed

        # 전투 박스 경계 제한
        soul_x = max(box_x + 10, min(box_x + box_width - 10, soul_x))
        soul_y = max(box_y + 10, min(box_y + box_height - 10, soul_y))

        # 탄막 생성 및 이동
        spawn_bullets(attack_pattern, enemy_turn_timer)
        soul_rect = pygame.Rect(soul_x - 5, soul_y - 5, 10, 10)
        graze_rect = pygame.Rect(soul_x - 14, soul_y - 14, 28, 28)

        for b in bullets[:]:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b_rect = pygame.Rect(b["x"] - b["w"] // 2, b["y"] - b["h"] // 2, b["w"], b["h"])

            # 그레이즈(스치기) 판정 -> TP 증가
            if graze_rect.colliderect(b_rect) and not soul_rect.colliderect(b_rect):
                if tick % 5 == 0:
                    tp = min(100, tp + 1)

            # 피격 판정
            if soul_rect.colliderect(b_rect) and invincible_timer == 0:
                player_hp -= 15
                invincible_timer = 45
                bullets.remove(b)
                if player_hp <= 0:
                    player_hp = 0
                    state = STATE_GAME_OVER

            # 화면 밖 탄막 제거
            if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > HEIGHT:
                if b in bullets:
                    bullets.remove(b)

        # 적 턴 종료
        if enemy_turn_timer <= 0:
            bullets.clear()
            state = STATE_PLAYER_TURN

    # --- 화면 그리기 ---
    # 1. 보스 및 보스 체력바
    draw_knight(screen, WIDTH // 2, 115, tick)
    pygame.draw.rect(screen, GRAY, (220, 20, 200, 12))
    pygame.draw.rect(screen, CYAN, (220, 20, int(200 * (boss_hp / boss_max_hp)), 12))
    boss_txt = font_small.render(f"{boss_name}  {boss_hp}/{boss_max_hp}", True, WHITE)
    screen.blit(boss_txt, (220, 35))

    # 2. TP 게이지 (왼쪽)
    pygame.draw.rect(screen, WHITE, (30, 240, 22, 140), 2)
    tp_height = int(136 * (tp / 100))
    pygame.draw.rect(screen, YELLOW, (32, 240 + 138 - tp_height, 18, tp_height))
    tp_txt = font_small.render(f"TP {tp}%", True, YELLOW)
    screen.blit(tp_txt, (20, 385))

    # 3. 상태별 중앙 박스 연출
    if state == STATE_PLAYER_TURN:
        pygame.draw.rect(screen, WHITE, (60, 240, 520, 140), 3)
        msg_surf = font_main.render(message_text, True, WHITE)
        screen.blit(msg_surf, (80, 265))
        guide_surf = font_small.render("[방향키: 이동 / Z 또는 Enter: 선택 / 회피 중 Shift: 저속 이동]", True, GRAY)
        screen.blit(guide_surf, (80, 345))

    elif state == STATE_ATTACK_BAR:
        pygame.draw.rect(screen, WHITE, (60, 240, 520, 140), 3)
        # 타겟 영역
        pygame.draw.rect(screen, DARK_PURPLE, (120, 260, 400, 100))
        pygame.draw.rect(screen, CYAN, (310, 260, 20, 100))  # 크리티컬 존
        # 움직이는 바
        pygame.draw.rect(screen, WHITE, (attack_bar_x - 3, 255, 6, 110))
        guide_surf = font_small.render("중앙에 맞춰 [Z] 또는 [Enter]를 누르세요!", True, YELLOW)
        screen.blit(guide_surf, (190, 220))

    elif state == STATE_ENEMY_TURN:
        # 전투 박스
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 3)
        # 영혼(하트) 그리기 (피격 무적 시 깜빡임)
        if invincible_timer % 6 < 3:
            draw_heart(screen, int(soul_x), int(soul_y), RED)
        # 탄막 그리기
        for b in bullets:
            pygame.draw.rect(screen, b["color"], (b["x"] - b["w"] // 2, b["y"] - b["h"] // 2, b["w"], b["h"]))

    elif state == STATE_GAME_OVER:
        over_txt = font_title.render("GAME OVER - SOUL SHATTERED", True, RED)
        retry_txt = font_main.render("다시 시작하려면 [R] 키를 누르세요.", True, WHITE)
        screen.blit(over_txt, (WIDTH // 2 - over_txt.get_width() // 2, 260))
        screen.blit(retry_txt, (WIDTH // 2 - retry_txt.get_width() // 2, 310))

    elif state == STATE_VICTORY:
        win_txt = font_title.render("VICTORY! THE KNIGHT RETREATS", True, YELLOW)
        retry_txt = font_main.render("다시 플레이하려면 [R] 키를 누르세요.", True, WHITE)
        screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, 260))
        screen.blit(retry_txt, (WIDTH // 2 - retry_txt.get_width() // 2, 310))

    # 4. 하단 상태창 및 액션 버튼
    hp_txt = font_main.render(f"KRIS   HP {player_hp} / {player_max_hp}", True, WHITE)
    screen.blit(hp_txt, (70, 395))
    pygame.draw.rect(screen, RED, (260, 400, 120, 16))
    pygame.draw.rect(screen, GREEN, (260, 400, int(120 * (player_hp / player_max_hp)), 16))

    for i, opt in enumerate(menu_options):
        btn_x = 70 + i * 135
        btn_y = 430
        color = YELLOW if (state == STATE_PLAYER_TURN and i == selected_menu) else WHITE
        pygame.draw.rect(screen, color, (btn_x, btn_y, 115, 35), 2)
        opt_surf = font_main.render(opt, True, color)
        screen.blit(opt_surf, (btn_x + 22, btn_y + 5))
        if state == STATE_PLAYER_TURN and i == selected_menu:
            draw_heart(screen, btn_x + 12, btn_y + 18, RED)

    pygame.display.flip()
    clock.tick(60
