package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CarListActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private CarAdapter carAdapter;
    private List<CarItem> carList;
    private TextView tvTotalCarCount;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_car_list);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        tvTotalCarCount = findViewById(R.id.tvTotalCarCount);
        recyclerView = findViewById(R.id.recyclerViewCars);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        carList = new ArrayList<>();
        carAdapter = new CarAdapter(carList);
        recyclerView.setAdapter(carAdapter);

        loadCarsFromServer();
    }

    private void loadCarsFromServer() {
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "");

        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        ApiService apiService = RetrofitClient.getApiService();
        apiService.getCars(userId).enqueue(new Callback<CarListResponse>() {
            @Override
            public void onResponse(Call<CarListResponse> call, Response<CarListResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<CarItem> cars = response.body().getCars();
                    carList.clear();
                    if (cars != null) carList.addAll(cars);
                    carAdapter.notifyDataSetChanged();
                    tvTotalCarCount.setText("총 " + carList.size() + "대");
                } else {
                    Toast.makeText(CarListActivity.this, "차량 정보를 불러오지 못했습니다.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<CarListResponse> call, Throwable t) {
                Toast.makeText(CarListActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
