import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="DELTARUNE - THE ROARING KNIGHT", layout="centered")

# 배경을 검은색으로 맞추는 CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚔️ DELTARUNE - THE ROARING KNIGHT")
st.caption("게임 화면을 한 번 클릭한 뒤 키보드로 조작하세요. (방향키: 이동 / Z 또는 Enter: 선택 / Shift: 저속 이동)")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {
    margin: 0;
    padding: 0;
    background-color: #000;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    font-family: 'Malgun Gothic', 'Courier New', monospace;
  }
  canvas {
    border: 2px solid #444;
    background-color: #000;
    outline: none;
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="640" height="480" tabindex="1"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
canvas.focus();

// 클릭 시 포커스 유지
canvas.addEventListener("click", () => canvas.focus());

// 게임 상태 상수
const STATE_PLAYER_TURN = 0;
const STATE_ATTACK_BAR = 1;
const STATE_ENEMY_TURN = 2;
const STATE_GAME_OVER = 3;
const STATE_VICTORY = 4;

let state = STATE_PLAYER_TURN;
let tick = 0;
let invincibleTimer = 0;

// 플레이어(영혼) 설정
let soulX = 320;
let soulY = 310;
const soulSpeed = 4;
let playerHp = 90;
const playerMaxHp = 90;
let tp = 0;

// 보스(나이트) 설정
let bossHp = 500;
const bossMaxHp = 500;
const bossName = "ROARING KNIGHT";

// 전투 박스 설정
const boxWidth = 180;
const boxHeight = 140;
const boxX = 320 - boxWidth / 2;
const boxY = 240;

// 메뉴 및 공격 게이지
const menuOptions = ["FIGHT", "ACT", "ITEM", "DEFEND"];
let selectedMenu = 0;
let attackBarX = 120;
const attackBarSpeed = 7;
let messageText = "* 어둠의 기사가 앞을 가로막았다!";

// 탄막 및 적 턴 변수
let bullets = [];
let enemyTurnTimer = 0;
let attackPattern = 0;

// 키 입력 상태 저장
const keys = {};
window.addEventListener("keydown", (e) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space", "Enter"].includes(e.code)) {
    e.preventDefault();
  }
  keys[e.code] = true;
  handleKeyPress(e.code);
});
window.addEventListener("keyup", (e) => {
  keys[e.code] = false;
});

function startEnemyTurn(msg) {
  messageText = msg;
  state = STATE_ENEMY_TURN;
  enemyTurnTimer = 250;
  attackPattern = Math.floor(Math.random() * 3);
  soulX = boxX + boxWidth / 2;
  soulY = boxY + boxHeight / 2;
}

function handleKeyPress(code) {
  if (state === STATE_PLAYER_TURN) {
    if (code === "ArrowLeft") {
      selectedMenu = (selectedMenu - 1 + menuOptions.length) % menuOptions.length;
    } else if (code === "ArrowRight") {
      selectedMenu = (selectedMenu + 1) % menuOptions.length;
    } else if (code === "KeyZ" || code === "Enter") {
      const choice = menuOptions[selectedMenu];
      if (choice === "FIGHT") {
        state = STATE_ATTACK_BAR;
        attackBarX = 120;
      } else if (choice === "ACT") {
        if (tp >= 25) {
          tp -= 25;
          playerHp = Math.min(playerMaxHp, playerHp + 30);
          startEnemyTurn("* 영혼의 빛으로 HP를 30 회복했다! (TP -25%)");
        } else {
          startEnemyTurn("* 나이트의 갑옷은 차가운 어둠으로 덮여있다. (TP 25% 필요)");
        }
      } else if (choice === "ITEM") {
        playerHp = Math.min(playerMaxHp, playerHp + 40);
        startEnemyTurn("* 다크버거를 먹었다! HP가 40 회복되었다.");
      } else if (choice === "DEFEND") {
        tp = Math.min(100, tp + 20);
        startEnemyTurn("* 방어 태세를 취했다! TP가 20% 올랐다.");
      }
    }
  } else if (state === STATE_ATTACK_BAR) {
    if (code === "KeyZ" || code === "Enter") {
      const dist = Math.abs(320 - attackBarX);
      const damage = Math.max(20, Math.floor(120 - dist * 0.6));
      bossHp -= damage;
      tp = Math.min(100, tp + 10);
      if (bossHp <= 0) {
        bossHp = 0;
        state = STATE_VICTORY;
      } else {
        startEnemyTurn(`* 나이트에게 ${damage}의 데미지를 입혔다!`);
      }
    }
  } else if (state === STATE_GAME_OVER || state === STATE_VICTORY) {
    if (code === "KeyR") {
      playerHp = playerMaxHp;
      bossHp = bossMaxHp;
      tp = 0;
      bullets = [];
      state = STATE_PLAYER_TURN;
      messageText = "* 어둠의 기사가 다시 나타났다!";
    }
  }
}

function drawHeart(x, y, color = "#FF0000") {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x, y - 4);
  ctx.lineTo(x - 4, y - 8);
  ctx.lineTo(x - 8, y - 4);
  ctx.lineTo(x - 8, y + 1);
  ctx.lineTo(x, y + 8);
  ctx.lineTo(x + 8, y + 1);
  ctx.lineTo(x + 8, y - 4);
  ctx.lineTo(x + 4, y - 8);
  ctx.closePath();
  ctx.fill();
}

function drawKnight(x, y, t) {
  const floatY = y + Math.sin(t * 0.05) * 6;

  // 망토
  ctx.fillStyle = "#3C0064";
  ctx.beginPath();
  ctx.moveTo(x, floatY - 30);
  ctx.lineTo(x - 45, floatY + 50);
  ctx.lineTo(x + 45, floatY + 50);
  ctx.closePath();
  ctx.fill();

  // 갑옷 몸통
  ctx.fillStyle = "#FFFFFF";
  ctx.beginPath();
  ctx.moveTo(x, floatY - 35);
  ctx.lineTo(x - 22, floatY + 10);
  ctx.lineTo(x, floatY + 35);
  ctx.lineTo(x + 22, floatY + 10);
  ctx.closePath();
  ctx.fill();

  // 투구 및 뿔
  ctx.fillStyle = "#000000";
  ctx.beginPath();
  ctx.arc(x, floatY - 42, 14, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = "#FFFFFF";
  ctx.beginPath();
  ctx.moveTo(x - 10, floatY - 48);
  ctx.lineTo(x - 25, floatY - 75);
  ctx.lineTo(x - 4, floatY - 52);
  ctx.fill();

  ctx.beginPath();
  ctx.moveTo(x + 10, floatY - 48);
  ctx.lineTo(x + 25, floatY - 75);
  ctx.lineTo(x + 4, floatY - 52);
  ctx.fill();

  // 빛나는 바이저
  ctx.strokeStyle = "#00FFFF";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x - 8, floatY - 42);
  ctx.lineTo(x + 8, floatY - 42);
  ctx.stroke();

  // 대검
  const swordOffset = Math.cos(t * 0.05) * 4;
  ctx.fillStyle = "#00FFFF";
  ctx.beginPath();
  ctx.moveTo(x + 35, floatY - 20 + swordOffset);
  ctx.lineTo(x + 42, floatY - 20 + swordOffset);
  ctx.lineTo(x + 38, floatY + 60 + swordOffset);
  ctx.closePath();
  ctx.fill();
}

function spawnBullets(pattern, timer) {
  if (pattern === 0 && timer % 15 === 0) {
    const bx = boxX + 10 + Math.random() * (boxWidth - 20);
    bullets.push({ x: bx, y: boxY - 20, vx: 0, vy: 3.5, w: 6, h: 18, color: "#FFFFFF" });
  } else if (pattern === 1 && timer % 25 === 0) {
    const side = Math.random() < 0.5 ? -1 : 1;
    const bx = side === 1 ? boxX - 20 : boxX + boxWidth + 20;
    const by = boxY + 15 + Math.random() * (boxHeight - 30);
    bullets.push({ x: bx, y: by, vx: side * 4, vy: 0, w: 22, h: 5, color: "#00FFFF" });
  } else if (pattern === 2 && timer % 35 === 0) {
    const angle = Math.random() * Math.PI * 2;
    const dist = 130;
    const bx = boxX + boxWidth / 2 + Math.cos(angle) * dist;
    const by = boxY + boxHeight / 2 + Math.sin(angle) * dist;
    bullets.push({
      x: bx,
      y: by,
      vx: -Math.cos(angle) * 2.8,
      vy: -Math.sin(angle) * 2.8,
      w: 10,
      h: 10,
      color: "#A020F0"
    });
  }
}

function rectIntersect(r1, r2) {
  return !(r2.left > r1.right || r2.right < r1.left || r2.top > r1.bottom || r2.bottom < r1.top);
}

function update() {
  tick++;

  if (state === STATE_ATTACK_BAR) {
    attackBarX += attackBarSpeed;
    if (attackBarX > 520) {
      startEnemyTurn("* 공격이 빗나갔다!");
    }
  } else if (state === STATE_ENEMY_TURN) {
    enemyTurnTimer--;
    if (invincibleTimer > 0) invincibleTimer--;

    const currentSpeed = (keys["ShiftLeft"] || keys["ShiftRight"] || keys["KeyX"]) ? soulSpeed * 0.5 : soulSpeed;
    if (keys["ArrowLeft"]) soulX -= currentSpeed;
    if (keys["ArrowRight"]) soulX += currentSpeed;
    if (keys["ArrowUp"]) soulY -= currentSpeed;
    if (keys["ArrowDown"]) soulY += currentSpeed;

    soulX = Math.max(boxX + 10, Math.min(boxX + boxWidth - 10, soulX));
    soulY = Math.max(boxY + 10, Math.min(boxY + boxHeight - 10, soulY));

    spawnBullets(attackPattern, enemyTurnTimer);

    const soulRect = { left: soulX - 5, right: soulX + 5, top: soulY - 5, bottom: soulY + 5 };
    const grazeRect = { left: soulX - 14, right: soulX + 14, top: soulY - 14, bottom: soulY + 14 };

    for (let i = bullets.length - 1; i >= 0; i--) {
      const b = bullets[i];
      b.x += b.vx;
      b.y += b.vy;

      const bRect = {
        left: b.x - b.w / 2,
        right: b.x + b.w / 2,
        top: b.y - b.h / 2,
        bottom: b.y + b.h / 2
      };

      // 그레이즈 판정
      if (rectIntersect(grazeRect, bRect) && !rectIntersect(soulRect, bRect)) {
        if (tick % 5 === 0) tp = Math.min(100, tp + 1);
      }

      // 피격 판정
      if (rectIntersect(soulRect, bRect) && invincibleTimer === 0) {
        playerHp -= 15;
        invincibleTimer = 45;
        bullets.splice(i, 1);
        if (playerHp <= 0) {
          playerHp = 0;
          state = STATE_GAME_OVER;
        }
        continue;
      }

      if (b.x < 0 || b.x > 640 || b.y < 0 || b.y > 480) {
        bullets.splice(i, 1);
      }
    }

    if (enemyTurnTimer <= 0 && state === STATE_ENEMY_TURN) {
      bullets = [];
      state = STATE_PLAYER_TURN;
    }
  }
}

function draw() {
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, 640, 480);

  // 1. 보스 및 체력바
  drawKnight(320, 115, tick);
  ctx.fillStyle = "#808080";
  ctx.fillRect(220, 20, 200, 12);
  ctx.fillStyle = "#00FFFF";
  ctx.fillRect(220, 20, 200 * (bossHp / bossMaxHp), 12);

  ctx.fillStyle = "#FFFFFF";
  ctx.font = "14px sans-serif";
  ctx.fillText(`${bossName}  ${bossHp}/${bossMaxHp}`, 220, 48);

  // 2. TP 게이지
  ctx.strokeStyle = "#FFFFFF";
  ctx.lineWidth = 2;
  ctx.strokeRect(30, 240, 22, 140);
  const tpHeight = 136 * (tp / 100);
  ctx.fillStyle = "#FFFF00";
  ctx.fillRect(32, 240 + 138 - tpHeight, 18, tpHeight);
  ctx.font = "13px sans-serif";
  ctx.fillText(`TP ${tp}%`, 20, 398);

  // 3. 중앙 박스 연출
  if (state === STATE_PLAYER_TURN) {
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 3;
    ctx.strokeRect(60, 240, 520, 140);

    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 18px 'Malgun Gothic', sans-serif";
    ctx.fillText(messageText, 80, 285);

    ctx.fillStyle = "#888888";
    ctx.font = "14px 'Malgun Gothic', sans-serif";
    ctx.fillText("[방향키: 이동 / Z 또는 Enter: 선택 / 회피 중 Shift: 저속 이동]", 80, 355);
  } else if (state === STATE_ATTACK_BAR) {
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 3;
    ctx.strokeRect(60, 240, 520, 140);

    ctx.fillStyle = "#3C0064";
    ctx.fillRect(120, 260, 400, 100);
    ctx.fillStyle = "#00FFFF";
    ctx.fillRect(310, 260, 20, 100);

    ctx.fillStyle = "#FFFFFF";
    ctx.fillRect(attackBarX - 3, 255, 6, 110);

    ctx.fillStyle = "#FFFF00";
    ctx.font = "14px 'Malgun Gothic', sans-serif";
    ctx.fillText("중앙에 맞춰 [Z] 또는 [Enter]를 누르세요!", 195, 228);
  } else if (state === STATE_ENEMY_TURN) {
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 3;
    ctx.strokeRect(boxX, boxY, boxWidth, boxHeight);

    if (invincibleTimer % 6 < 3) {
      drawHeart(soulX, soulY, "#FF0000");
    }

    for (const b of bullets) {
      ctx.fillStyle = b.color;
      ctx.fillRect(b.x - b.w / 2, b.y - b.h / 2, b.w, b.h);
    }
  } else if (state === STATE_GAME_OVER) {
    ctx.fillStyle = "#FF0000";
    ctx.font = "bold 28px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("GAME OVER - SOUL SHATTERED", 320, 285);
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "18px 'Malgun Gothic', sans-serif";
    ctx.fillText("다시 시작하려면 [R] 키를 누르세요.", 320, 325);
    ctx.textAlign = "left";
  } else if (state === STATE_VICTORY) {
    ctx.fillStyle = "#FFFF00";
    ctx.font = "bold 28px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("VICTORY! THE KNIGHT RETREATS", 320, 285);
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "18px 'Malgun Gothic', sans-serif";
    ctx.fillText("다시 플레이하려면 [R] 키를 누르세요.", 320, 325);
    ctx.textAlign = "left";
  }

  // 4. 하단 상태창 및 액션 버튼
  ctx.fillStyle = "#FFFFFF";
  ctx.font = "bold 18px sans-serif";
  ctx.fillText(`KRIS   HP ${playerHp} / ${playerMaxHp}`, 70, 415);

  ctx.fillStyle = "#FF0000";
  ctx.fillRect(265, 400, 120, 16);
  ctx.fillStyle = "#00FF00";
  ctx.fillRect(265, 400, 120 * (playerHp / playerMaxHp), 16);

  for (let i = 0; i < menuOptions.length; i++) {
    const btnX = 70 + i * 135;
    const btnY = 430;
    const isSelected = state === STATE_PLAYER_TURN && i === selectedMenu;
    const color = isSelected ? "#FFFF00" : "#FFFFFF";

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(btnX, btnY, 115, 35);

    ctx.fillStyle = color;
    ctx.font = "bold 18px sans-serif";
    ctx.fillText(menuOptions[i], btnX + 25, btnY + 24);

    if (isSelected) {
      drawHeart(btnX + 13, btnY + 18, "#FF0000");
    }
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=500)
