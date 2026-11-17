# W-Rookie for Linux

Linux판은 DOCX를 지원합니다. HWP/HWPX 자동화는 Windows 전용입니다. Python
3.10 이상, venv, Tkinter와 데스크톱 그래픽 세션이 필요합니다.

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

Debian/Ubuntu 계열 준비 예시:

```bash
sudo apt install python3 python3-venv python3-tk
```

GUI에서 DOCX를 추가하고 스마트 중앙 정렬을 선택합니다. 필요하면 **크기 조절 사용**을 켜고 가로·세로 수치와 `mm/cm` 단위를 입력한 뒤, 비율 유지 여부, 1.0pt 테두리, 새 파일 저장을 확인해 처리합니다.
다음 실행부터는 `./run.sh`만 사용합니다. 배포판에 따라 패키지 이름이 다를 수
있습니다.
