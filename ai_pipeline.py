import collections
import random
import time

class LicensePlateEnsembler:
    def __init__(self, confidence_threshold=0.6, final_score_threshold=0.80):
        self.frame_results = []
        self.conf_threshold = confidence_threshold
        self.final_threshold = final_score_threshold

    def add_frame_result(self, text, confidence):
        """프레임 결과를 리스트에 수집 (저품질 필터링 포함)"""
        if confidence >= self.conf_threshold: 
            self.frame_results.append((text, confidence))

    def get_final_result(self):
        """가중치 투표를 통해 최종 결과 도출"""
        if not self.frame_results:
            return None, "인식 실패 (유효 프레임 없음)"

        # 텍스트별로 확신도 점수 합산
        score_board = collections.defaultdict(float)
        for text, conf in self.frame_results:
            score_board[text] += conf
        
        # 가장 점수가 높은 1등 문자열 찾기
        best_text = max(score_board, key=score_board.get)
        
        # 최종 점수 정규화 (평균 확신도 계산)
        total_valid_frames = len(self.frame_results)
        average_confidence = score_board[best_text] / total_valid_frames

        if average_confidence >= self.final_threshold:
            return best_text, f"최종 승인 완료 (평균 확신도: {average_confidence:.2f})"
        else:
            return best_text, f"확신도 미달, 수동 전환 (평균 확신도: {average_confidence:.2f})"

# ==========================================
# 🚗 시뮬레이션 테스트 실행 코드
# ==========================================
if __name__ == "__main__":
    print("🎥 [AI 시뮬레이션] 3초간 90프레임 분석을 시작합니다...")
    
    ensembler = LicensePlateEnsembler()
    
    # 90번의 카메라 프레임 캡처를 흉내 냅니다.
    for i in range(1, 91):
        # 70% 확률로 정답, 30% 확률로 노이즈(오답)가 찍힌다고 가정
        if random.random() < 0.7:
            # 정답을 읽었을 때는 확신도가 높음 (0.7 ~ 0.99)
            text = "12가3456"
            conf = round(random.uniform(0.7, 0.99), 2)
        else:
            # 오답을 읽었을 때는 비가 오거나 흔들려서 확신도가 낮음 (0.4 ~ 0.7)
            text = random.choice(["12가3458", "12다3456", "72가3456"])
            conf = round(random.uniform(0.4, 0.7), 2)
        
        # 앙상블 모델에 데이터 집어넣기
        ensembler.add_frame_result(text, conf)
        
        # 터미널에 진행 상황 살짝 보여주기 (너무 길어지니 10번마다 출력)
        if i % 10 == 0:
            print(f"  👉 프레임 {i}/90 수집 중... (인식: {text}, 확신도: {conf})")
        
        time.sleep(0.02) # 실제 프레임 처리 시간을 흉내 냄
        
    print("\n📊 데이터 수집 완료. 가중치 투표를 진행합니다...")
    time.sleep(1)
    
    # 최종 결과 발표!
    final_plate, status_msg = ensembler.get_final_result()
    print("=" * 40)
    print(f"🎯 최종 인식 번호 : {final_plate}")
    print(f"💡 판단 결과     : {status_msg}")
    print("=" * 40)