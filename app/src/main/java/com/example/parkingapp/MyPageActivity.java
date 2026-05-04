package com.example.parkingapp; // 본인 패키지명 확인

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

public class MyPageActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_my_page);

        TextView tvUserInfo = findViewById(R.id.tvUserInfo);
        Button btnLogout = findViewById(R.id.btnLogout);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "알 수 없음");
        tvUserInfo.setText(userId + "님, 환영합니다.");

        btnLogout.setOnClickListener(v -> {
            SharedPreferences.Editor editor = prefs.edit();
            editor.putBoolean("isLoggedIn", false);
            editor.remove("userId");
            editor.apply();

            Toast.makeText(this, "로그아웃 되었습니다.", Toast.LENGTH_SHORT).show();
            finish(); // 메인 화면으로 복귀
        });
    }
}