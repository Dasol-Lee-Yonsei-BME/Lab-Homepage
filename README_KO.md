# BNSL GitHub Pages 홈페이지 — 관리 가이드

이 저장소는 **홈페이지 디자인과 연구실 데이터가 분리**되어 있습니다. 평소에는 `data/`와 `assets/images/`만 수정하면 됩니다. `main` 브랜치에 Commit하면 GitHub Actions가 자동으로 홈페이지를 다시 만들고 GitHub Pages에 배포합니다.

## 평소에 수정하는 곳

- `data/publications.yml` — 논문
- `data/projects.yml` — 연구과제 (Research 화면)
- `data/achievements.yml` — 특허 / 수상 / 학회
- `data/people.yml` — PI / Current Members / Alumni
- `data/news.yml` — 뉴스 (사진 없이 텍스트 중심으로 관리)
- `data/research.yml` — 연구 분야 설명
- `data/site.yml` — 홈페이지 이름 / 소개문 / 연락처
- `assets/images/` — 모든 이미지

## 새 논문 추가

`data/publications.yml`에서 기존 항목 하나를 복사해 맨 위에 추가합니다. **모든 논문은 반드시 `image:`가 있어야 합니다.** 이미지가 없으면 빌드가 실패하도록 설정해 두었습니다.

```yaml
- id: 2026-new-paper
  year: 2026
  authors: "Dasol Lee, ..."
  title: "Paper title"
  journal: "Journal Name"
  date: "2026.08.10"
  url: "https://doi.org/..."
  image: "assets/images/publications/2026-new-paper.jpg"
  highlight: false
```

그리고 `assets/images/publications/2026-new-paper.jpg`를 업로드하면 됩니다.

## 메인 Highlights에 띄우기

논문 또는 프로젝트에서:

```yaml
highlight: true
```

로 바꾸면 Home의 Highlights 후보가 됩니다. 중요한 성과만 `true`로 두세요.

## 프로젝트

프로젝트의 원래 위치는 **Research**입니다. `data/projects.yml`에서 `status: Ongoing` / `Completed`로 관리합니다. 큰 과제만 `highlight: true`로 설정하면 Home에도 나타납니다.

## People

Home에는 People 섹션이 없습니다. People 메뉴에서만 관리합니다. 졸업 시 Current 항목에서 Alumni로 옮기면 됩니다.


## News 관리

News는 **사진 없이 텍스트 중심**으로 관리합니다. 기본적으로 아래 3개 필드만 있으면 됩니다.

```yaml
- date: 2026.08.10
  category: Publication
  title: A new paper has been published in Journal Name.
```

필요할 때만 짧은 설명이나 외부 링크를 추가할 수 있습니다.

```yaml
  summary: Optional one- or two-sentence description.
  link: https://example.com
```

Home의 **Recent News는 `data/news.yml`의 입력 순서와 관계없이 날짜를 읽어 최신 6개를 자동으로 표시**합니다. News 전체 페이지도 날짜 기준 최신순으로 정렬되고, 연도별 섹션은 데이터에 있는 연도를 기준으로 자동 생성됩니다. 따라서 과거 홈페이지의 News를 옮길 때도 사진을 찾을 필요 없이 날짜 / 분류 / 제목만 입력하면 됩니다.

## 이미지 교체

현재 Research / Publications / People 등에 들어있는 이미지는 디자인 확인용 placeholder입니다. 같은 파일명으로 실제 BNSL 사진/graphical abstract를 덮어쓰거나, 데이터 파일의 `image:` 경로를 새 파일명으로 바꾸면 됩니다. News는 사진 없이 운영하도록 설계했습니다.

## 배포

1. GitHub에 새 repository를 만들고 이 폴더의 내용을 업로드합니다.
2. Settings → Pages → Source를 **GitHub Actions**로 선택합니다.
3. `main`에 Commit하면 `.github/workflows/deploy.yml`이 자동 실행됩니다.
4. 완성 후 `bnsl.yonsei.ac.kr` custom domain을 연결합니다.
