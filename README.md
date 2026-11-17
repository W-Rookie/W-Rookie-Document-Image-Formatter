# W-Rookie

[한국어](#w-rookie) · [English](#w-rookie-english)

[![Tests](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/actions/workflows/tests.yml/badge.svg)](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/W-Rookie/W-Rookie-Document-Image-Formatter?display_name=tag)](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> DOCX 문서를 Windows · macOS · Linux에서 처리하고, Windows에서는 HWP · HWPX까지 지원하는 데스크톱 프로그램

W-Rookie는 문서에 들어 있는 사진을 자동으로 찾아 **가로·세로 실물 크기(mm/cm)**를 맞추고, 가운데 정렬과 **검정 1pt 테두리**를 적용합니다. 여러 파일과 폴더를 한 번에 처리하며, 원본을 보존한 새 파일 저장이 기본값입니다.

- 기본 설정: `스마트 중앙 정렬 + 원본 크기 유지 + 검정 1pt + 새 파일 저장`
- 지원 형식: `.docx`, `.hwp`, `.hwpx`
- 처리 방식: PC 내부 로컬 처리 — 문서 외부 전송 없음
- 대용량 DOCX: 사진 데이터를 메모리에 펼치지 않는 스트리밍 처리

일반 사용자 기능은 하나의 GUI로 통일되어 있습니다. 운영체제별 배포 실행 파일과 소스 설치 명령인 `python -m docpicalign`, `w-rookie`, `w-rookie-gui`는 모두 같은 데스크톱 화면을 실행합니다. 명령줄 인터페이스는 자동화가 필요한 개발자용으로만 별도 제공됩니다.

## 운영체제별 다운로드

아래 파일은 공개 GitHub Release에서 로그인이나 별도 권한 요청 없이 받을 수 있습니다.

- [Windows용 ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-Windows.zip)
- [macOS용 ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-macOS.zip)
- [Linux용 TAR.GZ](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-Linux.tar.gz)
- [전체 소스 ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/archive/refs/tags/v1.4.2.zip)
- [SHA-256 무결성 확인 파일](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/SHA256SUMS.txt)
- [v1.4.2 릴리스 페이지](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/tag/v1.4.2)

---

## 목차

1. [준비 사항](#1-준비-사항)
2. [운영체제별 설치·실행](#2-운영체제별-설치실행)
3. [가장 빠른 사용법](#3-가장-빠른-사용법)
4. [화면과 기능 설명](#4-화면과-기능-설명)
5. [보안 검사](#5-보안-검사)
6. [정렬과 사진 크기](#6-정렬과-사진-크기)
7. [저장 방식과 결과 파일](#7-저장-방식과-결과-파일)
8. [DOCX 사용 시 참고사항](#8-docx-사용-시-참고사항)
9. [HWP/HWPX 사용 시 참고사항](#9-hwphwpx-사용-시-참고사항)
10. [안전하게 테스트하기](#10-안전하게-테스트하기)
11. [대용량 파일 처리](#11-대용량-파일-처리)
12. [오류 해결](#12-오류-해결)
13. [개발·테스트·네이티브 앱 빌드](#13-개발테스트네이티브-앱-빌드)
14. [제한사항](#14-제한사항)
15. [삭제 및 초기화](#15-삭제-및-초기화)

---

## 1. 준비 사항

### 필수 환경

- Windows 10/11, 최신 macOS 또는 데스크톱 Linux 중 하나
- 약 200MB 이상의 설치 여유 공간
- GitHub Release 실행 파일은 Python을 별도로 설치하지 않아도 됩니다.
- 전체 소스로 실행하거나 개발할 때만 Python 3.10 이상이 필요합니다.

| 운영체제 | 지원 문서 | 압축 해제 후 실행 |
|---|---|---|
| Windows | DOCX, HWP, HWPX | `W-Rookie\W-Rookie.exe` |
| macOS | DOCX | `W-Rookie.app` |
| Linux | DOCX | `./W-Rookie/W-Rookie` |

### HWP/HWPX 처리 시 추가로 필요한 것

- 한컴오피스 한/글이 설치된 Windows PC

DOCX만 처리할 때는 Microsoft Word와 한컴오피스가 없어도 됩니다.

---

## 2. 운영체제별 설치·실행

각 운영체제 이름이 붙은 GitHub Release 실행 파일을 내려받아 사용합니다. 별도 Python 설치나 패키지 다운로드는 필요하지 않습니다. 압축 파일 내부에서 실행하지 말고 반드시 먼저 완전히 압축 해제하세요.

### 2-1. Windows 사용 방법

대상 파일: `W-Rookie-v1.4.2-Windows.zip`

#### 준비

1. Windows 10 또는 Windows 11에서 진행합니다.
2. HWP/HWPX도 처리하려면 한컴오피스 한/글을 설치합니다. DOCX만 처리할 때는 Word나 한/글이 필요하지 않습니다.

#### 최초 설치

1. Windows용 ZIP을 마우스 오른쪽 버튼으로 누르고 **모두 압축 풀기**를 선택합니다.
2. 압축을 푼 위치에서 `W-Rookie` 폴더를 엽니다.
3. `W-Rookie.exe`를 더블클릭합니다.
4. 보안 경고가 나타나면 아래의 [운영체제 보안 경고 안내](#2-4-운영체제-보안-경고가-나타날-때)에 따라 파일 출처와 SHA-256을 먼저 확인합니다.

#### 프로그램 실행

1. 압축을 푼 폴더의 `W-Rookie.exe`를 더블클릭합니다.
2. `W-Rookie · 문서 사진 자동 편집` GUI가 나타나면 실행 성공입니다.
3. 다음 실행부터도 같은 `W-Rookie.exe`를 사용합니다.

GUI가 나타나지 않으면 ZIP을 완전히 압축 해제했는지 확인하고, 파일명과 SHA-256이 공식 릴리스와 일치하는지 확인한 뒤 GitHub Issue에 사용한 Windows 버전과 화면의 오류 내용을 남겨주세요.

#### Windows에서 문서 처리

1. 처음에는 중요한 원본이 아닌 테스트용 사본을 준비합니다.
2. **파일 추가** 또는 **폴더 추가**를 눌러 DOCX/HWP/HWPX를 목록에 넣습니다.
3. 일반적인 문서는 **스마트 중앙 정렬(권장)**을 선택합니다.
4. 사진 크기를 바꾸려면 **크기 조절 사용**을 체크합니다.
5. 가로·세로 입력칸에 원하는 수치를 넣고 `mm` 또는 `cm`를 선택합니다. 한쪽만 입력해도 됩니다.
6. 비율을 유지하려면 **원본 비율 유지**를 체크하고, 정확히 두 수치로 늘이려면 체크를 해제합니다.
7. 사진 테두리는 기본값인 `1.0pt`, 검정색을 유지합니다.
8. 저장 방식은 **새 파일로 저장(원본 보존)**을 선택합니다.
9. 가능하면 **Windows Defender 추가 검사(권장)**를 켭니다.
10. **작업 시작**을 누르고 상태가 `완료`로 바뀔 때까지 기다립니다.
11. 원본 폴더에서 `_사진정렬`이 붙은 결과 파일을 열어 크기·정렬·테두리를 확인합니다.

`페이지 가로·세로 중앙`은 사진 개체를 페이지 정중앙으로 옮깁니다. 한 페이지의 여러 사진이 겹칠 수 있으므로 대부분은 스마트 중앙 정렬을 권장합니다.

#### Windows에서 HWP/HWPX가 실패할 때

1. 한컴오피스 한/글을 설치하고 최신 업데이트를 적용합니다.
2. 처리할 문서를 한/글에서 닫습니다.
3. W-Rookie의 **환경 진단**을 실행합니다.
4. 필요하면 **HWP 처리 화면 표시**를 체크하고 다시 처리합니다.

### 2-2. macOS 사용 방법

대상 파일: `W-Rookie-v1.4.2-macOS.zip` — DOCX만 지원합니다.

1. macOS용 ZIP을 완전히 압축 해제합니다.
2. `W-Rookie.app`을 Control-클릭하고 **열기**를 선택합니다.
3. GUI에서 DOCX를 추가하고 필요하면 사진 크기(mm/cm)를 지정한 뒤 스마트 중앙 정렬, 1.0pt, 새 파일 저장으로 처리합니다.

다음 실행부터는 `W-Rookie.app`을 사용합니다. macOS의 보안 확인창이 나타나면 **시스템 설정 → 개인정보 보호 및 보안**에서 차단 내용을 확인하세요. 출처를 모르는 파일에는 보안 예외를 적용하지 마세요.

### 2-3. Linux 사용 방법

대상 파일: `W-Rookie-v1.4.2-Linux.tar.gz` — DOCX만 지원합니다.

1. Linux용 TAR.GZ를 내려받습니다.
2. 파일이 있는 폴더에서 터미널을 엽니다.
3. 다음 명령을 실행합니다.

```bash
tar -xzf W-Rookie-v1.4.2-Linux.tar.gz
chmod +x W-Rookie/W-Rookie
./W-Rookie/W-Rookie
```

다음 실행부터는 `./W-Rookie/W-Rookie`만 실행합니다. 데스크톱 세션과 그래픽 화면이 필요하며, 서버 전용·SSH 전용 환경에서는 GUI가 표시되지 않을 수 있습니다.

### 2-4. 운영체제 보안 경고가 나타날 때

GitHub Actions에서 생성한 실행 파일은 현재 상용 코드 서명 인증서로 서명되지 않았기 때문에 Windows SmartScreen이나 macOS Gatekeeper가 `알 수 없는 게시자` 또는 `확인되지 않은 개발자` 경고를 표시할 수 있습니다.

> **Windows Defender, SmartScreen, Gatekeeper, 방화벽, AppArmor 또는 SELinux를 통째로 끄는 방법은 권장하지 않습니다.** 보안 기능을 끄면 W-Rookie와 관계없는 악성 파일까지 실행될 수 있습니다.

예외 실행 전에는 다음을 먼저 확인하세요.

1. [공식 GitHub Releases](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases)에서 받은 파일인지 확인합니다.
2. 릴리스의 `SHA256SUMS.txt`와 다운로드한 파일의 SHA-256 값이 같은지 확인합니다.
3. 파일명과 버전이 예상한 W-Rookie 릴리스와 일치하는지 확인합니다.
4. 백신이 구체적인 악성코드명을 탐지하면 예외 처리하지 말고 실행을 중단한 뒤 GitHub Issue에 탐지명과 SHA-256을 신고합니다.

#### Windows 10/11

1. ZIP 파일을 우클릭하고 **속성**을 엽니다.
2. 공식 릴리스와 해시가 일치할 때만 하단의 **차단 해제**가 있으면 체크하고 적용합니다.
3. SmartScreen 경고가 나오면 **추가 정보**에서 파일명과 게시자를 다시 확인한 뒤 **실행**을 선택합니다.
4. Defender가 실제 위협을 탐지한 경우 Defender를 끄지 말고 실행을 취소합니다.

PowerShell에서 SHA-256 확인:

```powershell
Get-FileHash .\W-Rookie-v1.4.2-Windows.zip -Algorithm SHA256
```

#### macOS

1. Finder에서 `W-Rookie.app`을 Control-클릭하고 **열기**를 선택합니다.
2. 필요하면 **시스템 설정 → 개인정보 보호 및 보안 → 확인 없이 열기**를 사용합니다.
3. `sudo spctl --master-disable`처럼 Gatekeeper 전체를 끄는 명령은 사용하지 마세요.

터미널에서 SHA-256 확인:

```bash
shasum -a 256 W-Rookie-v1.4.2-macOS.zip
```

#### Linux

공식 TAR.GZ의 해시를 확인한 뒤 `chmod +x W-Rookie/W-Rookie`로 이 프로그램에만 실행 권한을 부여합니다. AppArmor, SELinux 또는 배포판 보안 정책 전체를 비활성화하지 마세요.

```bash
sha256sum W-Rookie-v1.4.2-Linux.tar.gz
```

### 2-5. 개발자용 공통 설치

전체 소스 폴더에서 현재 운영체제의 Python을 사용합니다.

```text
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
w-rookie
```

Windows에서 HWP/HWPX도 사용하려면 `python -m pip install -e ".[hwp]"`로 설치합니다.

---

## 3. 가장 빠른 사용법

처음 사용하는 경우 아래 설정을 그대로 사용하는 것이 가장 안전합니다.

1. Windows는 `W-Rookie.exe`, macOS는 `W-Rookie.app`, Linux는 `./W-Rookie/W-Rookie`를 실행합니다.
2. 프로그램에서 **파일 추가**를 누릅니다.
3. 처리할 문서를 선택합니다. DOCX는 모든 운영체제에서 지원하고 HWP/HWPX는 Windows에서만 지원합니다.
4. 정렬 기준은 **스마트 중앙 정렬(권장)**을 선택합니다.
5. 원본 크기를 유지하려면 **크기 조절 사용**을 끕니다. 바꾸려면 체크한 뒤 가로·세로와 `mm/cm`를 입력합니다.
6. 테두리는 `1.0pt`, 검정색을 유지합니다.
7. 저장 방식은 **새 파일로 저장(원본 보존)**을 선택합니다.
8. **작업 시작**을 누릅니다.
9. 작업이 끝나면 원본 파일 옆의 `_사진정렬` 파일을 확인합니다.

예시:

```text
보고서.docx
└─ 보고서_사진정렬.docx
```

처음에는 중요한 원본이 아닌 사본으로 결과를 확인하세요.

---

## 4. 화면과 기능 설명

### 문서 목록

| 메뉴 | 기능 |
|---|---|
| 파일 추가 | DOCX, HWP, HWPX 파일을 하나 이상 선택합니다. |
| 폴더 추가 | 선택한 폴더와 하위 폴더의 지원 문서를 모두 추가합니다. |
| 선택 제거 | 목록에서 선택한 파일만 제거합니다. 실제 파일은 삭제하지 않습니다. |
| 전체 비우기 | 작업 목록을 비웁니다. 실제 파일은 삭제하지 않습니다. |
| 상태 | 대기, 처리 중, 완료, 실패 상태와 처리한 사진 수를 표시합니다. |

동일한 파일을 여러 번 추가해도 작업 목록에는 한 번만 들어갑니다.

### 정렬 기준

| 설정 | 설명 |
|---|---|
| 스마트 중앙 정렬 | 문단과 표 구조를 유지하며 사진을 자연스럽게 가운데 정렬합니다. |
| 페이지 가로·세로 중앙 | 사진 개체를 페이지 정중앙으로 이동합니다. |

### 사진 크기

| 설정 | 설명 |
|---|---|
| 크기 조절 사용 | 끄면 원본 크기를 유지하고, 켜면 입력한 실물 크기를 적용합니다. |
| 가로 / 세로 | 원하는 사진 크기를 숫자로 입력합니다. 둘 중 하나만 입력해도 됩니다. |
| mm / cm | 입력값의 단위를 선택합니다. 예: `35 mm`, `3.5 cm`는 같은 길이입니다. |
| 원본 비율 유지 | 한쪽 값으로 비례 확대·축소합니다. 양쪽 값이 있으면 그 박스 안의 최대 크기로 맞춥니다. |

두 값을 정확히 그대로 적용해야 한다면 **원본 비율 유지**를 해제하세요. 원본 비율과 다른 값이면 사진이 늘어나거나 눌릴 수 있습니다. 허용 범위는 각 축 `0 초과~1000mm 이하`입니다.

### 사진 테두리

| 설정 | 설명 |
|---|---|
| 두께 | `0.1~12pt` 범위에서 지정합니다. 기본값은 `1.0pt`입니다. |
| 선 색상 | 색상 선택창에서 원하는 RGB 색상을 선택합니다. 기본값은 검정입니다. |

### 기타 옵션

| 옵션 | 설명 |
|---|---|
| 머리글·바닥글의 사진도 처리 | DOCX의 머리글, 바닥글, 각주, 미주 사진까지 처리합니다. |
| HWP 처리 화면 표시 | 한/글 자동화 화면을 표시합니다. HWP 문제 확인 시 사용합니다. |
| 환경 진단 | Python, DOCX 엔진, HWP/HWPX 자동화 연결 상태를 확인합니다. |
| 작업 취소 | 진행 중인 파일 처리를 안전하게 중단합니다. 완성되지 않은 임시 파일은 삭제됩니다. |

---

## 5. 보안 검사

모든 문서는 실제 처리 전에 보안 검사를 통과해야 합니다. 정적 검사는 항상 실행되며 GUI에서 끌 수 없습니다. 위험 판정된 문서는 Word 또는 한/글 자동화로 열기 전에 차단하고 결과 파일을 만들지 않습니다.

### 자동 차단 항목

- VBA 매크로와 HWP 스크립트 저장소
- ActiveX 및 OLE 첨부 개체
- EXE, DLL, BAT, CMD, PowerShell, JavaScript 등 실행 가능한 payload
- `file:`, `javascript:`, `ms-msdt:` 등의 위험한 외부 링크
- 압축 내부 경로 조작과 대소문자 중복 항목
- 암호화되어 내부를 검사할 수 없는 ZIP 항목
- DTD, XML 외부 엔터티와 비정상 XML
- 비정상적으로 높은 압축률과 ZIP 폭탄
- 과도한 항목 수, XML 크기, 압축 해제 예상 크기
- 손상되었거나 형식과 구조가 맞지 않는 문서

### 경고 후 처리 가능한 항목

- 일반 HTTP/HTTPS 외부 링크
- 사용자 지정 Office 리본 구성
- 정적 분석 범위가 제한되는 구형 HWP
- Windows Defender 명령줄 검사를 사용할 수 없는 환경

경고가 있는 파일은 처리 결과 상태줄에 `⚠` 표시와 안내가 나타납니다.

### Windows Defender 추가 검사

GUI의 **Windows Defender 추가 검사(권장)**를 켜면 정적 검사 후 운영체제 백신 검사도 실행합니다.

- 검사 중 자동 치료·삭제를 비활성화해 원본을 임의로 변경하지 않습니다.
- 위협 가능성이 보고되면 문서 처리를 차단합니다.
- Defender를 사용할 수 없으면 정적 검사는 계속 실행하고 경고를 표시합니다.

> 이 기능은 다층 방어를 위한 사전 검사입니다. 완전한 백신이나 샌드박스를 대체하지 않습니다. Windows, Microsoft Defender, Word, 한컴오피스를 최신 상태로 유지하세요.

상단의 **보안 안내** 버튼에서 같은 내용을 언제든 확인할 수 있습니다.

---

## 6. 정렬과 사진 크기

### 스마트 중앙 정렬 — 기본값·권장

- 일반 문단의 사진은 문단 기준 가로 가운데로 정렬합니다.
- 표 안의 사진은 문단 가로 가운데와 표 셀 세로 가운데를 함께 적용합니다.
- 문서의 기존 흐름을 최대한 유지하므로 보고서, 신청서, 점검표에 적합합니다.

### 페이지 가로·세로 중앙

- 사진 개체를 표나 문단 흐름과 무관하게 페이지 정중앙에 놓습니다.
- 표지나 페이지당 대표 사진이 한 장인 문서에 적합합니다.
- 같은 페이지에 사진이 여러 장 있으면 중앙에서 겹칠 수 있습니다.

### 사진의 가로·세로 길이 맞추기

크기를 바꾸지 않으려면 **크기 조절 사용**을 끈 상태로 둡니다. 크기를 바꿀 때는 다음처럼 입력합니다.

| 원하는 결과 | 입력 예시 | 원본 비율 유지 |
|---|---|---|
| 가로 50mm, 세로는 비례 계산 | 가로 `50`, 세로 비움, `mm` | 켬 |
| 세로 3cm, 가로는 비례 계산 | 가로 비움, 세로 `3`, `cm` | 켬 |
| 50×30mm 박스 안에 최대 크기 | 가로 `50`, 세로 `30`, `mm` | 켬 |
| 정확히 50×30mm | 가로 `50`, 세로 `30`, `mm` | 끔 |

**원본 비율 유지**가 켜진 상태에서 두 값을 모두 입력하면 사진을 자르지 않고 지정한 가로×세로 영역 안에 들어가는 가장 큰 크기로 맞춥니다. 두 값을 정확히 고정하면 원본 비율에 따라 왜곡될 수 있으므로 필요한 경우에만 비율 유지를 해제하세요.

### 어떤 설정을 선택해야 하나요?

| 문서 유형 | 권장 설정 |
|---|---|
| 일반 보고서 | 스마트 중앙 정렬 + 비율 유지 |
| 표 안에 사진이 많은 문서 | 스마트 중앙 정렬 + 동일한 가로값 |
| 증명사진 규격처럼 정확한 크기 | 정확한 가로·세로 입력 + 비율 유지 해제 |
| 페이지마다 사진 한 장 | 페이지 가로·세로 중앙 + 비율 유지 |
| 크기는 그대로, 테두리만 적용 | 크기 조절 사용 해제 |

---

## 7. 저장 방식과 결과 파일

### 새 파일로 저장 — 권장

- 원본을 변경하지 않습니다.
- 기본 결과 이름은 `원본이름_사진정렬.확장자`입니다.
- 같은 이름이 이미 있으면 `_2`, `_3`을 자동으로 붙입니다.

```text
보고서.docx
보고서_사진정렬.docx
보고서_사진정렬_2.docx
```

저장 폴더 입력란을 비워 두면 원본과 같은 폴더에 저장합니다. `폴더` 버튼으로 별도의 결과 폴더를 선택할 수도 있습니다.

### 원본 덮어쓰기

- 결과 파일로 원본을 교체합니다.
- 저장이 끝나기 전에는 임시 파일을 사용하므로 중간 실패로 인한 손상을 줄입니다.
- 충분히 테스트하고 별도 백업이 있을 때만 사용하세요.

---

## 8. DOCX 사용 시 참고사항

- Microsoft Word가 설치되지 않아도 처리할 수 있습니다.
- 최신 DrawingML 사진과 구형 VML 사진을 처리합니다.
- 입력한 mm/cm를 OOXML 표준 단위(EMU)로 변환해 사진 표시 크기를 저장합니다.
- 테두리 1pt는 OOXML 규격의 정확한 `12700 EMU`로 저장됩니다.
- 사진 바이너리를 다시 인코딩하지 않으므로 원본 화질이 유지됩니다.
- 선택 시 머리글, 바닥글, 각주, 미주의 사진도 처리합니다.
- 결과 파일은 ZIP 구조 검사와 XML 안전 검사를 거쳐 저장됩니다.

사진과 일반 글자가 같은 문단에 있으면 해당 문단 전체가 가운데 정렬될 수 있습니다. 중요한 혼합 문단은 사본으로 먼저 확인하세요.

---

## 9. HWP/HWPX 사용 시 참고사항

HWP/HWPX는 설치된 한컴오피스 한/글의 공식 Windows 자동화 기능을 사용합니다.

### 처리 전 확인

1. 한컴오피스 한/글을 설치합니다.
2. W-Rookie의 **환경 진단**을 누릅니다.
3. `HWP/HWPX 엔진: 한/글 자동화 연결 정상`인지 확인합니다.
4. 작은 HWP 사본으로 먼저 시험합니다.

사진 크기는 한/글 내부 단위로 변환해 적용합니다. 한/글 버전과 개체 속성에 따라 화면에 표시되는 반올림 값이 아주 조금 다를 수 있으므로 규격이 중요한 문서는 결과 파일의 **개체 속성**에서 최종 수치를 확인하세요.

### 1pt 테두리 차이

한/글의 테두리 두께는 단계형 값입니다. 따라서 1pt에 가장 가까운 **0.4mm(약 1.13pt)**로 적용됩니다. 이 변환이 발생하면 작업 결과에 안내가 표시됩니다.

| 형식 | 1pt 처리 방식 |
|---|---|
| DOCX | 정확한 1pt |
| HWP/HWPX | 한/글 지원값 중 가장 가까운 0.4mm |

### 한/글 보안 확인창이 나타날 때

- `HWP 처리 화면 표시`를 체크합니다.
- 다시 작업을 시작합니다.
- 한/글에서 파일 접근을 허용합니다.
- 회사 보안 정책으로 자동화가 차단된 PC에서는 관리자 확인이 필요할 수 있습니다.

---

## 10. 안전하게 테스트하기

### 합성 샘플 문서 만들기

실제 개인정보 없이 시험할 수 있는 DOCX를 생성합니다.

```bat
.venv\Scripts\python scripts\create_sample.py sample_before.docx
```

생성된 `sample_before.docx`를 프로그램에 추가하고 기본 설정으로 처리하세요.

확인 항목:

- 일반 문단의 사진이 가로 가운데인지
- 표 안의 사진이 셀 가운데인지
- 입력한 사진 가로·세로 길이가 맞는지
- 검정 테두리가 적용됐는지
- Word에서 복구 경고 없이 열리는지
- 원본 파일이 그대로 남아 있는지

### 자동 테스트

```bat
test.bat
```

자동 테스트는 다음을 검사합니다.

- 스마트 중앙 정렬과 페이지 가로·세로 중앙 배치
- mm/cm 변환, 비율 유지, 정확한 가로·세로 크기
- 정확한 DOCX 1pt 테두리
- 표 셀 세로 가운데 정렬
- 구형 VML 사진
- 사진 바이너리 SHA-256 보존
- 반복 실행 시 속성 중복 방지
- 손상 파일과 작업 취소 보호
- 결과 파일 이름 충돌 방지
- HWP 자동화 매개변수
- 매크로, ActiveX, OLE, 위험 링크와 실행 payload 차단
- ZIP 경로 조작, XML 엔터티와 압축 폭탄 방어

---

## 11. 대용량 파일 처리

DOCX는 내부적으로 ZIP 형식입니다. W-Rookie는 사진·영상 같은 `word/media` 데이터를 1MB 단위로 복사하고, 수정 대상 XML만 메모리에 올립니다.

- 사진 전체를 RAM에 중복 로딩하지 않습니다.
- 대용량 미디어를 복사하는 동안에도 진행률을 갱신합니다.
- 파일 사이 또는 복사 중 작업 취소를 확인합니다.
- ZIP64를 사용해 4GB 초과 패키지 구조를 지원합니다.
- GUI 처리는 백그라운드 스레드에서 실행됩니다.

대용량 스트레스 테스트:

```bat
.venv\Scripts\python scripts\stress_test.py --size-mb 512
```

HWP/HWPX의 실제 메모리 사용량은 설치된 한/글 버전에 따라 달라집니다. 처리 중에는 다른 무거운 프로그램을 줄이고 충분한 디스크 공간을 확보하세요.

---

## 12. 오류 해결

### `py` 또는 Python을 찾을 수 없습니다

Python 3.10 이상을 설치한 뒤 Windows를 다시 시작하세요. 설치 첫 화면에서 가능하면 다음 항목을 체크합니다.

- `Add python.exe to PATH`
- `Install launcher for all users` 또는 Python Launcher

버전 확인:

```bat
py -3 --version
python --version
```

둘 중 하나에서 `Python 3.10` 이상의 버전이 나오면 됩니다.

### `W-Rookie.exe`를 실행해도 GUI가 나타나지 않습니다

ZIP 내부에서 직접 실행하지 말고 새 폴더에 완전히 압축을 풉니다.

1. 공식 GitHub Release에서 Windows ZIP을 다시 내려받습니다.
2. `SHA256SUMS.txt`와 파일 해시가 일치하는지 확인합니다.
3. ZIP 속성에 **차단 해제**가 있으면 공식 파일임을 확인한 뒤 적용합니다.
4. **모두 압축 풀기**를 사용하고 `W-Rookie\W-Rookie.exe`를 실행합니다.
5. 실제 악성코드 탐지명이 표시되면 보안 기능을 끄지 말고 실행을 중단합니다.

그래도 실행되지 않으면 GitHub Issue에 Windows 버전, W-Rookie 버전, 화면에 표시된 오류와 SHA-256을 남겨주세요. 개인 문서나 개인정보가 포함된 화면은 첨부하지 마세요.

### HWP/HWPX만 실패합니다

1. 한컴오피스 한/글이 설치됐는지 확인합니다.
2. 프로그램에서 **환경 진단**을 실행합니다.
3. `HWP 처리 화면 표시`를 체크합니다.
4. 처리할 HWP 파일을 한/글에서 닫고 다시 시도합니다.

### 파일 접근 권한 또는 저장 오류가 발생합니다

- Word나 한/글에서 원본과 기존 결과 파일을 닫습니다.
- 읽기 전용 폴더가 아닌 문서 폴더에서 시험합니다.
- 네트워크 드라이브라면 먼저 로컬 폴더에 복사해 시험합니다.
- 저장 공간이 충분한지 확인합니다.

### 보안 검사에서 파일이 차단됩니다

- 차단된 파일은 우회 처리하지 마세요.
- 신뢰할 수 있는 작성자에게 매크로, OLE, ActiveX를 제거한 새 문서를 요청하세요.
- Word 또는 한/글의 최신 버전에서 새 DOCX/HWPX로 다시 저장한 뒤 검사하세요.
- 오탐이 의심되어도 원본은 별도 격리하고 회사 보안 담당자나 백신으로 먼저 확인하세요.
- W-Rookie에는 보안 검사를 끄는 GUI 옵션이 없습니다.

### 사진을 찾지 못했다고 나옵니다

다음 개체는 일반 사진으로 인식되지 않을 수 있습니다.

- OLE 개체
- 차트
- 그룹 안의 특수 도형
- 문서 배경 이미지
- 링크가 끊긴 외부 개체

사진을 Word 또는 한/글의 일반 그림 개체로 다시 삽입한 뒤 시험하세요.

### 페이지 중앙에서 사진이 겹칩니다

페이지 가로·세로 중앙은 모든 사진을 페이지 정중앙으로 이동합니다. 사진이 여러 장인 페이지는 스마트 중앙 정렬을 사용하세요.

### 입력한 가로·세로와 결과가 다릅니다

- **원본 비율 유지**가 켜져 있고 두 값을 모두 입력하면 지정한 박스 안에 맞추므로 한쪽 길이가 입력값보다 작아질 수 있습니다.
- 두 값을 정확히 적용하려면 **원본 비율 유지**를 해제합니다. 이 경우 사진이 왜곡될 수 있습니다.
- HWP/HWPX는 한/글 내부 단위로 반올림되므로 극히 작은 차이가 생길 수 있습니다.

### Word에서 복구 메시지가 나타납니다

- 원본을 보존하고 결과 파일만 닫습니다.
- 같은 문서를 스마트 중앙 정렬로 다시 시험합니다.
- 개인정보를 제거한 최소 재현 문서를 만들어 이슈에 첨부하세요.
- 원본을 덮어쓰지 마세요.

---

## 13. 개발·테스트·네이티브 앱 빌드

### 개발 환경 설치

```bat
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e ".[hwp,dev]"
```

일반 실행 명령은 모두 GUI를 엽니다.

```bat
w-rookie
w-rookie-gui
```

자동화용 CLI는 개발자용 별도 명령입니다.

```bat
w-rookie-cli --help
```

### 품질 검사

```bat
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\ruff check run_gui.pyw src tests scripts
.venv\Scripts\ruff format --check run_gui.pyw src tests scripts
```

### Windows 실행 파일 만들기

```bat
build.bat
```

빌드 결과:

```text
dist\W-Rookie\W-Rookie.exe
```

한컴오피스는 실행 파일에 포함되지 않습니다. HWP/HWPX를 처리할 PC에 별도로 설치해야 합니다.

### macOS/Linux 실행 파일 만들기

```bash
./build.sh
```

현재 운영체제용 결과가 `dist` 폴더에 생성됩니다. 다른 운영체제의 실행 파일은 교차 빌드하지 않고 해당 운영체제의 GitHub Actions 러너에서 각각 생성합니다.

### GitHub 자동 테스트

`.github/workflows/tests.yml`이 Windows, macOS, Ubuntu와 Python 3.10/3.12 조합에서 다음 작업을 실행합니다.

- 단위 테스트
- Ruff 정적 검사
- Ruff 포맷 검사

`v*` 태그를 푸시하면 `.github/workflows/release.yml`이 Windows ZIP, macOS 앱 ZIP, Linux tar.gz를 각 운영체제에서 네이티브 빌드하고 GitHub Release에 첨부합니다.

최근 검증 결과와 Windows 출시 전 확인 사항은 [테스트 보고서](docs/TEST_REPORT.md)를 참고하세요.

---

## 14. 제한사항

- 암호가 설정된 문서는 처리하지 않습니다.
- 구형 `.doc` 파일은 지원하지 않습니다. Word에서 `.docx`로 저장한 뒤 사용하세요.
- OLE, 차트, 그룹 안의 특수 도형은 사진으로 취급하지 않습니다.
- 스마트 중앙 정렬에서 사진과 텍스트가 같은 문단에 있으면 문단 전체가 가운데 정렬될 수 있습니다.
- 페이지 가로·세로 중앙은 같은 페이지의 여러 사진을 정중앙에서 겹치게 할 수 있습니다.
- 비율 유지를 해제하고 원본 비율과 다른 가로·세로 값을 입력하면 사진이 왜곡됩니다.
- HWP/HWPX 자동화는 Windows와 설치된 한/글이 필요합니다.
- 회사 보안 정책에 따라 한/글 자동화가 제한될 수 있습니다.
- 정적 검사와 Windows Defender 검사는 다층 방어이며, 모든 신종 악성코드를 완벽히 보장하지는 않습니다.

---

## 15. 삭제 및 초기화

### 프로그램 삭제

프로젝트 폴더와 그 안의 `.venv` 폴더를 삭제하면 됩니다. 문서 결과 파일은 별도로 삭제하지 않는 한 유지됩니다.

### 저장된 설정까지 초기화

다음 폴더를 삭제합니다.

```text
Windows:
%APPDATA%\WRookie

macOS:
~/Library/Application Support/WRookie

Linux:
~/.config/WRookie
```

다음 실행 시 기본 설정으로 다시 시작합니다.

---

## 개인정보와 안전

- 문서와 사진을 외부 서버에 업로드하지 않습니다.
- 새 파일 저장이 기본값입니다.
- 임시 파일이 완성된 뒤 최종 결과로 교체합니다.
- 실패하거나 취소한 작업의 미완성 임시 파일은 삭제합니다.
- 테스트 문서를 공유할 때는 개인정보와 회사 정보를 제거하세요.

## 프로젝트 구조

```text
src/docpicalign/
├─ app.py                 # 데스크톱 GUI
├─ cli.py                 # 개발자용 명령줄 인터페이스
├─ security.py            # 문서 사전 보안 검사
├─ service.py             # 형식별 처리 라우팅
└─ processors/
   ├─ docx.py             # 저메모리 OOXML 처리 엔진
   └─ hwp.py              # 한/글 COM 자동화 엔진
tests/                    # 자동 테스트
scripts/create_sample.py  # 합성 DOCX 생성기
scripts/stress_test.py    # 대용량 스트레스 테스트
```

## 라이선스

[MIT License](LICENSE)

---

<a id="w-rookie-english"></a>

# W-Rookie — English

[한국어](#w-rookie) · [English](#w-rookie-english)

> A cross-platform desktop application for processing DOCX documents on Windows, macOS, and Linux, with additional HWP and HWPX support on Windows

W-Rookie automatically finds pictures in documents, adjusts their **physical width and height in mm or cm**, centers them, and applies a **1 pt black border**. It can process multiple files or folders in one batch and saves the results as new files by default, preserving the originals.

- Default configuration: `Smart Center + Keep Original Size + Black 1 pt Border + Save as New File`
- Supported formats: `.docx`, `.hwp`, `.hwpx`
- Local processing: documents are not uploaded to an external server
- Large DOCX support: media data is streamed instead of being fully expanded in memory

All regular user features are available through the same GUI. The operating-system release executables and the source-install commands `python -m docpicalign`, `w-rookie`, and `w-rookie-gui` open the same desktop interface. A separate command-line interface is available only for developers who need automation.

## Downloads by operating system

The following files are hosted on the public GitHub Release and can be downloaded without signing in or requesting access.

- [Windows ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-Windows.zip)
- [macOS ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-macOS.zip)
- [Linux TAR.GZ](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/W-Rookie-v1.4.2-Linux.tar.gz)
- [Complete source ZIP](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/archive/refs/tags/v1.4.2.zip)
- [SHA-256 checksum file](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/download/v1.4.2/SHA256SUMS.txt)
- [v1.4.2 release page](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases/tag/v1.4.2)

---

## English table of contents

1. [Requirements](#en-1-requirements)
2. [Installation and launch by operating system](#en-2-installation-and-launch-by-operating-system)
3. [Quick start](#en-3-quick-start)
4. [GUI and features](#en-4-gui-and-features)
5. [Security scanning](#en-5-security-scanning)
6. [Alignment and picture size](#en-6-alignment-and-picture-size)
7. [Saving and output files](#en-7-saving-and-output-files)
8. [DOCX notes](#en-8-docx-notes)
9. [HWP and HWPX notes](#en-9-hwp-and-hwpx-notes)
10. [Safe testing](#en-10-safe-testing)
11. [Large-file processing](#en-11-large-file-processing)
12. [Troubleshooting](#en-12-troubleshooting)
13. [Development, testing, and native builds](#en-13-development-testing-and-native-builds)
14. [Limitations](#en-14-limitations)
15. [Uninstallation and reset](#en-15-uninstallation-and-reset)

---

<a id="en-1-requirements"></a>

## 1. Requirements

### Required environment

- Windows 10/11, a current macOS release, or desktop Linux
- Approximately 200 MB or more of free space for installation
- GitHub Release executables do not require a separate Python installation.
- Python 3.10 or later is required only for running from source or development.

| Operating system | Supported documents | Launch after extraction |
|---|---|---|
| Windows | DOCX, HWP, HWPX | `W-Rookie\W-Rookie.exe` |
| macOS | DOCX | `W-Rookie.app` |
| Linux | DOCX | `./W-Rookie/W-Rookie` |

### Additional requirements for HWP/HWPX

- A Windows PC with Hancom Office Hangul installed

Microsoft Word and Hancom Office are not required when processing DOCX files only.

---

<a id="en-2-installation-and-launch-by-operating-system"></a>

## 2. Installation and launch by operating system

Download the GitHub Release executable for your operating system. No separate Python installation or package download is required. Do not run W-Rookie from inside an archive; fully extract it first.

### 2-1. Windows instructions

Package: `W-Rookie-v1.4.2-Windows.zip`

#### Preparation

1. Use Windows 10 or Windows 11.
2. Install Hancom Office Hangul if you also need HWP/HWPX support. Word or Hangul is not required for DOCX-only use.

#### First-time installation

1. Right-click the Windows ZIP and select **Extract All**.
2. Open the `W-Rookie` folder in the extracted location.
3. Double-click `W-Rookie.exe`.
4. If a security warning appears, first verify the source and SHA-256 as described under [operating-system security warnings](#2-4-when-the-operating-system-displays-a-security-warning).

#### Launching the program

1. Double-click `W-Rookie.exe` in the extracted folder.
2. The launch succeeded when the `W-Rookie · Document Picture Auto Editor` GUI appears.
3. Use the same `W-Rookie.exe` for later launches.

If the GUI does not appear, confirm that the ZIP was fully extracted and that its filename and SHA-256 match the official release. Then open a GitHub Issue with your Windows version and the displayed error.

#### Processing documents on Windows

1. Start with a test copy rather than an important original document.
2. Use **Add Files** or **Add Folder** to add DOCX, HWP, or HWPX documents.
3. Select **Smart Center (Recommended)** for typical documents.
4. To change picture dimensions, enable **Resize Pictures**.
5. Enter the required width and height, then select `mm` or `cm`. You may enter only one dimension.
6. Enable **Keep Aspect Ratio** for proportional resizing. Disable it only when both exact dimensions must be forced.
7. Keep the default picture border at black and `1.0 pt`.
8. Select **Save as New File (Preserve Original)**.
9. Enable **Additional Windows Defender Scan (Recommended)** when available.
10. Select **Start Processing** and wait until the status changes to `Completed`.
11. Open the output file with `_사진정렬` in the original folder and check its dimensions, alignment, and border.

**Center on Page Horizontally and Vertically** places every picture object in the exact center of its page. Multiple pictures on the same page may overlap, so Smart Center is recommended for most documents.

#### If HWP/HWPX processing fails on Windows

1. Install Hancom Office Hangul and apply its latest updates.
2. Close the document in Hangul before processing it.
3. Run **Environment Diagnostics** in W-Rookie.
4. If necessary, enable **Show HWP Processing Window** and try again.

### 2-2. macOS instructions

Package: `W-Rookie-v1.4.2-macOS.zip` — DOCX only.

1. Fully extract the macOS ZIP.
2. Control-click `W-Rookie.app` and select **Open**.
3. Add DOCX files in the GUI, optionally set their dimensions in mm/cm, and process them with Smart Center, a 1.0 pt border, and Save as New File.

Use `W-Rookie.app` for later launches. If macOS shows a security prompt, inspect it under **System Settings → Privacy & Security**. Never add a security exception for a file from an unknown source.

### 2-3. Linux instructions

Package: `W-Rookie-v1.4.2-Linux.tar.gz` — DOCX only.

1. Download the Linux TAR.GZ.
2. Open a terminal in the download folder.
3. Run:

```bash
tar -xzf W-Rookie-v1.4.2-Linux.tar.gz
chmod +x W-Rookie/W-Rookie
./W-Rookie/W-Rookie
```

For later launches, run only `./W-Rookie/W-Rookie`. A graphical desktop session is required; the GUI may not appear in a server-only or SSH-only environment.

### 2-4. When the operating system displays a security warning

Executables produced by GitHub Actions are not currently signed with a commercial code-signing certificate. Windows SmartScreen or macOS Gatekeeper may therefore display an `Unknown publisher` or `Unidentified developer` warning.

> **Do not disable Windows Defender, SmartScreen, Gatekeeper, your firewall, AppArmor, or SELinux globally.** Disabling these protections may allow unrelated malicious files to run.

Before allowing W-Rookie to run, verify all of the following:

1. Confirm that the file came from the [official GitHub Releases page](https://github.com/W-Rookie/W-Rookie-Document-Image-Formatter/releases).
2. Compare the downloaded file's SHA-256 value with the release's `SHA256SUMS.txt`.
3. Confirm that the filename and version match the W-Rookie release you intended to download.
4. If antivirus software reports a specific malware name, do not create an exception. Stop and report the detection name and SHA-256 value in a GitHub Issue.

#### Windows 10/11

1. Right-click the ZIP file and open **Properties**.
2. Only after the official release and hash have been verified, select **Unblock** if that option appears, then apply the change.
3. If SmartScreen appears, select **More info**, verify the filename and publisher information again, and then choose **Run anyway**.
4. If Defender detects an actual threat, do not disable Defender; cancel the launch.

Check SHA-256 in PowerShell:

```powershell
Get-FileHash .\W-Rookie-v1.4.2-Windows.zip -Algorithm SHA256
```

#### macOS

1. In Finder, Control-click `W-Rookie.app` and select **Open**.
2. If necessary, use **System Settings → Privacy & Security → Open Anyway**.
3. Do not use commands such as `sudo spctl --master-disable`, which disable Gatekeeper globally.

Check SHA-256 in Terminal:

```bash
shasum -a 256 W-Rookie-v1.4.2-macOS.zip
```

#### Linux

After verifying the official archive's hash, use `chmod +x W-Rookie/W-Rookie` to grant execute permission only to W-Rookie. Do not disable AppArmor, SELinux, or your distribution's security policy.

```bash
sha256sum W-Rookie-v1.4.2-Linux.tar.gz
```

### 2-5. Common developer installation

Use the Python installation for your current operating system from the complete source directory.

```text
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e .
w-rookie
```

On Windows, install with `python -m pip install -e ".[hwp]"` to enable HWP/HWPX support.

---

<a id="en-3-quick-start"></a>

## 3. Quick start

For a first run, keeping the following defaults is the safest approach.

1. Launch `W-Rookie.exe` on Windows, `W-Rookie.app` on macOS, or `./W-Rookie/W-Rookie` on Linux.
2. Select **Add Files**.
3. Select the documents to process. DOCX is supported on all operating systems; HWP/HWPX is supported only on Windows.
4. Select **Smart Center (Recommended)**.
5. Leave **Resize Pictures** disabled to keep the original size. To resize, enable it and enter the width and height in `mm` or `cm`.
6. Keep the border at black and `1.0 pt`.
7. Select **Save as New File (Preserve Original)**.
8. Select **Start Processing**.
9. When processing finishes, inspect the `_사진정렬` file next to the original.

Example:

```text
report.docx
└─ report_사진정렬.docx
```

Always validate the result with a copy before processing an important original.

---

<a id="en-4-gui-and-features"></a>

## 4. GUI and features

### Document list

| Control | Function |
|---|---|
| Add Files | Select one or more DOCX, HWP, or HWPX files. |
| Add Folder | Add every supported document in the selected folder and its subfolders. |
| Remove Selected | Remove only selected items from the work list. It does not delete files. |
| Clear All | Clear the work list. It does not delete files. |
| Status | Show queued, processing, completed, or failed status and the number of pictures processed. |

Adding the same file more than once still creates only one work-list entry.

### Alignment mode

| Setting | Description |
|---|---|
| Smart Center | Center pictures naturally while preserving paragraph and table structure. |
| Center on Page Horizontally and Vertically | Move each picture object to the exact center of the page. |

### Picture size

| Setting | Description |
|---|---|
| Resize Pictures | Disabled: preserve original dimensions. Enabled: apply the entered physical dimensions. |
| Width / Height | Enter numeric dimensions. Either field may be left blank. |
| mm / cm | Select the unit. For example, `35 mm` and `3.5 cm` are equal. |
| Keep Aspect Ratio | Resize proportionally from one dimension. With both dimensions, fit the largest possible size inside that box. |

Disable **Keep Aspect Ratio** only when both exact dimensions must be applied. If they differ from the original ratio, the picture may appear stretched or compressed. Each dimension must be greater than `0` and no greater than `1000 mm`.

### Picture border

| Setting | Description |
|---|---|
| Thickness | Set a value from `0.1` to `12 pt`. The default is `1.0 pt`. |
| Line Color | Select any RGB color. The default is black. |

### Other options

| Option | Description |
|---|---|
| Process Header and Footer Pictures | Also process pictures in DOCX headers, footers, footnotes, and endnotes. |
| Show HWP Processing Window | Show the Hangul automation window for diagnosing HWP problems. |
| Environment Diagnostics | Check Python, the DOCX engine, and HWP/HWPX automation connectivity. |
| Cancel | Safely stop active processing. Incomplete temporary files are removed. |

---

<a id="en-5-security-scanning"></a>

## 5. Security scanning

Every document must pass a security scan before processing. Static scanning always runs and cannot be disabled in the GUI. A document classified as dangerous is blocked before Word or Hangul automation can open it, and no output is created.

### Automatically blocked content

- VBA macros and HWP script storage
- ActiveX and embedded OLE objects
- Executable payloads such as EXE, DLL, BAT, CMD, PowerShell, and JavaScript
- Dangerous external links using schemes such as `file:`, `javascript:`, or `ms-msdt:`
- Path traversal and case-insensitive duplicate entries inside archives
- Encrypted ZIP entries that cannot be inspected
- DTDs, XML external entities, and malformed XML
- Abnormally high compression ratios and ZIP bombs
- Excessive entry counts, XML size, or expected extracted size
- Corrupt documents or documents whose structure does not match their format

### Content that produces a warning but may be processed

- Regular HTTP/HTTPS external links
- Custom Office ribbon configuration
- Legacy HWP files for which static analysis is limited
- Environments where Windows Defender command-line scanning is unavailable

A file with warnings displays a `⚠` marker and explanation in the result status.

### Additional Windows Defender scan

When **Additional Windows Defender Scan (Recommended)** is enabled, the operating system antivirus scan runs after static analysis.

- Automatic remediation and deletion are disabled so the original is not changed unexpectedly.
- Processing is blocked when a possible threat is reported.
- If Defender is unavailable, static scanning continues and a warning is displayed.

> This is a pre-processing layer in a defense-in-depth design. It does not replace a complete antivirus product or sandbox. Keep Windows, Microsoft Defender, Word, and Hancom Office up to date.

The same information is always available from the **Security Information** button at the top of the GUI.

---

<a id="en-6-alignment-and-picture-size"></a>

## 6. Alignment and picture size

### Smart Center — default and recommended

- Pictures in regular paragraphs are centered horizontally within their paragraphs.
- Pictures in tables receive horizontal paragraph alignment and vertical table-cell alignment.
- This mode preserves the existing document flow as much as possible, making it suitable for reports, forms, and checklists.

### Center on Page Horizontally and Vertically

- Places a picture object in the exact center of the page, independently of its table or paragraph flow.
- Suitable for covers or documents with one primary picture per page.
- Multiple pictures on the same page may overlap in the center.

### Setting picture width and height

Leave **Resize Pictures** disabled to preserve existing dimensions. To resize, use the following patterns.

| Desired result | Example input | Keep Aspect Ratio |
|---|---|---|
| Width 50 mm, proportional height | Width `50`, height blank, `mm` | On |
| Height 3 cm, proportional width | Width blank, height `3`, `cm` | On |
| Largest size inside a 50 × 30 mm box | Width `50`, height `30`, `mm` | On |
| Exactly 50 × 30 mm | Width `50`, height `30`, `mm` | Off |

When **Keep Aspect Ratio** is enabled and both values are provided, the picture is fitted inside the specified width × height area without cropping. Disable aspect-ratio preservation only when both dimensions must be forced, because doing so may distort the picture.

### Recommended settings by document type

| Document type | Recommended setting |
|---|---|
| General report | Smart Center + Keep Aspect Ratio |
| Document with many pictures in tables | Smart Center + consistent width |
| Exact ID-photo-style dimensions | Exact width and height + Keep Aspect Ratio off |
| One picture per page | Center on Page + Keep Aspect Ratio |
| Keep size and add only a border | Resize Pictures off |

---

<a id="en-7-saving-and-output-files"></a>

## 7. Saving and output files

### Save as New File — recommended

- The original is not modified.
- The default output name is `original-name_사진정렬.extension`.
- If the name already exists, `_2`, `_3`, and so on are added automatically.

```text
report.docx
report_사진정렬.docx
report_사진정렬_2.docx
```

Leave the output-folder field blank to save beside the original. You can also select a separate destination with the **Folder** button.

### Overwrite Original

- Replaces the original with the completed result.
- A temporary file is used until saving finishes, reducing the risk of corruption from an interrupted operation.
- Use this only after sufficient testing and when a separate backup exists.

---

<a id="en-8-docx-notes"></a>

## 8. DOCX notes

- Microsoft Word is not required.
- Both current DrawingML pictures and legacy VML pictures are processed.
- Entered mm/cm values are converted to the OOXML standard unit, EMU.
- A 1 pt border is stored as exactly `12700 EMU` under the OOXML specification.
- Picture binaries are not re-encoded, preserving their original image quality.
- Headers, footers, footnotes, and endnotes can optionally be processed.
- Output files pass ZIP structure and XML safety validation before being saved.

If a paragraph contains both a picture and regular text, the whole paragraph may become centered. Test important mixed-content paragraphs with a copy first.

---

<a id="en-9-hwp-and-hwpx-notes"></a>

## 9. HWP and HWPX notes

HWP/HWPX processing uses the official Windows automation interface of the installed Hancom Office Hangul application.

### Before processing

1. Install Hancom Office Hangul.
2. Select **Environment Diagnostics** in W-Rookie.
3. Confirm that the HWP/HWPX engine reports a successful Hangul automation connection.
4. Test with a small copy of an HWP document first.

Picture dimensions are converted to Hangul's internal units. Displayed values may differ slightly due to rounding by the installed Hangul version or object properties. For documents with strict specifications, verify the final values under the output object's **Properties**.

### Difference in 1 pt borders

Hangul supports border thicknesses as discrete steps. W-Rookie therefore applies **0.4 mm (approximately 1.13 pt)**, the closest supported value to 1 pt. The result reports when this conversion occurs.

| Format | Handling of 1 pt |
|---|---|
| DOCX | Exact 1 pt |
| HWP/HWPX | Closest Hangul-supported value: 0.4 mm |

### If a Hangul security prompt appears

- Enable **Show HWP Processing Window**.
- Start the task again.
- Allow file access in Hangul.
- A company-managed PC may require administrator assistance if its security policy blocks automation.

---

<a id="en-10-safe-testing"></a>

## 10. Safe testing

### Create a synthetic sample document

Generate a DOCX test file that contains no real personal information.

```bat
.venv\Scripts\python scripts\create_sample.py sample_before.docx
```

Add `sample_before.docx` to W-Rookie and process it with the defaults.

Verify that:

- Pictures in regular paragraphs are horizontally centered.
- Pictures in tables are centered within their cells.
- The requested width and height are correct.
- A black border is present.
- Word opens the output without a recovery warning.
- The original file remains unchanged.

### Automated tests

```bat
test.bat
```

The automated suite covers:

- Smart Center and page-center placement
- mm/cm conversion, aspect-ratio preservation, and exact dimensions
- Exact 1 pt DOCX borders
- Vertical table-cell alignment
- Legacy VML pictures
- Preservation of picture binary SHA-256 values
- Prevention of duplicate properties across repeated runs
- Protection against corrupt files and cancelled operations
- Output-name collision handling
- HWP automation parameters
- Blocking macros, ActiveX, OLE, dangerous links, and executable payloads
- Protection against ZIP path traversal, XML entities, and compression bombs

---

<a id="en-11-large-file-processing"></a>

## 11. Large-file processing

A DOCX document is internally a ZIP package. W-Rookie copies `word/media` data such as pictures and video in 1 MB chunks and loads only the XML that must be modified into memory.

- Complete picture data is not duplicated in RAM.
- Progress continues to update while large media is copied.
- Cancellation is checked between files and during copying.
- ZIP64 supports package structures larger than 4 GB.
- GUI processing runs on a background thread.

Large-file stress test:

```bat
.venv\Scripts\python scripts\stress_test.py --size-mb 512
```

Actual memory use for HWP/HWPX depends on the installed Hangul version. Close other resource-intensive applications and ensure that sufficient disk space is available.

---

<a id="en-12-troubleshooting"></a>

## 12. Troubleshooting

### `py` or Python cannot be found

Install Python 3.10 or later and restart Windows. If available on the first installer screen, select:

- `Add python.exe to PATH`
- `Install launcher for all users` or Python Launcher

Check the version:

```bat
py -3 --version
python --version
```

Either command may be used if it reports Python 3.10 or later.

### The GUI does not appear after launching `W-Rookie.exe`

Do not run the executable from inside the ZIP. Fully extract it into a new folder.

1. Download the Windows ZIP again from the official GitHub Release.
2. Verify its hash against `SHA256SUMS.txt`.
3. If ZIP Properties shows **Unblock**, apply it only after verifying the official file.
4. Use **Extract All**, then launch `W-Rookie\W-Rookie.exe`.
5. If a specific malware detection is reported, do not disable security software; cancel the launch.

If it still does not launch, open a GitHub Issue with your Windows version, W-Rookie version, displayed error, and SHA-256. Do not attach screenshots containing private documents or personal information.

### Only HWP/HWPX processing fails

1. Confirm that Hancom Office Hangul is installed.
2. Run **Environment Diagnostics**.
3. Enable **Show HWP Processing Window**.
4. Close the HWP file in Hangul and try again.

### A file-access or save error occurs

- Close the original and any existing output in Word or Hangul.
- Test in a normal document folder rather than a read-only location.
- For a network drive, copy the document to a local folder first.
- Confirm that sufficient storage space is available.

### A file is blocked by security scanning

- Do not bypass processing for a blocked file.
- Ask the trusted author for a new copy with macros, OLE, and ActiveX removed.
- Open the source in the latest Word or Hangul and save it as a new DOCX/HWPX before scanning again.
- Even if you suspect a false positive, isolate the original and have your security team or antivirus product inspect it first.
- W-Rookie does not provide a GUI option to disable security scanning.

### No pictures are found

The following objects may not be recognized as regular pictures:

- OLE objects
- Charts
- Special shapes inside groups
- Document background images
- Broken externally linked objects

Reinsert the image as a regular picture in Word or Hangul and try again.

### Pictures overlap in the center of a page

Page Center moves every picture to the exact center. Use Smart Center on pages containing multiple pictures.

### Output dimensions differ from the entered width and height

- With **Keep Aspect Ratio** enabled and both dimensions entered, the picture fits inside the specified box, so one dimension may be smaller than its input value.
- Disable **Keep Aspect Ratio** to force both exact values. This may distort the picture.
- HWP/HWPX dimensions may differ by a very small amount due to Hangul's internal rounding.

### Word displays a recovery message

- Preserve the original and close only the output.
- Try the same document again with Smart Center.
- Remove personal information from a minimal reproduction document before attaching it to an Issue.
- Do not overwrite the original.

---

<a id="en-13-development-testing-and-native-builds"></a>

## 13. Development, testing, and native builds

### Set up a development environment

```bat
py -3 -m venv .venv
.venv\Scripts\python -m pip install -e ".[hwp,dev]"
```

The regular launch commands both open the GUI:

```bat
w-rookie
w-rookie-gui
```

The automation-oriented CLI is a separate developer command:

```bat
w-rookie-cli --help
```

### Quality checks

```bat
.venv\Scripts\python -m unittest discover -s tests -v
.venv\Scripts\ruff check run_gui.pyw src tests scripts
.venv\Scripts\ruff format --check run_gui.pyw src tests scripts
```

### Build the Windows executable

```bat
build.bat
```

Output:

```text
dist\W-Rookie\W-Rookie.exe
```

Hancom Office is not bundled with the executable. It must be installed separately on any PC that processes HWP/HWPX files.

### Build the macOS/Linux executable

```bash
./build.sh
```

The build for the current operating system is placed in `dist`. Cross-compilation is not used; GitHub Actions builds each executable natively on its corresponding operating-system runner.

### GitHub automated tests

`.github/workflows/tests.yml` runs the following on Windows, macOS, and Ubuntu with Python 3.10 and 3.12:

- Unit tests
- Ruff static analysis
- Ruff format check

Pushing a `v*` tag triggers `.github/workflows/release.yml`, which builds a Windows ZIP, macOS app ZIP, and Linux tar.gz natively and attaches them to a GitHub Release.

See the [test report](docs/TEST_REPORT.md) for recent validation results and the Windows pre-release checklist.

---

<a id="en-14-limitations"></a>

## 14. Limitations

- Password-protected documents are not processed.
- Legacy `.doc` files are not supported. Save them as `.docx` in Word first.
- OLE objects, charts, and special shapes inside groups are not treated as pictures.
- In Smart Center mode, a paragraph containing both a picture and text may be centered as a whole.
- Page Center may overlap multiple pictures on the same page.
- Disabling aspect-ratio preservation and entering dimensions with a different ratio distorts the picture.
- HWP/HWPX automation requires Windows and an installed copy of Hancom Office Hangul.
- Company security policy may restrict Hangul automation.
- Static scanning and Windows Defender scanning provide defense in depth but cannot guarantee detection of every new malware family.

---

<a id="en-15-uninstallation-and-reset"></a>

## 15. Uninstallation and reset

### Uninstall the program

Delete the project folder and its `.venv` folder. Generated document outputs remain unless you delete them separately.

### Reset saved settings

Delete the folder for your operating system:

```text
Windows:
%APPDATA%\WRookie

macOS:
~/Library/Application Support/WRookie

Linux:
~/.config/WRookie
```

The next launch starts with the default settings.

---

## Privacy and safety

- Documents and pictures are not uploaded to an external server.
- Save as New File is the default.
- A temporary file is replaced by the final output only after processing completes.
- Incomplete temporary files from failed or cancelled operations are removed.
- Remove personal and company information before sharing a test document.

## Project structure

```text
src/docpicalign/
├─ app.py                 # Desktop GUI
├─ cli.py                 # Developer command-line interface
├─ security.py            # Document pre-processing security scan
├─ service.py             # Format-specific processing router
└─ processors/
   ├─ docx.py             # Low-memory OOXML processing engine
   └─ hwp.py              # Hangul COM automation engine
tests/                    # Automated tests
scripts/create_sample.py  # Synthetic DOCX generator
scripts/stress_test.py    # Large-file stress test
```

## License

[MIT License](LICENSE)
