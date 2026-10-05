# 경기광주 재가복지센터 홈페이지

GitHub Actions가 **매일 오전 9시(한국 시간)에 글을 한 편씩** 자동으로 공개해요.
첫날에는 3편(등급 신청, 비용, 서비스 비교)이 올라가고, 그다음부터 하루 1편씩 올라가요. 글은 모두 300편이고, 약 10개월(297일) 동안 매일 새 글이 발행돼요.

## 폴더 구조

```
config.json              도메인, 시작일, 센터명, 전화번호
content/posts.json       글 300편 (day = 시작일로부터 며칠째에 공개할지)
src/home_main.html       메인 페이지 본문
static/assets/           style.css, main.js
build.py                 오늘 날짜까지 공개할 글만 골라 public/ 에 사이트 생성
.github/workflows/publish.yml   매일 자동 실행
form-apps-script.js      상담 폼 → 구글 시트 연결 코드
```

## 처음 세팅 (10분)

1. GitHub에 새 레포를 만들고 이 폴더 내용을 그대로 올려요.
2. 레포의 **Settings → Pages → Source**를 **GitHub Actions**로 바꿔요.
3. `config.json`을 고쳐요.
   - `domain`: 실제 도메인 (예: `https://gjcare.co.kr`). 그대로 두면 자동으로 `https://아이디.github.io/레포이름`을 써요.
   - `start_date`: 첫 글을 공개할 날짜
   - `tel`: 센터 전화번호
4. 커밋해서 올리면 자동으로 첫 빌드가 돌아가요. **Actions** 탭에서 진행 상황을 볼 수 있어요.
5. 도메인을 연결했다면 **Settings → Pages → Custom domain**에도 같은 도메인을 넣어요. CNAME 파일은 자동으로 만들어져요.

## 내 컴퓨터에서 미리보기

```bash
python build.py                          # 오늘 기준
BUILD_DATE=2026-11-30 python build.py    # 특정 날짜 기준 (어떤 글까지 공개되는지 확인)
```

빌드하면 `public/index.html`이 생겨요. 브라우저로 열어 보면 돼요.

## 글 관리

- **순서 바꾸기**: `content/posts.json`에서 해당 글의 `day` 숫자를 바꿔요.
- **새 글 추가**: 아래 형식으로 하나 추가하고 `day`를 마지막 숫자 다음으로 넣어요.

```json
{
  "id": "영문-주소",
  "category": "grade | money | service | dementia | health | family | policy | center",
  "title": "글 제목",
  "summary": "한두 줄 요약 (목록, 검색 설명에 쓰여요)",
  "minutes": 3,
  "keyword": "썸네일에 크게 들어갈 말",
  "body": "본문",
  "day": 51
}
```

본문 쓰는 법: `## 소제목`, `- 목록`, `| 표 | 칸 |`(첫 줄이 제목 줄), `> 박스 제목|박스 내용`, `**굵게**`

- **바로 공개하기**: Actions 탭 → "매일 글 발행" → **Run workflow**를 눌러요.

## 올리기 전에 바꿀 것

`src/home_main.html`이랑 `build.py`의 footer 부분에 있는 아래 항목을 바꿔요.

- `○○○` → 센터장 이름
- `상세 주소` → 실제 주소
- `지정 후 기재` → 장기요양기관 지정번호

## 상담 폼 연결

1. 구글 시트를 새로 만들고 **확장 프로그램 → Apps Script**를 열어요. `form-apps-script.js` 내용을 붙여넣어요.
2. **배포 → 새 배포 → 웹 앱**을 고르고, 실행은 "나", 액세스는 "모든 사용자"로 배포해요.
3. 나온 URL을 `static/assets/main.js` 맨 위 `FORM_ENDPOINT`에 넣어요.

## 검색 등록

1. **네이버 스마트플레이스** 등록. 지역 검색 노출 효과가 가장 커요.
2. **네이버 서치어드바이저**와 **구글 서치콘솔**에 사이트를 등록해요. 소유확인 메타태그는 `build.py`의 `head()` 안 주석 자리에 넣어요. 그다음 `도메인/sitemap.xml`을 제출해요.

sitemap은 매일 새 글이 반영된 상태로 자동 갱신돼요.

## 알아둘 것

- GitHub 예약 실행은 서버가 붐비면 몇십 분 늦게 돌 수 있어요.
- 레포에 60일 동안 아무 활동이 없으면 GitHub가 예약 실행을 멈춰요. 글이 공개되는 동안은 매일 자동 커밋이 생기니까 괜찮아요. 300편을 다 올린 뒤 새 글을 추가할 때 Actions 탭에서 다시 켜 주면 돼요.
