package com.example.parkingapp;

import android.content.SharedPreferences;
import android.graphics.Color;
import android.os.Bundle;
import android.text.InputType;
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
import com.journeyapps.barcodescanner.ScanContract;
import com.journeyapps.barcodescanner.ScanIntentResult;
import com.journeyapps.barcodescanner.ScanOptions;
import androidx.activity.result.ActivityResultLauncher;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class CouponActivity extends AppCompatActivity {

    private List<CouponItem> couponList;
    private CouponAdapter couponAdapter;
    private TextView tvAvailableCount;
    private String userId;

    private final ActivityResultLauncher<ScanOptions> qrScanLauncher =
            registerForActivityResult(new ScanContract(), result -> {
                if (result.getContents() != null) {
                    redeemCouponByCode(result.getContents());
                }
            });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_coupon);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        userId = prefs.getString("userId", "");

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        Button btnQrScan = findViewById(R.id.btnQrScan);
        btnQrScan.setOnClickListener(v -> startQrScan());

        Button btnAddCoupon = findViewById(R.id.btnAddCoupon);
        btnAddCoupon.setOnClickListener(v -> showAddCouponDialog());

        tvAvailableCount = findViewById(R.id.tvAvailableCount);

        RecyclerView recyclerView = findViewById(R.id.recyclerViewCoupons);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        couponList = new ArrayList<>();
        couponAdapter = new CouponAdapter(couponList);
        recyclerView.setAdapter(couponAdapter);

        loadCouponsFromServer();
    }

    private void startQrScan() {
        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }
        ScanOptions options = new ScanOptions();
        options.setDesiredBarcodeFormats(ScanOptions.QR_CODE);
        options.setPrompt("쿠폰 QR 코드를 스캔하세요");
        options.setBeepEnabled(true);
        options.setOrientationLocked(true);
        qrScanLauncher.launch(options);
    }

    private void redeemCouponByCode(String code) {
        CouponRedeemRequest request = new CouponRedeemRequest(userId, code);
        RetrofitClient.getApiService().redeemCoupon(request).enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Toast.makeText(CouponActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();
                    loadCouponsFromServer();
                } else {
                    Toast.makeText(CouponActivity.this, "유효하지 않은 쿠폰 코드입니다.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                Toast.makeText(CouponActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showAddCouponDialog() {
        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (20 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, 0);

        EditText etCode = new EditText(this);
        etCode.setHint("쿠폰 코드 입력 (예: PYPASS30)");
        etCode.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
        etCode.setTextColor(Color.parseColor("#1A1A1A"));
        etCode.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etCode);

        new AlertDialog.Builder(this)
                .setTitle("쿠폰 코드 입력")
                .setView(layout)
                .setPositiveButton("등록", (dialog, which) -> {
                    String code = etCode.getText().toString().trim();
                    if (code.isEmpty()) {
                        Toast.makeText(this, "쿠폰 코드를 입력해주세요.", Toast.LENGTH_SHORT).show();
                        return;
                    }
                    redeemCouponByCode(code);
                })
                .setNegativeButton("취소", null)
                .show();
    }

    private void loadCouponsFromServer() {
        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        RetrofitClient.getApiService().getCoupons(userId).enqueue(new Callback<CouponListResponse>() {
            @Override
            public void onResponse(Call<CouponListResponse> call, Response<CouponListResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<CouponItem> coupons = response.body().getCoupons();
                    couponList.clear();
                    if (coupons != null) couponList.addAll(coupons);
                    couponAdapter.notifyDataSetChanged();

                    long availableCount = couponList.stream()
                            .filter(CouponItem::isAvailable)
                            .count();
                    tvAvailableCount.setText(availableCount + "개");
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
