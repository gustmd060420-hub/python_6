package com.example.parkingapp;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class CarAdapter extends RecyclerView.Adapter<CarAdapter.CarViewHolder> {

    public interface OnDeleteClickListener {
        void onDelete(CarItem item);
    }

    private List<CarItem> carList;
    private OnDeleteClickListener deleteListener;

    public CarAdapter(List<CarItem> carList, OnDeleteClickListener deleteListener) {
        this.carList = carList;
        this.deleteListener = deleteListener;
    }

    @NonNull
    @Override
    public CarViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_car, parent, false);
        return new CarViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull CarViewHolder holder, int position) {
        CarItem item = carList.get(position);
        holder.tvCarNumber.setText(item.getCarNumber());
        holder.tvCarModel.setText(item.getCarModel());
        holder.tvCarColor.setText(item.getCarColor());
        holder.tvCarYear.setText(item.getCarYear());

        if (item.isPrimary()) {
            holder.tvPrimaryBadge.setVisibility(View.VISIBLE);
        } else {
            holder.tvPrimaryBadge.setVisibility(View.GONE);
        }

        holder.btnDelete.setOnClickListener(v -> {
            if (deleteListener != null) {
                deleteListener.onDelete(item);
            }
        });
    }

    @Override
    public int getItemCount() {
        return carList.size();
    }

    public void updateList(List<CarItem> newList) {
        carList.clear();
        carList.addAll(newList);
        notifyDataSetChanged();
    }

    static class CarViewHolder extends RecyclerView.ViewHolder {
        TextView tvCarNumber, tvCarModel, tvCarColor, tvCarYear, tvPrimaryBadge;
        ImageButton btnDelete;

        public CarViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCarNumber = itemView.findViewById(R.id.tvCarNumber);
            tvCarModel = itemView.findViewById(R.id.tvCarModel);
            tvCarColor = itemView.findViewById(R.id.tvCarColor);
            tvCarYear = itemView.findViewById(R.id.tvCarYear);
            tvPrimaryBadge = itemView.findViewById(R.id.tvPrimaryBadge);
            btnDelete = itemView.findViewById(R.id.btnDelete);
        }
    }
}
