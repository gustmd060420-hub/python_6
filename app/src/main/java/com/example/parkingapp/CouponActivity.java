package com.example.parkingapp;

import android.os.Bundle;
import android.widget.ImageButton;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class CouponActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_coupon);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        RecyclerView recyclerView = findViewById(R.id.recyclerViewCoupons);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // 가짜 데이터 세팅 (사용가능 2개, 사용완료 1개)
        List<CouponItem> list = new ArrayList<>();
        list.add(new CouponItem("강남역 30분 무료", "% 30분 무료\n강남역 공영주차장", "🕒 2026.05.31까지", true));
        list.add(new CouponItem("역삼역 50% 할인", "% 첫 1시간 50% 할인\n역삼역 스마트파킹", "🕒 2026.04.30까지", true));
        list.add(new CouponItem("신논현역 2000원 할인", "2000원 할인\n신논현역 주차장", "만료됨", false));

        CouponAdapter adapter = new CouponAdapter(list);
        recyclerView.setAdapter(adapter);
    }
}