package com.example.parkingapp;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CreditCardAdapter extends RecyclerView.Adapter<CreditCardAdapter.CardViewHolder> {

    private List<CreditCardItem> cardList;

    public CreditCardAdapter(List<CreditCardItem> cardList) {
        this.cardList = cardList;
    }

    @NonNull
    @Override
    public CardViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_credit_card, parent, false);
        return new CardViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CardViewHolder holder, int position) {
        CreditCardItem item = cardList.get(position);

        holder.tvCardNumber.setText(item.getCardNumber());
        holder.tvCardCompany.setText(item.getCardCompany());

        // 데이터에 지정된 헥사코드(Hex) 색상으로 카드 배경색 변경
        holder.cardContainer.setCardBackgroundColor(Color.parseColor(item.getBgColorHex()));

        if (item.isPrimary()) {
            holder.tvPrimaryStatus.setText("✓ 주 카드");
            holder.tvPrimaryStatus.setBackgroundColor(Color.parseColor("#40FFFFFF")); // 반투명 흰색
        } else {
            holder.tvPrimaryStatus.setText("주 카드로 설정");
            holder.tvPrimaryStatus.setBackgroundColor(Color.parseColor("#20000000")); // 반투명 검정
        }
    }

    @Override
    public int getItemCount() {
        return cardList.size();
    }

    static class CardViewHolder extends RecyclerView.ViewHolder {
        CardView cardContainer;
        TextView tvCardNumber, tvCardCompany, tvPrimaryStatus;

        public CardViewHolder(@NonNull View itemView) {
            super(itemView);
            cardContainer = itemView.findViewById(R.id.cardContainer);
            tvCardNumber = itemView.findViewById(R.id.tvCardNumber);
            tvCardCompany = itemView.findViewById(R.id.tvCardCompany);
            tvPrimaryStatus = itemView.findViewById(R.id.tvPrimaryStatus);
        }
    }
}