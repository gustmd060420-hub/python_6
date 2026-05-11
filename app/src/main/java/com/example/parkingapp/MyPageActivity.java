package com.example.parkingapp;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MyPageActivity extends AppCompatActivity {

    private TextView tvUserInfo;
    private TextView tvUserId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_page);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        tvUserInfo = findViewById(R.id.tvUserInfo);
        tvUserId = findViewById(R.id.tvUserId);
        LinearLayout btnLogout = findViewById(R.id.btnLogout);
        LinearLayout btnDeleteAccount = findViewById(R.id.btnDeleteAccount);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "");

        tvUserId.setText("@" + userId);
        tvUserInfo.setText(userId + "님, 환영합니다.");

        if (!userId.isEmpty()) {
            ApiService apiService = RetrofitClient.getApiService();
            apiService.getUserInfo(userId).enqueue(new Callback<UserInfoResponse>() {
                @Override
                public void onResponse(Call<UserInfoResponse> call, Response<UserInfoResponse> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        tvUserInfo.setText(response.body().getName() + "님, 환영합니다.");
                    }
                }

                @Override
                public void onFailure(Call<UserInfoResponse> call, Throwable t) {}
            });
        }

        btnLogout.setOnClickListener(v -> {
            prefs.edit()
                    .putBoolean("isLoggedIn", false)
                    .remove("userId")
                    .apply();
            Toast.makeText(this, "로그아웃 되었습니다.", Toast.LENGTH_SHORT).show();
            finish();
        });

        btnDeleteAccount.setOnClickListener(v -> {
            new AlertDialog.Builder(this)
                    .setTitle("회원 탈퇴")
                    .setMessage("탈퇴 시 모든 데이터(차량, 카드, 쿠폰)가 삭제됩니다.\n정말 탈퇴하시겠습니까?")
                    .setPositiveButton("탈퇴", (dialog, which) -> {
                        ApiService apiService = RetrofitClient.getApiService();
                        apiService.deleteUser(new UserIdRequest(userId)).enqueue(new Callback<AuthResponse>() {
                            @Override
                            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                                if (response.isSuccessful()) {
                                    prefs.edit()
                                            .putBoolean("isLoggedIn", false)
                                            .remove("userId")
                                            .apply();
                                    Toast.makeText(MyPageActivity.this, "탈퇴가 완료되었습니다.", Toast.LENGTH_SHORT).show();
                                    Intent intent = new Intent(MyPageActivity.this, MainActivity.class);
                                    intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
                                    startActivity(intent);
                                    finish();
                                } else {
                                    Toast.makeText(MyPageActivity.this, "탈퇴 처리 중 오류가 발생했습니다.", Toast.LENGTH_SHORT).show();
                                }
                            }

                            @Override
                            public void onFailure(Call<AuthResponse> call, Throwable t) {
                                Toast.makeText(MyPageActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                            }
                        });
                    })
                    .setNegativeButton("취소", null)
                    .show();
        });
    }
}
