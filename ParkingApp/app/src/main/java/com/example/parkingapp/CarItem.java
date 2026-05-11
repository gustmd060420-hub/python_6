package com.example.parkingapp;

import com.google.gson.annotations.SerializedName;

public class CarItem {
    @SerializedName("plate")
    private String carNumber;
    @SerializedName("model")
    private String carModel;
    @SerializedName("color")
    private String carColor;
    @SerializedName("year")
    private String carYear;
    @SerializedName("is_default")
    private boolean isPrimary;

    public CarItem() {}

    public CarItem(String carNumber, String carModel, String carColor, String carYear, boolean isPrimary) {
        this.carNumber = carNumber;
        this.carModel = carModel;
        this.carColor = carColor;
        this.carYear = carYear;
        this.isPrimary = isPrimary;
    }

    public String getCarNumber() { return carNumber; }
    public String getCarModel() { return carModel; }
    public String getCarColor() { return carColor; }
    public String getCarYear() { return carYear; }
    public boolean isPrimary() { return isPrimary; }
}
