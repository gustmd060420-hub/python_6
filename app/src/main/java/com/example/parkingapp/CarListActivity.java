package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.graphics.Color;
import android.text.InputType;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CarListActivity extends AppCompatActivity {

    private CarAdapter carAdapter;
    private List<CarItem> carList;
    private TextView tvTotalCarCount;
    private String userId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_car_list);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        userId = prefs.getString("userId", "");

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        Button btnAddCar = findViewById(R.id.btnAddCar);
        btnAddCar.setOnClickListener(v -> showAddCarDialog());

        tvTotalCarCount = findViewById(R.id.tvTotalCarCount);
        RecyclerView recyclerView = findViewById(R.id.recyclerViewCars);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        carList = new ArrayList<>();
        carAdapter = new CarAdapter(carList, item -> showDeleteConfirmDialog(item));
        recyclerView.setAdapter(carAdapter);

        loadCarsFromServer();
    }

    private void loadCarsFromServer() {
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

    private void showAddCarDialog() {
        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (20 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, 0);

        EditText etPlate = new EditText(this);
        etPlate.setHint("차량 번호 (예: 12가 3456)");
        etPlate.setInputType(InputType.TYPE_CLASS_TEXT);
        etPlate.setTextColor(Color.parseColor("#1A1A1A"));
        etPlate.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etPlate);

        EditText etModel = new EditText(this);
        etModel.setHint("차종 (예: 현대 아반떼)");
        etModel.setInputType(InputType.TYPE_CLASS_TEXT);
        etModel.setTextColor(Color.parseColor("#1A1A1A"));
        etModel.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etModel);

        EditText etColor = new EditText(this);
        etColor.setHint("색상 (예: 화이트)");
        etColor.setInputType(InputType.TYPE_CLASS_TEXT);
        etColor.setTextColor(Color.parseColor("#1A1A1A"));
        etColor.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etColor);

        EditText etYear = new EditText(this);
        etYear.setHint("연식 (예: 2023년)");
        etYear.setInputType(InputType.TYPE_CLASS_TEXT);
        etYear.setTextColor(Color.parseColor("#1A1A1A"));
        etYear.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etYear);

        new AlertDialog.Builder(this)
                .setTitle("차량 추가")
                .setView(layout)
                .setPositiveButton("추가", (dialog, which) -> {
                    String plate = etPlate.getText().toString().trim();
                    String model = etModel.getText().toString().trim();
                    String color = etColor.getText().toString().trim();
                    String year = etYear.getText().toString().trim();

                    if (plate.isEmpty() || model.isEmpty() || color.isEmpty() || year.isEmpty()) {
                        Toast.makeText(this, "모든 항목을 입력해주세요.", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    addCarToServer(plate, model, color, year);
                })
                .setNegativeButton("취소", null)
                .show();
    }

    private void addCarToServer(String plate, String model, String color, String year) {
        ApiService apiService = RetrofitClient.getApiService();
        CarAddRequest request = new CarAddRequest(userId, plate, model, color, year);

        apiService.addCar(request).enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Toast.makeText(CarListActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();
                    loadCarsFromServer();
                } else if (response.code() == 400) {
                    Toast.makeText(CarListActivity.this, "이미 등록된 번호판입니다.", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(CarListActivity.this, "차량 추가 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                Toast.makeText(CarListActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showDeleteConfirmDialog(CarItem item) {
        new AlertDialog.Builder(this)
                .setTitle("차량 삭제")
                .setMessage(item.getCarNumber() + " 차량을 삭제하시겠습니까?")
                .setPositiveButton("삭제", (dialog, which) -> deleteCarFromServer(item.getCarNumber()))
                .setNegativeButton("취소", null)
                .show();
    }

    private void deleteCarFromServer(String plate) {
        ApiService apiService = RetrofitClient.getApiService();
        PlateDeleteRequest request = new PlateDeleteRequest(userId, plate);

        apiService.deleteCar(request).enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Toast.makeText(CarListActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();
                    loadCarsFromServer();
                } else {
                    Toast.makeText(CarListActivity.this, "삭제 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                Toast.makeText(CarListActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
