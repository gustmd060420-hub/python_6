package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MyPageActivity extends AppCompatActivity {

    private TextView tvUserInfo;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_page);

        tvUserInfo = findViewById(R.id.tvUserInfo);
        Button btnLogout = findViewById(R.id.btnLogout);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "");

        // 기본 표시 (서버 응답 전)
        tvUserInfo.setText(userId + "님, 환영합니다.");

        // 서버에서 실제 이름 조회
        if (!userId.isEmpty()) {
            ApiService apiService = RetrofitClient.getApiService();
            apiService.getUserInfo(userId).enqueue(new Callback<UserInfoResponse>() {
                @Override
                public void onResponse(Call<UserInfoResponse> call, Response<UserInfoResponse> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        String name = response.body().getName();
                        tvUserInfo.setText(name + "님, 환영합니다.");
                    }
                }

                @Override
                public void onFailure(Call<UserInfoResponse> call, Throwable t) {
                    // 실패 시 userId 그대로 유지
                }
            });
        }

        btnLogout.setOnClickListener(v -> {
            SharedPreferences.Editor editor = prefs.edit();
            editor.putBoolean("isLoggedIn", false);
            editor.remove("userId");
            editor.apply();
            Toast.makeText(this, "로그아웃 되었습니다.", Toast.LENGTH_SHORT).show();
            finish();
        });
    }
}
