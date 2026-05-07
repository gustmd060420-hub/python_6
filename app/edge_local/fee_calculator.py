import pandas as pd
import datetime
import math
import os

# [설정값]
DAILY_MAX_FEE = 30000
BASE_FEE_PER_10MIN = 1000

class NaverAutoPass:
    def __init__(self, file_path='../../data/db/parking_logs_v3.csv'):
        self.file_path = file_path
        self.load_db()

    def load_db(self):
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=['차량 번호', '입차 일시', '출차 일시', '연동 계좌 잔액', '보유 할인권 (원)', '결제 상태'])
            df.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        self.db = pd.read_csv(self.file_path, encoding='utf-8-sig')

    def save_db(self):
        self.db.to_csv(self.file_path, index=False, encoding='utf-8-sig')

    def get_latest_balance(self, car_id):
        user_history = self.db[self.db['차량 번호'] == car_id]
        if not user_history.empty:
            return user_history.iloc[-1]['연동 계좌 잔액']
        return 50000 # 기본 테스트 잔액

    def process_entry(self, car_id, entry_time_str):
        """새로운 입차 기록 생성 (초 단위 기록)"""
        is_inside = self.db[(self.db['차량 번호'] == car_id) & (self.db['출차 일시'].isna())]
        if not is_inside.empty:
            return False, f"⚠️ {car_id}: 이미 주차장 안에 있는 차량입니다."

        current_balance = self.get_latest_balance(car_id)
        
        new_log = {
            '차량 번호': car_id,
            '입차 일시': entry_time_str,
            '출차 일시': float('nan'),
            '연동 계좌 잔액': current_balance,
            '보유 할인권 (원)': 0,
            '결제 상태': '대기'
        }
        self.db = pd.concat([self.db, pd.DataFrame([new_log])], ignore_index=True)
        self.save_db()
        return True, f"🚗 [입차 완료] {car_id} / 잔액: {current_balance:,}원"

    def process_settlement(self, car_id, exit_time_str):
        """출차 정산 (초 단위 계산 적용)"""
        target_idx = self.db[(self.db['차량 번호'] == car_id) & (self.db['출차 일시'].isna())].index
        if target_idx.empty:
            return False, f"❌ {car_id}: 입차 기록이 없습니다."
        
        # 💡 [시스템 개선] 입차 기록이 없는 꼬인 상황에 대한 실제 주차장식 예외 처리!
        if target_idx.empty:
            # 주차장 안에는 없다고 나오는데 카메라엔 찍힌 경우 (오인식 or 무단침입)
            error_msg = f"🚨 [긴급] {car_id} 차량의 입차 기록이 없습니다. 무단 진입이거나 입차 카메라 오류입니다.\n📞 정산기 인터폰을 통해 관리자를 호출합니다."
            return False, error_msg

        idx = target_idx[0]
        row = self.db.loc[idx]
        
        # 💡 초 단위까지 파싱 (%S 추가)
        fmt = "%Y-%m-%d %H:%M:%S"
        entry_time = datetime.datetime.strptime(row['입차 일시'], fmt)
        exit_time = datetime.datetime.strptime(exit_time_str, fmt)
        
        duration_minutes = (exit_time - entry_time).total_seconds() / 60.0

        # 테스트용 강제 요금 부과 (1분도 안 지나도 기본 10분 요금 부과하도록 math.ceil 적용)
        total_fee = (int(duration_minutes // (24*60)) * DAILY_MAX_FEE) + \
                    min(DAILY_MAX_FEE, math.ceil(max(1, duration_minutes) / 10) * BASE_FEE_PER_10MIN)
        
        final_fee = max(0, total_fee - row['보유 할인권 (원)'])

        # 결제 처리
        current_balance = row['연동 계좌 잔액']
        if current_balance >= final_fee:
            self.db.at[idx, '연동 계좌 잔액'] -= final_fee
            self.db.at[idx, '결제 상태'] = '완료'
            status_msg = "결제 완료"
        else:
            self.db.at[idx, '결제 상태'] = '미납(후불전환)'
            status_msg = "잔액 부족 (후불)"
        
        self.db.at[idx, '출차 일시'] = exit_time_str
        self.save_db()
        
        remain_balance = self.db.at[idx, '연동 계좌 잔액']
        return True, f"💳 [출차 정산] {car_id} | 주차시간: {int(duration_minutes)}분 | 요금: {final_fee:,}원 | 상태: {status_msg} | 잔액: {remain_balance:,}원", final_fee