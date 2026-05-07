import csv
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def show_beautiful_logs(csv_path):
    console = Console()
    
    # 1. 엑셀(CSV) 데이터 읽기
    logs = []
    total_revenue = 0
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 첫 줄(헤더) 건너뛰기
        for row in reader:
            if len(row) >= 6:
                logs.append(row)
                # 요금 합산 (CSV 구조에 따라 인덱스 조정 필요)
                try:
                    total_revenue += int(row[4].replace(',', '')) 
                except:
                    pass

    # 2. 상단 요약 정보 패널 만들기
    summary_text = f"[bold white]총 방문 차량:[/bold white] [cyan]{len(logs)} 대[/cyan]      "
    summary_text += f"[bold white]오늘 총 매출액:[/bold white] [green]{total_revenue:,} 원[/green]"
    
    panel = Panel(summary_text, title="[bold yellow]📊 주차장 요약 정보[/bold yellow]", expand=False, border_style="yellow")
    console.print(panel)
    console.print()

    # 3. 데이터 표(Table) 만들기
    table = Table(title="[bold magenta]🏢 주차장 실시간 정산 로그[/bold magenta]", show_header=True, header_style="bold white")
    
    table.add_column("차량 번호", style="dim", width=12)
    table.add_column("입차 일시", justify="center")
    table.add_column("출차 일시", justify="center")
    table.add_column("잔액/요금", justify="right", style="green")
    table.add_column("결제 상태", justify="center")

    # 최근 10개 로그만 표에 추가
    for row in logs[-10:]:
        plate, entry_time, exit_time, balance, fee, status = row[0], row[1], row[2], row[3], row[4], row[5]
        
        # 상태에 따라 색상 입히기
        if status == "완료":
            status_styled = "[bold blue]완료[/bold blue]"
        elif status == "미납":
            status_styled = "[bold red]미납[/bold red]"
        else:
            status_styled = f"[bold yellow]{status}[/bold yellow]"

        table.add_row(plate, entry_time, exit_time, f"{balance}원", status_styled)

    # 터미널에 아름다운 표 출력!
    console.print(table)

if __name__ == "__main__":
    # 1. 현재 파일(view_logs.py)이 있는 scripts 폴더의 절대 경로 파악
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. scripts 폴더의 부모 폴더(smart-parking-system) 최상단 경로 계산
    project_root = os.path.dirname(current_dir)
    
    # 3. 최상단에서부터 안전하게 경로 조립 (.. 기호 원천 차단)
    csv_path = os.path.join(project_root, "data", "db", "parking_logs_v3.csv")
    
    # 4. 파일 존재 여부 최종 확인 후 실행
    if not os.path.exists(csv_path):
        print(f"❌ 파일을 찾을 수 없습니다. 경로를 확인하세요:\n -> {csv_path}")
    else:
        show_beautiful_logs(csv_path)