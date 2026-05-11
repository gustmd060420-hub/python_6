package com.example.parkingapp;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.cardview.widget.CardView;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CreditCardAdapter extends RecyclerView.Adapter<CreditCardAdapter.CardViewHolder> {

    public interface OnDeleteClickListener {
        void onDelete(CreditCardItem item);
    }

    private List<CreditCardItem> cardList;
    private OnDeleteClickListener deleteListener;

    public CreditCardAdapter(List<CreditCardItem> cardList, OnDeleteClickListener deleteListener) {
        this.cardList = cardList;
        this.deleteListener = deleteListener;
    }

    // 기존 코드 호환용
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

        try {
            holder.cardContainer.setCardBackgroundColor(Color.parseColor(item.getBgColorHex()));
        } catch (Exception e) {
            holder.cardContainer.setCardBackgroundColor(Color.parseColor("#4C6BFF")); // 파싱 실패 시 기본색
        }

        if (item.isPrimary()) {
            holder.tvPrimaryStatus.setText("✓ 주 카드");
            holder.tvPrimaryStatus.setBackgroundColor(Color.parseColor("#40FFFFFF"));
        } else {
            holder.tvPrimaryStatus.setText("주 카드로 설정");
            holder.tvPrimaryStatus.setBackgroundColor(Color.parseColor("#20000000"));
        }

        holder.btnDeleteCard.setOnClickListener(v -> {
            if (deleteListener != null) {
                deleteListener.onDelete(item);
            }
        });
    }

    @Override
    public int getItemCount() {
        return cardList.size();
    }

    public void updateList(List<CreditCardItem> newList) {
        cardList.clear();
        cardList.addAll(newList);
        notifyDataSetChanged();
    }

    static class CardViewHolder extends RecyclerView.ViewHolder {
        CardView cardContainer;
        TextView tvCardNumber, tvCardCompany, tvPrimaryStatus;
        ImageButton btnDeleteCard;

        public CardViewHolder(@NonNull View itemView) {
            super(itemView);
            cardContainer = itemView.findViewById(R.id.cardContainer);
            tvCardNumber = itemView.findViewById(R.id.tvCardNumber);
            tvCardCompany = itemView.findViewById(R.id.tvCardCompany);
            tvPrimaryStatus = itemView.findViewById(R.id.tvPrimaryStatus);
            btnDeleteCard = itemView.findViewById(R.id.btnDeleteCard);
        }
    }
}
