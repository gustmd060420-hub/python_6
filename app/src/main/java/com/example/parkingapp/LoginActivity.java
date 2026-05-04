package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        EditText etName = findViewById(R.id.etName);
        EditText etUserId = findViewById(R.id.etUserId);
        EditText etPassword = findViewById(R.id.etPassword);
        Button btnLoginSubmit = findViewById(R.id.btnLoginSubmit);
        Button btnSignupSubmit = findViewById(R.id.btnSignupSubmit);

        ApiService apiService = RetrofitClient.getApiService();

        // 1. 회원가입 버튼 클릭 이벤트
        btnSignupSubmit.setOnClickListener(v -> {
            String name = etName.getText().toString();
            String userId = etUserId.getText().toString();
            String password = etPassword.getText().toString();

            if (userId.isEmpty() || password.isEmpty() || name.isEmpty()) {
                Toast.makeText(this, "모든 정보를 입력해주세요.", Toast.LENGTH_SHORT).show();
                return;
            }

            UserRequest request = new UserRequest(userId, password, name);
            apiService.signup(request).enqueue(new Callback<AuthResponse>() {
                @Override
                public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                    if (response.isSuccessful()) {
                        Toast.makeText(LoginActivity.this, "회원가입 성공! 로그인해주세요.", Toast.LENGTH_SHORT).show();
                    } else if (response.code() == 400) {
                        // 서버에서 명시적으로 400(중복) 에러를 보냈을 때
                        Toast.makeText(LoginActivity.this, "이미 존재하는 아이디입니다.", Toast.LENGTH_SHORT).show();
                    } else {
                        // 오타나 문법 오류 등 서버 자체 문제(500)일 때
                        Toast.makeText(LoginActivity.this, "서버 오류 발생 (" + response.code() + ")", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<AuthResponse> call, Throwable t) {
                    Toast.makeText(LoginActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });

        // 2. 로그인 버튼 클릭 이벤트
        btnLoginSubmit.setOnClickListener(v -> {
            String userId = etUserId.getText().toString();
            String password = etPassword.getText().toString();

            if (userId.isEmpty() || password.isEmpty()) {
                Toast.makeText(this, "아이디와 비밀번호를 입력해주세요.", Toast.LENGTH_SHORT).show();
                return;
            }

            UserRequest request = new UserRequest(userId, password, ""); // 로그인은 이름 필요 없음
            apiService.login(request).enqueue(new Callback<AuthResponse>() {
                @Override
                public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        String userName = response.body().getName();

                        // 로그인 성공 시 기기에 상태 저장
                        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
                        SharedPreferences.Editor editor = prefs.edit();
                        editor.putBoolean("isLoggedIn", true);
                        editor.putString("userId", userId);
                        editor.apply();

                        Toast.makeText(LoginActivity.this, userName + "님 환영합니다!", Toast.LENGTH_SHORT).show();
                        finish(); // 메인 화면으로 복귀
                    } else {
                        Toast.makeText(LoginActivity.this, "아이디 또는 비밀번호가 틀렸습니다.", Toast.LENGTH_SHORT).show();
                    }
                }

                @Override
                public void onFailure(Call<AuthResponse> call, Throwable t) {
                    Toast.makeText(LoginActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        });
    }
}