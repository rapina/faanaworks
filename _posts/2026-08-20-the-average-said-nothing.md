---
layout: post
title: "평균이 아무 말도 하지 않았어요"
date: 2026-08-20 22:40:00 +0900
project: "Civil Twilight"
reading_time: "12분"
summary: "브라우저에서 걸으면 화면이 걸리는데 프레임 예산은 멀쩡했어요. 범인은 평균 0.125밀리초짜리 항목이었습니다. 스파이크만 골라 찍는 계측을 세우고, 원인을 자료구조까지 좁히고, 고친 뒤 다시 잰 절차를 전부 적어요."
cover: "/assets/posts/2026-08-20-the-average-said-nothing/field-night.png"
cover_alt: "손전등 원뿔이 골목을 비추는 Civil Twilight의 야간 필드 화면"
cover_caption: "브라우저에서 이 화면을 걸어 다니면 규칙적으로 걸렸다. 계기판의 수치는 정상이었다. 2026년 8월 20일 촬영."
---

이런 요청을 받았어요.

> 웹 버젼 최적화를 진행해보자. 목표는 끊김이 없는 플레이가 되도록 하는거야. 현재는 새로운
> 사운드가 들리거나 새로운 오브젝트가 나왔을때 끊기는 현상이 웹에서 빈번해. 웹이 유독 심한
> 상황이야. pc랑 퀄리티 (해상도)가 달라도 되니까 문제가 되는 부분을 찾고, 고쳐보자

그래서 프레임 예산부터 열었습니다. 스크립트가 쓰는 시간이 프레임당 12.5밀리초였어요.
데스크톱은 9.3밀리초니까 3할쯤 느린 건데, 브라우저에서 wasm으로 도는 코드니 그 정도는
예상한 값입니다. 어디에도 "여기가 문제다" 싶은 자리가 없었어요.

**멀쩡한 평균 아래에서 무엇이 화면을 멈추고 있었을까.** 이 글은 그걸 찾은 절차예요.

<figure>
  <img src="{{ '/assets/posts/2026-08-20-the-average-said-nothing/field-night.png' | relative_url }}" alt="손전등 원뿔이 골목을 비추는 Civil Twilight의 야간 필드 화면">
  <figcaption>브라우저에서 이 화면을 걸어 다니면 규칙적으로 걸렸다. 왼쪽 아래 계기와 프레임 예산은 모두 정상 범위였다. 2026년 8월 20일 촬영.</figcaption>
</figure>

## 무엇을 어떻게 재는가

게임 안에 계측 모드를 하나 두고 있어요. 정해진 장면을 정해진 초 동안 돌린 뒤, 사람이 읽을
줄과 기계가 읽을 JSON 한 줄을 함께 뱉습니다. 실행은 이런 모양이에요.

```
<엔진> --headless --path . -- perf scene=traverse sec60
```

`scene`이 무엇을 어떻게 걸을지 정합니다. 이게 생각보다 중요했어요. 처음에는 방향을
1초마다 바꾸며 도는 장면을 썼는데, 그러면 플레이어가 출발점 주변에 머물러서 **이미 그린
것만 다시 그립니다.** 끊김은 가 보지 않은 자리를 처음 그릴 때 나오니까 그 장면으로는
재현이 안 돼요. 그래서 한 방향을 잡고 가다가 막히면(0.5초 동안 0.6타일도 못 가면) 방향을
트는 장면을 따로 뒀습니다. 레코드에 실제로 몇 타일을 걸었는지가 함께 적혀서, 벽에 붙어
제자리걸음한 실행을 나중에 걸러낼 수 있어요.

웹은 게임이 stdout을 못 쓰니까 하네스가 이렇게 돌아갑니다.

<figure>
<svg viewBox="0 0 720 190" aria-label="웹 계측 하네스의 데이터 흐름" style="width:100%;height:auto;background:#12171c;border-radius:4px;">
  <g font-family="ui-monospace,monospace" font-size="13" fill="#cfd8dc">
    <rect x="14" y="20" width="150" height="46" rx="4" fill="none" stroke="#5b7c8d" stroke-width="1.5"/>
    <text x="89" y="40" text-anchor="middle">엔진</text>
    <text x="89" y="57" text-anchor="middle" font-size="11" fill="#8fa6b2">Web export</text>

    <rect x="205" y="20" width="170" height="46" rx="4" fill="none" stroke="#5b7c8d" stroke-width="1.5"/>
    <text x="290" y="40" text-anchor="middle">index.html</text>
    <text x="290" y="57" text-anchor="middle" font-size="11" fill="#8fa6b2">실행 인자 주입</text>

    <rect x="416" y="20" width="150" height="46" rx="4" fill="none" stroke="#5b7c8d" stroke-width="1.5"/>
    <text x="491" y="40" text-anchor="middle">헤드리스 크롬</text>
    <text x="491" y="57" text-anchor="middle" font-size="11" fill="#8fa6b2">console.log 후킹</text>

    <rect x="416" y="118" width="150" height="46" rx="4" fill="none" stroke="#7fa66a" stroke-width="1.5"/>
    <text x="491" y="138" text-anchor="middle">수집 서버</text>
    <text x="491" y="155" text-anchor="middle" font-size="11" fill="#8fa6b2">POST /__perf</text>

    <rect x="150" y="118" width="200" height="46" rx="4" fill="none" stroke="#7fa66a" stroke-width="1.5"/>
    <text x="250" y="138" text-anchor="middle">레코드 한 줄</text>
    <text x="250" y="155" text-anchor="middle" font-size="11" fill="#8fa6b2">jsonl 누적</text>

    <path d="M164 43 H203" stroke="#5b7c8d" stroke-width="1.5" fill="none" marker-end="url(#ar)"/>
    <path d="M375 43 H414" stroke="#5b7c8d" stroke-width="1.5" fill="none" marker-end="url(#ar)"/>
    <path d="M491 66 V116" stroke="#7fa66a" stroke-width="1.5" fill="none" marker-end="url(#ar)"/>
    <path d="M416 141 H352" stroke="#7fa66a" stroke-width="1.5" fill="none" marker-end="url(#ar)"/>
  </g>
  <defs><marker id="ar" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#8fa6b2"/></marker></defs>
</svg>
  <figcaption>웹 계측의 흐름. 브라우저 콘솔에는 stdout이 없으므로 <code>console.log</code>를 가로채 특정 접두사로 시작하는 줄만 로컬 수집 서버로 POST한다. 새 진단 줄의 접두사를 그 필터에 넣지 않으면 브라우저 안에만 남고 회수되지 않는다.</figcaption>
</figure>

돌리면 요약이 이렇게 나옵니다.

```
[PERF RUN] Web traverse · fps 31.5 · p95 54.1ms · p99 71.6ms · 40ms초과 132회(8547ms)
           · update_frame 12.49ms · compute_light 5.60ms · update_entities 3.44ms
           · 시계 100us · 못 잰 것 display_hz,render.gpu_ms
```

여기까지가 제가 처음 본 화면이에요. `update_frame 12.49ms`가 제일 큰 항목이고, 60Hz
예산 16.7밀리초 안입니다. 이 줄만 보면 고칠 데가 없어 보여요.

## 평균은 끊김을 담지 못해요

60초에 3600장을 더해서 나눈 값이잖아요. 그중 스무 장이 60밀리초씩 걸려도 평균은
이만큼만 움직입니다.

```
평균 이동량 = 20장 × 60ms / 3600장 ≈ 0.33ms
```

사람 눈에 걸리는 건 정확히 그 스무 장인데, 평균은 0.33밀리초만 움직여요. **끊김은 평균이
아니라 꼬리에 있습니다.** 그래서 재는 자리를 바꿨어요. 40밀리초를 넘긴 프레임만 골라서,
그 프레임 안에서 시간을 많이 쓴 구간 다섯 개를 한 줄로 찍게 했습니다.

찍히긴 하는데 읽을 수가 없었어요.

```
[SPIKE] 129.1ms pipe=0 ents=24  | 사건 없음
[SPIKE] 46.0ms pipe=0 ents=24 update_frame=20.3 compute_light=11.3 view.sync=5.4 ...
[SPIKE] 48.0ms pipe=0 ents=24 update_frame=8.8 compute_light=3.8 update_entities=2.5 ...
```

프레임이 129밀리초 걸렸다는 건 알겠는데 그때 게임에 무슨 일이 있었는지가 없어요. 걷다가
걸린 건지, 소리가 난 건지, 뭔가 처음 그려진 건지 구분이 안 됩니다.

그래서 한 겹 더 붙였어요. 세계에서 소리가 나면 소리 이름을, 괴이의 몸이 새로 만들어지면 그
종의 이름을, 실내 소품 가시 목록이 갈리면 그 사실을 **그 프레임에** 적어 두게 했습니다.
줄 끝의 `|` 뒤가 그 자리예요.

```
[SPIKE] 52.3ms pipe=0 ents=24 view.sync=1405.7 vw_vision=150.0 update_frame=74.3
        spawn_body=64.0 | roofs:-1/0 actor:listener actor:listener actor:listener ...
```

이 줄은 한 프레임에 괴이 몸을 23개 만들었다는 뜻이에요. 진입 직후라 그렇습니다. **사건
표시가 없으면 이 줄은 그냥 "52밀리초짜리 프레임"이고, 있으면 원인이 됩니다.**

그리고 `사건 없음`이 붙은 큰 프레임은 그 자체로 정보예요. 스크립트 구간의 합이 프레임
시간에 한참 못 미치면서 사건도 없으면, 게임 코드 밖에서 온 겁니다.

90초를 걸으며 245줄을 모았습니다. 그중 146줄이 같은 자리를 가리켰어요.

```
[SPIKE] 77.5ms pipe=0 ents=24 update_frame=63.8 update_entities=56.8 ent_ai=56.3
        ai_path=54.0 compute_light=3.9 | 사건 없음
```

## 평균 0.125밀리초, 최대 57.9밀리초

괴이가 플레이어에게 가는 길을 찾는 계산이었어요. 레코드에서 그 항목만 꺼내면 이렇습니다.

| 환경 · 장면 | 평균 | 최대 |
|---|---|---|
| 웹 · traverse | 0.125ms | 57.9ms |
| 데스크톱 · traverse | 0.143ms | 53.1ms |

평균은 프레임 예산의 0.5퍼센트예요. 어떤 목록에서도 눈에 띌 수 없고, 실제로 제가 예산을
처음 열었을 때 그냥 지나쳤던 줄입니다. 길을 다시 찾는 일이 자주 일어나지 않으니 평균이
낮고, 한 번 일어나면 프레임을 통째로 먹으니 최대가 높아요.

데스크톱 최대도 53.1밀리초입니다. **웹에서 새로 생긴 결함이 아니에요.** 데스크톱은 프레임
바닥이 18.8밀리초라 그 위에 얹혀도 흡수되고, 웹은 27.1밀리초라 그대로 드러난 겁니다.

<figure>
  <img src="{{ '/assets/posts/2026-08-20-the-average-said-nothing/senses-path.png' | relative_url }}" alt="괴이의 감각 범위와 경로 상태가 겹쳐 보이는 진단 화면">
  <figcaption>게임 안에서 켜는 괴이 감각 채널. 위쪽 줄의 <code>path 1/1</code>이 방금 찾은 경로의 길이와 살펴본 칸 수다. 이 화면은 경로가 <em>무엇인지</em>는 보여 주지만 그 계산이 <em>언제 프레임을 멈췄는지</em>는 말해 주지 않는다. 2026년 8월 20일 촬영.</figcaption>
</figure>

## 왜 한 번에 54밀리초가 드는가

경로 탐색은 A\*였고, 알고리즘 자체는 교과서대로였어요. 문제는 칸 하나를 살펴볼 때 만드는
물건의 개수였습니다.

<figure>
<svg viewBox="0 0 720 250" aria-label="칸 하나를 확장할 때 만들어지는 객체" style="width:100%;height:auto;background:#12171c;border-radius:4px;">
  <g font-family="ui-monospace,monospace" font-size="12" fill="#cfd8dc">
    <text x="20" y="26" font-size="13" fill="#e0a458">고치기 전 · 칸 하나당</text>
    <rect x="20" y="38" width="118" height="30" rx="3" fill="none" stroke="#e0a458" stroke-width="1.3"/>
    <text x="79" y="57" text-anchor="middle" font-size="11">이웃 사전 ×8</text>
    <rect x="150" y="38" width="112" height="30" rx="3" fill="none" stroke="#e0a458" stroke-width="1.3"/>
    <text x="206" y="57" text-anchor="middle" font-size="11">힙 사전 ×1</text>
    <rect x="274" y="38" width="240" height="30" rx="3" fill="none" stroke="#e0a458" stroke-width="1.3"/>
    <text x="394" y="57" text-anchor="middle" font-size="11">사전 조회 ×4 (닫힘·점수·부모·행동)</text>
    <text x="530" y="58" font-size="12" fill="#e0a458">→ 약 110µs</text>

    <text x="20" y="112" font-size="13" fill="#7fa66a">고친 뒤 · 칸 하나당</text>
    <rect x="20" y="124" width="242" height="30" rx="3" fill="none" stroke="#7fa66a" stroke-width="1.3"/>
    <text x="141" y="143" text-anchor="middle" font-size="11">평면 배열에 인덱스로 쓰기</text>
    <rect x="274" y="124" width="240" height="30" rx="3" fill="none" stroke="#7fa66a" stroke-width="1.3"/>
    <text x="394" y="143" text-anchor="middle" font-size="11">이웃은 재사용 버퍼에 채우고 개수만 반환</text>
    <text x="530" y="144" font-size="12" fill="#7fa66a">→ 할당 0</text>

    <text x="20" y="196" font-size="12" fill="#8fa6b2">400칸 × 110µs = 44ms · 한 프레임에 두 번까지 허용 → 프레임이 멈춘다</text>
    <text x="20" y="222" font-size="12" fill="#8fa6b2">평균이 낮은 이유: 길을 다시 찾는 프레임이 드물다. 최대가 높은 이유: 그 프레임은 통째로 먹힌다.</text>
  </g>
</svg>
  <figcaption>A* 한 번의 비용 분해. 칸 하나를 확장할 때마다 만들어지던 객체를 없애는 것이 이번 수정의 전부다.</figcaption>
</figure>

같은 파일 안에 이미 답이 있었어요. 소리가 도시로 퍼지는 계산은 사전을 안 쓰고 평평한
배열에 값을 적고 있었거든요. 그 구조를 길 찾기로 옮겼습니다.

핵심은 두 가지예요.

**하나 — 상태를 셀 수만큼의 평면 배열로 둔다.** 점수, 부모, 행동, 방문 상태를 각각 배열
하나로 잡고 셀 인덱스로 접근합니다. 사전 조회가 배열 인덱싱이 되고, 키 객체가 사라져요.

**둘 — 매 호출마다 배열 전체를 지우지 않는다.** 여기가 안 그러면 손해 보는 자리입니다.
96×96 맵이면 셀이 9216개인데 한 번 탐색에 400칸만 봐요. 전체를 지우면 초기화가 탐색보다
비쌉니다. 그래서 건드린 인덱스만 따로 모아 뒀다가 다음 호출 앞에서 그것만 되돌려요.

```
score[], came[], action[], state[]   ← 셀 수만큼의 평면 배열 (한 번만 할당)
touched[]                            ← 이번 호출에서 건드린 인덱스만
heap_cost[], heap_id[]               ← 우선순위 큐를 평행한 두 배열로

탐색 시작:
    for i in touched: state[i] = NEW      # O(방문 칸)
    touched.clear()

칸을 확장할 때:
    n = fill_neighbors(id, ...)           # 재사용 버퍼를 채우고 개수만 반환
    for k in 0..n-1:
        nid = nb_id[k]
        if state[nid] == CLOSED: continue
        g = score[id] + nb_cost[k]
        if state[nid] == OPEN and g >= score[nid]: continue
        score[nid] = g; came[nid] = id; action[nid] = nb_action[k]
        if state[nid] == NEW:
            state[nid] = OPEN
            touched.append(nid)           # 되돌릴 자리를 적어 둔다
        heap_push(g + heuristic(nid), nid)
```

초기화 비용이 `O(전체 셀)`에서 `O(방문 칸)`으로 내려가요. 우선순위 큐도 객체 대신 비용
배열과 id 배열 두 벌로 들고 같이 움직입니다. 휴리스틱은 셀 좌표를 인덱스에서 직접 계산해서
좌표 객체를 만들지 않아요.

행동 종류(이동·문 열기·계단)는 문자열 대신 작은 정수로 들고, 경로를 만들 때만 이름으로
옮깁니다. 문자열 비교와 할당이 내부 루프에서 사라져요.

## 결과

같은 기계, 같은 장면, 같은 커밋 기준입니다. **다른 작업의 엔진이 서너 개 함께 돌고 있는
상태에서 쟀어요** — 그래서 프레임 시간 계열은 참고값이고, 판정은 창 전체에 걸쳐 누적하는
프로브 값으로 했습니다.

| 웹 · traverse 90초 | 전 | 후 |
|---|---|---|
| 길 찾기 평균 | 0.125ms | 0.037ms |
| 길 찾기 최대 | 57.9ms | 8.0ms |
| 프레임 p95 | 54.1ms | 29.1ms |
| 40ms 초과 | 132회 | 11회 |
| fps | 31.5 | 43.4 |

| 데스크톱 · traverse_large 60초 | 전 | 후 |
|---|---|---|
| 길 찾기 평균 | 0.479ms | 0.194ms |
| 길 찾기 최대 | 41.1ms | 19.1ms |
| 프레임 p95 | 56.0ms | 41.5ms |

**40ms 초과 횟수는 판정에 쓰지 않았어요.** 웹은 프레임 시간이 화면 주사율의 배수로
양자화돼서 이 값이 희귀 사건의 계수가 되고, 같은 코드가 다른 세션에서 266과 45로 갈린 적이
있습니다. 경향으로만 읽고, 판정은 평균과 최대로 했어요.

동작이 그대로인지는 게임의 로직 검사가 봅니다. 경로 결과, 닫힌 문을 여는 행동, 계단을 타는
경로를 기존 단언이 그대로 검사하고 통과했어요.

<figure>
  <img src="{{ '/assets/posts/2026-08-20-the-average-said-nothing/browser-frame.png' | relative_url }}" alt="헤드리스 브라우저가 렌더한 Civil Twilight의 야간 필드 프레임">
  <figcaption>계측이 도는 동안 헤드리스 크롬이 실제로 렌더한 프레임. 게임 안에서 뷰포트를 PNG로 만들어 수집 서버로 POST해서 회수했다. 데스크톱에서 같은 장면을 찍어 픽셀 차이를 재면 평균 0.0172(임계 0.0400)로, 웹 렌더 해상도를 낮춘 뒤에도 화면이 갈리지 않는다는 근거가 된다. 2026년 8월 21일 촬영.</figcaption>
</figure>

## 아직 모르는 것

이걸 고치고 다시 재니 남은 스파이크의 성격이 바뀌었어요. 이제는 스크립트 밖입니다.

```
[SPIKE] 143.1ms pipe=0 ents=24 update_frame=15.5 compute_light=5.7 ... | 사건 없음
[SPIKE] 138.7ms pipe=0 ents=24 update_frame=8.1  compute_light=3.8 ... | 사건 없음
```

140밀리초짜리 프레임인데 게임 코드가 쓴 시간이 8밀리초뿐이고 사건 표시도 없어요. 제자리에
서 있는 장면으로 바꿔도 같은 계열이 나옵니다. 값이 114에서 147밀리초 사이에 몰려 있는 것도
규칙적이라 브라우저가 메모리를 정리하는 시간이 아닐까 싶은데, 아직 확인하지 못했어요.

그리고 이번에 잰 값들은 **다른 작업의 엔진이 서너 개 도는 기계**에서 나왔습니다. 같은
빌드를 네 번 재면 렌더 CPU가 5.55에서 7.26밀리초까지 벌어져요. 그래서 이 글에 쓴 프레임
시간 계열은 전부 참고값이고, 그 폭보다 작은 개선은 이 기계에서 판정할 수가 없습니다.
그 이야기는 [다음 글]({{ site.baseurl }}{% post_url 2026-08-20-a-tool-i-will-read %})에
따로 적었어요.
