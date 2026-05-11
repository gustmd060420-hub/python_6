package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.ImageButton;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CouponActivity extends AppCompatActivity {

    private List<CouponItem> couponList;
    private CouponAdapter couponAdapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_coupon);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        RecyclerView recyclerView = findViewById(R.id.recyclerViewCoupons);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        couponList = new ArrayList<>();
        couponAdapter = new CouponAdapter(couponList);
        recyclerView.setAdapter(couponAdapter);

        loadCouponsFromServer();
    }

    private void loadCouponsFromServer() {
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "");

        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        ApiService apiService = RetrofitClient.getApiService();
        apiService.getCoupons(userId).enqueue(new Callback<CouponListResponse>() {
            @Override
            public void onResponse(Call<CouponListResponse> call, Response<CouponListResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<CouponItem> coupons = response.body().getCoupons();
                    couponList.clear();
                    if (coupons != null) couponList.addAll(coupons);
                    couponAdapter.notifyDataSetChanged();
                } else {
                    Toast.makeText(CouponActivity.this, "쿠폰 정보를 불러오지 못했습니다.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<CouponListResponse> call, Throwable t) {
                Toast.makeText(CouponActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
