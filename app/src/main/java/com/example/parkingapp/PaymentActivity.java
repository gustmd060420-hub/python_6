package com.example.parkingapp;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.graphics.Color;
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
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class PaymentActivity extends AppCompatActivity {

    private List<CreditCardItem> cardList;
    private CreditCardAdapter cardAdapter;
    private TextView tvTotalCardCount;
    private String userId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_payment);

        SharedPreferences prefs = getSharedPreferences("AppPrefs", MODE_PRIVATE);
        userId = prefs.getString("userId", "");

        ImageButton btnBack = findViewById(R.id.btnBack);
        btnBack.setOnClickListener(v -> finish());

        Button btnAddCard = findViewById(R.id.btnAddCard);
        btnAddCard.setOnClickListener(v -> showAddCardDialog());

        tvTotalCardCount = findViewById(R.id.tvTotalCardCount);
        RecyclerView recyclerView = findViewById(R.id.recyclerViewCards);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        cardList = new ArrayList<>();
        cardAdapter = new CreditCardAdapter(cardList, item -> showDeleteConfirmDialog(item));
        recyclerView.setAdapter(cardAdapter);

        loadCardsFromServer();
    }

    private void loadCardsFromServer() {
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

    private void showAddCardDialog() {
        if (userId.isEmpty()) {
            Toast.makeText(this, "로그인이 필요합니다.", Toast.LENGTH_SHORT).show();
            return;
        }

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (20 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, 0);

        EditText etCardNumber = new EditText(this);
        etCardNumber.setHint("카드 번호 (예: **** **** **** 1234)");
        etCardNumber.setInputType(InputType.TYPE_CLASS_TEXT);
        etCardNumber.setTextColor(Color.parseColor("#1A1A1A"));
        etCardNumber.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etCardNumber);

        EditText etBank = new EditText(this);
        etBank.setHint("카드사 (예: 신한카드)");
        etBank.setInputType(InputType.TYPE_CLASS_TEXT);
        etBank.setTextColor(Color.parseColor("#1A1A1A"));
        etBank.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etBank);

        EditText etColor = new EditText(this);
        etColor.setHint("카드 색상 HEX (예: #4C6BFF)");
        etColor.setInputType(InputType.TYPE_CLASS_TEXT);
        etColor.setTextColor(Color.parseColor("#1A1A1A"));
        etColor.setHintTextColor(Color.parseColor("#888888"));
        layout.addView(etColor);

        new AlertDialog.Builder(this)
                .setTitle("카드 추가")
                .setView(layout)
                .setPositiveButton("추가", (dialog, which) -> {
                    String cardNumber = etCardNumber.getText().toString().trim();
                    String bank = etBank.getText().toString().trim();
                    String color = etColor.getText().toString().trim();

                    if (cardNumber.isEmpty() || bank.isEmpty() || color.isEmpty()) {
                        Toast.makeText(this, "모든 항목을 입력해주세요.", Toast.LENGTH_SHORT).show();
                        return;
                    }

                    addCardToServer(cardNumber, bank, color);
                })
                .setNegativeButton("취소", null)
                .show();
    }

    private void addCardToServer(String cardNumber, String bank, String color) {
        CardAddRequest request = new CardAddRequest(userId, cardNumber, bank, color);
        RetrofitClient.getApiService().addCard(request).enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Toast.makeText(PaymentActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();
                    loadCardsFromServer();
                } else if (response.code() == 400) {
                    Toast.makeText(PaymentActivity.this, "이미 등록된 카드입니다.", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(PaymentActivity.this, "카드 추가 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                Toast.makeText(PaymentActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showDeleteConfirmDialog(CreditCardItem item) {
        new AlertDialog.Builder(this)
                .setTitle("카드 삭제")
                .setMessage(item.getCardCompany() + " (" + item.getCardNumber() + ") 을 삭제하시겠습니까?")
                .setPositiveButton("삭제", (dialog, which) -> deleteCardFromServer(item.getCardNumber()))
                .setNegativeButton("취소", null)
                .show();
    }

    private void deleteCardFromServer(String cardNumber) {
        CardDeleteRequest request = new CardDeleteRequest(userId, cardNumber);
        RetrofitClient.getApiService().deleteCard(request).enqueue(new Callback<AuthResponse>() {
            @Override
            public void onResponse(Call<AuthResponse> call, Response<AuthResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Toast.makeText(PaymentActivity.this, response.body().getMessage(), Toast.LENGTH_SHORT).show();
                    loadCardsFromServer();
                } else {
                    Toast.makeText(PaymentActivity.this, "카드 삭제 실패", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<AuthResponse> call, Throwable t) {
                Toast.makeText(PaymentActivity.this, "서버 연결 실패: " + t.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });
    }
}
