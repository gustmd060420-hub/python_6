package com.example.parkingapp;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    // 1. UI 요소 변수
    private ImageView btnProfile;
    private CardView btnNavCar, btnNavMap, btnNavPayment, btnNavCoupon;
    private Button btnExit;
    private LinearLayout layoutEmptyParking;
    private CardView layoutParkedInfo;
    private TextView tvParkedTime;
    private TextView tvElapsedTime;
    private TextView tvFee;

    // 2. 스마트 폴링을 위한 변수
    private Handler handler = new Handler(Looper.getMainLooper());
    private Runnable pollingRunnable;
    private final int POLLING_INTERVAL = 3000;
    private final int MAX_POLL_COUNT = 20;
    private int currentPollCount = 0;

    // 3. 실시간 시계(1초) 타이머를 위한 변수
    private Handler timerHandler = new Handler(Looper.getMainLooper());
    private Runnable timerRunnable;
    private String serverEntryTimeStr = "";
    private boolean isTimerRunning = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // UI 연결
        btnProfile = findViewById(R.id.btnProfile);
        btnNavCar = findViewById(R.id.btnNavCar);
        btnNavMap = findViewById(R.id.btnNavMap);
        btnNavPayment = findViewById(R.id.btnNavPayment);
        btnNavCoupon = findViewById(R.id.btnNavCoupon);
        btnExit = findViewById(R.id.btnExit);
        layoutEmptyParking = findViewById(R.id.layoutEmptyParking);
        layoutParkedInfo = findViewById(R.id.layoutParkedInfo);
        tvParkedTime = findViewById(R.id.tvParkedTime);
        tvElapsedTime = findViewById(R.id.tvElapsedTime);
        tvFee = findViewById(R.id.tvFee);

        // 하단 메뉴 클릭 이벤트
        btnNavCar.setOnClickListener(v -> {
            startSmartPolling();
            startActivity(new Intent(MainActivity.this, CarListActivity.class));
        });
        btnNavMap.setOnClickListener(v -> {
            startSmartPolling();
            startActivity(new Intent(MainActivity.this, MapActivity.class));
        });
        btnNavPayment.setOnClickListener(v -> {
            startSmartPolling();
            startActivity(new Intent(MainActivity.this, PaymentActivity.class));
        });
        btnNavCoupon.setOnClickListener(v -> {
            startSmartPolling();
            startActivity(new Intent(MainActivity.this, CouponActivity.class));
        });

        // 프로필 클릭 이벤트
        btnProfile.setOnClickListener(v -> {
            startSmartPolling();
            SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
            boolean isUserLoggedIn = prefs.getBoolean("isLoggedIn", false);

            if (isUserLoggedIn) {
                startActivity(new Intent(MainActivity.this, MyPageActivity.class));
            } else {
                startActivity(new Intent(MainActivity.this, LoginActivity.class));
            }
        });

        // 출차하기 버튼 클릭 이벤트
        btnExit.setOnClickListener(v -> {
            SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
            String userId = prefs.getString("userId", "");

            if (userId.isEmpty()) {
                Toast.makeText(MainActivity.this, "로그인 정보가 없습니다.", Toast.LENGTH_SHORT).show();
                return;
            }

            ApiService apiService = RetrofitClient.getApiService();
            apiService.exitParking(new UserIdRequest(userId)).enqueue(new Callback<AuthResponse>() {
                @Override
                public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        Toast.makeText(MainActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();

                        layoutParkedInfo.setVisibility(View.GONE);
                        layoutEmptyParking.setVisibility(View.VISIBLE);

                        stopRealTimeClock();
                        startSmartPolling();
                    } else {
                        Toast.makeText(MainActivity.this, "이미 출차되었거나 오류가 발생했습니다.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<AuthResponse> call, Throwable t) {
                    Toast.makeText(MainActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        startSmartPolling();
    }

    @Override
    protected void onPause() {
        super.onPause();
        stopPolling();
        stopRealTimeClock();
    }

    // 스마트 폴링 로직
    private void startSmartPolling() {
        stopPolling();
        currentPollCount = 0;

        pollingRunnable = new Runnable() {
            @Override
            public void run() {
                if (currentPollCount >= MAX_POLL_COUNT) {
                    stopPolling();
                    return;
                }

                checkParkingStatusFromServer();
                currentPollCount++;
                handler.postDelayed(this, POLLING_INTERVAL);
            }
        };
        handler.post(pollingRunnable);
    }

    private void stopPolling() {
        if (handler != null && pollingRunnable != null) {
            handler.removeCallbacks(pollingRunnable);
        }
    }

    // 실시간 시계 로직
    private void startRealTimeClock(String entryTimeStr) {
        if (isTimerRunning) return;
        stopRealTimeClock();
        this.serverEntryTimeStr = entryTimeStr;

        // 1. 서버 시간을 밀리초 단위로 변환 (타이머 바깥에서 딱 한 번만 실행)
        long tempEntryTime = 0;
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault());
            sdf.setTimeZone(java.util.TimeZone.getTimeZone("Asia/Seoul")); // 한국 시간 고정
            Date entryDate = sdf.parse(serverEntryTimeStr);
            tempEntryTime = entryDate.getTime();

            // 2. 핵심 보정: 서버 시간(입차 시간)이 스마트폰 시간보다 미래라면?
            // 기기 시계가 느린 것이므로, 입차 시간을 그냥 스마트폰의 '현재 시간'으로 당겨버립니다.
            if (tempEntryTime > System.currentTimeMillis()) {
                tempEntryTime = System.currentTimeMillis();
            }
        } catch (Exception e) {
            e.printStackTrace();
            tempEntryTime = System.currentTimeMillis(); // 에러 발생 시 현재 시간 기준
        }

        final long finalEntryTime = tempEntryTime; // 타이머 내부에서 쓰기 위해 final 선언

        timerRunnable = new Runnable() {
            @Override
            public void run() {
                // 3. 타이머 내부에서는 복잡한 계산 없이 (현재 시간 - 보정된 입차 시간)만 수행
                long diff = System.currentTimeMillis() - finalEntryTime;

                int hours = (int) (diff / (1000 * 60 * 60));
                int mins = (int) ((diff / (1000 * 60)) % 60);
                int secs = (int) ((diff / 1000) % 60);

                String elapsedStr = String.format(Locale.getDefault(), "%02d:%02d:%02d", hours, mins, secs);

                // 화면 업데이트
                tvParkedTime.setText("입차 시간: " + serverEntryTimeStr.substring(11, 19));
                tvElapsedTime.setText("경과 시간: " + elapsedStr);

                // 1초 뒤 반복
                timerHandler.postDelayed(this, 1000);
            }
        };
        isTimerRunning = true;
        timerHandler.post(timerRunnable);
    }

    private void stopRealTimeClock() {
        isTimerRunning = false;
        if (timerHandler != null && timerRunnable != null) {
            timerHandler.removeCallbacks(timerRunnable);
        }
    }

    // 서버 통신 로직
    private void checkParkingStatusFromServer() {
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        boolean isUserLoggedIn = prefs.getBoolean("isLoggedIn", false);
        String userId = prefs.getString("userId", "");

        if (!isUserLoggedIn || userId.isEmpty()) {
            layoutEmptyParking.setVisibility(View.VISIBLE);
            layoutParkedInfo.setVisibility(View.GONE);
            stopRealTimeClock();
            return;
        }

        ApiService apiService = RetrofitClient.getApiService();
        apiService.getParkingStatus(userId).enqueue(new Callback<ParkingStatusResponse>() {
            @Override
            public void onResponse(Call<ParkingStatusResponse> call, Response<ParkingStatusResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    boolean isParked = response.body().isParked();

                    if (isParked) {
                        layoutEmptyParking.setVisibility(View.GONE);
                        layoutParkedInfo.setVisibility(View.VISIBLE);
                        startRealTimeClock(response.body().getParkedTime());
                        String fee = response.body().getFee();
                        if (fee != null && !fee.isEmpty()) tvFee.setText(fee);
                    } else {
                        layoutEmptyParking.setVisibility(View.VISIBLE);
                        layoutParkedInfo.setVisibility(View.GONE);
                        stopRealTimeClock();
                    }
                }
            }

            @Override
            public void onFailure(Call<ParkingStatusResponse> call, Throwable t) {
                Log.e("PARKING_TEST", "통신 실패: " + t.getMessage());
            }
        });
    }
}