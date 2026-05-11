package com.example.parkingapp;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CarAdapter extends RecyclerView.Adapter<CarAdapter.CarViewHolder> {

    private List<CarItem> carList;

    public CarAdapter(List<CarItem> carList) {
        this.carList = carList;
    }

    @NonNull
    @Override
    public CarViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        // item_car.xml을 가져와서 화면에 그릴 준비를 함
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_car, parent, false);
        return new CarViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CarViewHolder holder, int position) {
        // 데이터를 화면의 각 TextView에 연결함
        CarItem item = carList.get(position);
        holder.tvCarNumber.setText(item.getCarNumber());
        holder.tvCarModel.setText(item.getCarModel());
        holder.tvCarColor.setText(item.getCarColor());
        holder.tvCarYear.setText(item.getCarYear());

        // 주 차량이면 뱃지를 보여주고, 아니면 숨김
        if (item.isPrimary()) {
            holder.tvPrimaryBadge.setVisibility(View.VISIBLE);
        } else {
            holder.tvPrimaryBadge.setVisibility(View.GONE);
        }
    }

    @Override
    public int getItemCount() {
        return carList.size();
    }

    // 화면의 요소들을 찾아놓는 역할 (뷰홀더)
    static class CarViewHolder extends RecyclerView.ViewHolder {
        TextView tvCarNumber, tvCarModel, tvCarColor, tvCarYear, tvPrimaryBadge;

        public CarViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCarNumber = itemView.findViewById(R.id.tvCarNumber);
            tvCarModel = itemView.findViewById(R.id.tvCarModel);
            tvCarColor = itemView.findViewById(R.id.tvCarColor);
            tvCarYear = itemView.findViewById(R.id.tvCarYear);
            tvPrimaryBadge = itemView.findViewById(R.id.tvPrimaryBadge);
        }
    }
}