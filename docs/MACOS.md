# W-Rookie for macOS

macOS판은 DOCX를 지원합니다. HWP/HWPX 자동화는 Windows 전용입니다.

1. Python 3.10 이상을 설치합니다.
2. ZIP을 완전히 압축 해제합니다.
3. `setup.command`를 Control-클릭한 뒤 **열기**를 선택합니다.
4. 설치가 끝나면 `run.command`를 같은 방법으로 실행합니다.
5. GUI에서 DOCX를 추가하고 스마트 중앙 정렬을 선택합니다.
6. 필요하면 **크기 조절 사용**을 켜고 가로·세로 수치와 `mm/cm` 단위를 입력합니다.
7. 비율 유지 여부, 1.0pt 테두리, 새 파일 저장을 확인한 뒤 처리합니다.

터미널에서는 `./setup.sh`, `./run.sh`를 사용할 수 있습니다. Python 3.10
이상이 필요하며 python.org의 최신 macOS Python을 권장합니다. 다음 실행부터는
`run.command`만 사용합니다. 보안 확인이 나타나면 시스템 설정의 개인정보 보호
및 보안에서 차단 내용을 확인하세요. 공식 릴리스의 SHA-256을 확인한 뒤
Control-클릭 → **열기** 또는 **확인 없이 열기**를 사용하고 Gatekeeper 전체는 끄지 마세요.
