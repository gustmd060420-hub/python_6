package com.example.parkingapp;

import android.graphics.Color;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CouponAdapter extends RecyclerView.Adapter<CouponAdapter.CouponViewHolder> {

    private List<CouponItem> couponList;

    public CouponAdapter(List<CouponItem> couponList) {
        this.couponList = couponList;
    }

    @NonNull
    @Override
    public CouponViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_coupon, parent, false);
        return new CouponViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CouponViewHolder holder, int position) {
        CouponItem item = couponList.get(position);

        holder.tvCouponTitle.setText(item.getTitle());
        holder.tvCouponDesc.setText(item.getDescription());
        holder.tvExpiryDate.setText(item.getExpiryDate());

        // 사용 가능 여부에 따른 디자인 변경
        if (item.isAvailable()) {
            holder.layoutCouponBg.setBackgroundColor(Color.parseColor("#5DB075")); // 메인 그린
            holder.tvStatusBadge.setText("사용가능");
            holder.btnUseCoupon.setVisibility(View.VISIBLE);
        } else {
            holder.layoutCouponBg.setBackgroundColor(Color.parseColor("#BDBDBD")); // 회색
            holder.tvStatusBadge.setText("사용완료");
            holder.btnUseCoupon.setVisibility(View.INVISIBLE); // 버튼 숨김
        }
    }

    @Override
    public int getItemCount() {
        return couponList.size();
    }

    static class CouponViewHolder extends RecyclerView.ViewHolder {
        LinearLayout layoutCouponBg;
        TextView tvCouponTitle, tvCouponDesc, tvExpiryDate, tvStatusBadge;
        Button btnUseCoupon;

        public CouponViewHolder(@NonNull View itemView) {
            super(itemView);
            layoutCouponBg = itemView.findViewById(R.id.layoutCouponBg);
            tvCouponTitle = itemView.findViewById(R.id.tvCouponTitle);
            tvCouponDesc = itemView.findViewById(R.id.tvCouponDesc);
            tvExpiryDate = itemView.findViewById(R.id.tvExpiryDate);
            tvStatusBadge = itemView.findViewById(R.id.tvStatusBadge);
            btnUseCoupon = itemView.findViewById(R.id.btnUseCoupon);
        }
    }
}