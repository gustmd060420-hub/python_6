<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="#FFFFFF">

    <!-- 상단 헤더 (주차패스 + 프로필) -->
    <RelativeLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:padding="20dp">
        <LinearLayout
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:gravity="center_vertical">
            <View
                android:id="@+id/btn_profile"
                android:layout_width="32dp"
                android:layout_height="32dp"
                android:background="#00C87E" />
            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="주차패스"
                android:textSize="20sp"
                android:textStyle="bold"
                android:layout_marginStart="8dp"
                android:textColor="#333333" />
        </LinearLayout>
        <View
            android:layout_width="36dp"
            android:layout_height="36dp"
            android:layout_alignParentEnd="true"
            android:background="#00C87E" />
    </RelativeLayout>

    <!-- 2x2 메뉴 그리드 -->
    <GridLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:columnCount="2"
        android:rowCount="2"
        android:layout_marginHorizontal="12dp"
        android:layout_marginTop="10dp">

        <!-- 1. 차량등록 -->
        <androidx.cardview.widget.CardView
            android:layout_width="0dp"
            android:layout_height="160dp"
            android:layout_columnWeight="1"
            android:layout_margin="8dp"
            app:cardCornerRadius="20dp"
            app:cardElevation="2dp">
            <LinearLayout android:orientation="vertical" android:padding="20dp" android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center_vertical">
                <View android:layout_width="48dp" android:layout_height="48dp" android:background="#E0F7ED" />
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="차량등록" android:textStyle="bold" android:layout_marginTop="12dp" android:textSize="16sp" android:textColor="#000000"/>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="내 차량 정보 관리" android:textSize="12sp" android:textColor="#888888"/>
            </LinearLayout>
        </androidx.cardview.widget.CardView>

        <!-- 2. 주차장 -->
        <androidx.cardview.widget.CardView
            android:layout_width="0dp"
            android:layout_height="160dp"
            android:layout_columnWeight="1"
            android:layout_margin="8dp"
            app:cardCornerRadius="20dp"
            app:cardElevation="2dp">
            <LinearLayout android:orientation="vertical" android:padding="20dp" android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center_vertical">
                <View android:layout_width="48dp" android:layout_height="48dp" android:background="#E0F7ED" />
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="주차장" android:textStyle="bold" android:layout_marginTop="12dp" android:textSize="16sp" android:textColor="#000000"/>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="주변 주차장 찾기" android:textSize="12sp" android:textColor="#888888"/>
            </LinearLayout>
        </androidx.cardview.widget.CardView>

        <!-- 3. 결제수단 -->
        <androidx.cardview.widget.CardView
            android:layout_width="0dp"
            android:layout_height="160dp"
            android:layout_columnWeight="1"
            android:layout_margin="8dp"
            app:cardCornerRadius="20dp"
            app:cardElevation="2dp">
            <LinearLayout android:orientation="vertical" android:padding="20dp" android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center_vertical">
                <View android:layout_width="48dp" android:layout_height="48dp" android:background="#E0F7ED" />
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="결제수단" android:textStyle="bold" android:layout_marginTop="12dp" android:textSize="16sp" android:textColor="#000000"/>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="결제 방법 설정" android:textSize="12sp" android:textColor="#888888"/>
            </LinearLayout>
        </androidx.cardview.widget.CardView>

        <!-- 4. 할인쿠폰 -->
        <androidx.cardview.widget.CardView
            android:layout_width="0dp"
            android:layout_height="160dp"
            android:layout_columnWeight="1"
            android:layout_margin="8dp"
            app:cardCornerRadius="20dp"
            app:cardElevation="2dp">
            <LinearLayout android:orientation="vertical" android:padding="20dp" android:layout_width="match_parent" android:layout_height="match_parent" android:gravity="center_vertical">
                <View android:layout_width="48dp" android:layout_height="48dp" android:background="#E0F7ED" />
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="할인쿠폰" android:textStyle="bold" android:layout_marginTop="12dp" android:textSize="16sp" android:textColor="#000000"/>
                <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="쿠폰 확인 및 사용" android:textSize="12sp" android:textColor="#888888"/>
            </LinearLayout>
        </androidx.cardview.widget.CardView>
    </GridLayout>

    <View
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />

    <!-- 하단 주차 현황 카드 -->
    <androidx.cardview.widget.CardView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_margin="16dp"
        app:cardBackgroundColor="#F0FBF5"
        app:cardCornerRadius="28dp"
        app:cardElevation="0dp">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="24dp">

            <!-- 위치 정보 -->
            <LinearLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:orientation="horizontal"
                android:gravity="center_vertical">
                <View android:layout_width="44dp" android:layout_height="44dp" android:background="#00C87E"/>
                <LinearLayout
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:layout_marginStart="14dp">
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="📍 강남역 공영주차장" android:textStyle="bold" android:textColor="#333333" android:textSize="16sp"/>
                    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="서울시 강남구 강남대로 지하 1층" android:textSize="13sp" android:textColor="#777777"/>
                </LinearLayout>
            </LinearLayout>

            <!-- 주차 시간 및 요금 (이 부분이 들어가야 휑하지 않아요!) -->
            <androidx.cardview.widget.CardView
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginTop="20dp"
                app:cardBackgroundColor="#FFFFFF"
                app:cardCornerRadius="16dp"
                app:cardElevation="0dp">
                <LinearLayout
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:padding="16dp"
                    android:orientation="horizontal">
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:orientation="vertical">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="🕒 주차 시간" android:textSize="13sp" android:textColor="#555555"/>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="00:00:08" android:textStyle="bold" android:textColor="#00C87E" android:textSize="18sp"/>
                    </LinearLayout>
                    <LinearLayout android:layout_width="0dp" android:layout_height="wrap_content" android:layout_weight="1" android:orientation="vertical">
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="예상 요금" android:textSize="13sp" android:textColor="#555555"/>
                        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="0원" android:textStyle="bold" android:textColor="#333333" android:textSize="18sp"/>
                    </LinearLayout>
                </LinearLayout>
            </androidx.cardview.widget.CardView>

            <!-- 출차하기 버튼 -->
            <Button
                android:id="@+id/btn_exit"
                android:layout_width="match_parent"
                android:layout_height="56dp"
                android:layout_marginTop="20dp"
                android:text="출차하기"
                android:backgroundTint="#00C87E"
                android:textSize="17sp"
                android:textStyle="bold"
                android:textColor="#FFFFFF" />
        </LinearLayout>
    </androidx.cardview.widget.CardView>

</LinearLayout>