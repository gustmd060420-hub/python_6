package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
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

public class PaymentActivity extends AppCompatActivity {

    private List<CreditCardItem> cardList;
    private CreditCardAdapter cardAdapter;
    private TextView tvTotalCardCount;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_payment);

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        tvTotalCardCount = findViewById(R.id.tvTotalCardCount);
        RecyclerView recyclerView = findViewById(R.id.recyclerViewCards);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        cardList = new ArrayList<>();
        cardAdapter = new CreditCardAdapter(cardList);
        recyclerView.setAdapter(cardAdapter);

        loadCardsFromServer();
    }

    private void loadCardsFromServer() {
        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        String userId = prefs.getString("userId", "");

        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        ApiService apiService = RetrofitClient.getApiService();
        apiService.getCards(userId).enqueue(new Callback<CardListResponse>() {
            @Override
            public void onResponse(Call<CardListResponse> call, Response<CardListResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<CreditCardItem> cards = response.body().getCards();
                    cardList.clear();
                    if (cards != null) cardList.addAll(cards);
                    cardAdapter.notifyDataSetChanged();
                    tvTotalCardCount.setText("총 " + cardList.size() + "개");
                } else {
                    Toast.makeText(PaymentActivity.this, "카드 정보를 불러오지 못했습니다.", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<CardListResponse> call, Throwable t) {
                Toast.makeText(PaymentActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
