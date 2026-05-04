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

public class CarListActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private CarAdapter carAdapter;
    private List<CarItem> carList;
    private TextView tvTotalCarCount;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_car_list);

        // 뒤로가기 버튼 처리
        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish()); // 현재 화면 종료

        tvTotalCarCount = findViewById(R.id.tvTotalCarCount);
        recyclerView = findViewById(R.id.recyclerViewCars);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        // 가짜 데이터 생성 (피그마 디자인에 있는 데이터)
        carList = new ArrayList<>();
        carList.add(new CarItem("12가 3456", "현대 아반떼", "화이트", "2023년", true));
        carList.add(new CarItem("78나 9012", "기아 K5", "블랙", "2022년", false));
        carList.add(new CarItem("34다 5678", "제네시스 G80", "그레이", "2024년", false));

        // 총 개수 표시
        tvTotalCarCount.setText("총 " + carList.size() + "대");

        // 어댑터 연결
        carAdapter = new CarAdapter(carList);
        recyclerView.setAdapter(carAdapter);
    }
}