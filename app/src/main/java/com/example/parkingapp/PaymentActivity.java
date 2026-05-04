package com.example.parkingapp;

import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;

public class PaymentActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_payment);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        RecyclerView recyclerView = findViewById(R.id.recyclerViewCards);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // 피그마 시안에 맞춘 카드 데이터 3개
        List<CreditCardItem> list = new ArrayList<>();
        list.add(new CreditCardItem("**** **** **** 1234", "신한카드", "#4C6BFF", true)); // 파란색
        list.add(new CreditCardItem("**** **** **** 5678", "삼성카드", "#6A38F5", false)); // 보라색
        list.add(new CreditCardItem("**** **** **** 9012", "현대카드", "#A038F5", false)); // 연보라색

        TextView tvTotalCardCount = findViewById(R.id.tvTotalCardCount);
        tvTotalCardCount.setText("총 " + list.size() + "개");

        CreditCardAdapter adapter = new CreditCardAdapter(list);
        recyclerView.setAdapter(adapter);
    }
}