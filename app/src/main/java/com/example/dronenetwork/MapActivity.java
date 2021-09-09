package com.example.dronenetwork;

import android.Manifest;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Address;
import android.location.Geocoder;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.StrictMode;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class MapActivity extends FragmentActivity implements OnMapReadyCallback {
    private static final int GPS_ENABLE_REQUEST_CODE = 2001;
    private static final int PERMISSIONS_REQUEST_CODE = 100;
    double latitude;
    double longitude;
    String[] REQUIRED_PERMISSIONS = {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION};
    GoogleMap mMap;
    MarkerOptions makerOp;
    Spinner spinner;
    TextView tv;
    String selected;
    Button btn;
    ArrayList<String> dzNum;
    ArrayList<Double> dzLatitude;
    ArrayList<Double> dzLongitude;

    private GpsTracker gpsTracker;
    private Socket socket;
    private Thread clientThread;
    private InputStream in;
    private OutputStream out;
    private Intent mvWeb;
    @Override
    protected void onCreate(Bundle saveInstanceState){
        super.onCreate(saveInstanceState);
        setContentView(R.layout.activity_map);

        //WebActivity 연결
        mvWeb = new Intent(this,WebActivity.class);

        //허가코드
        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        //Activity_map 기능 가져오기
        spinner =   (Spinner)findViewById(R.id.spinner);
        tv =        (TextView)findViewById(R.id.TV);
        btn =       (Button)findViewById(R.id.button2);

        //Set CCTV Position
        dzNum = new ArrayList<String>();
        dzLatitude = new ArrayList<Double>();
        dzLongitude = new ArrayList<Double>();
        setPoint("0", 35.132790, 129.105719);
        setPoint("1", 35.133036, 129.105700);
        setPoint("2", 35.133191, 129.105683);
        setPoint("3", 35.133244, 129.105968);
        setPoint("4", 35.133055, 129.105962);
        setPoint("5", 35.132807, 129.105968);
        setPoint("6", 35.132663, 129.105967);
        setPoint("7", 35.132463, 129.105953);
        setPoint("8", 35.132495, 129.106159);
        setPoint("9", 35.132628, 129.106135);
        setPoint("10", 35.132800, 129.106187);
        setPoint("11", 35.133012, 129.106114);
        setPoint("12", 35.133223, 129.106086);
        setPoint("13", 35.133212, 129.106441);
        setPoint("14", 35.132995, 129.106451);
        setPoint("15", 35.132805, 129.106441);
        setPoint("16", 35.132634, 129.106521);
        setPoint("17", 35.132512, 129.106528);
        setPoint("18", 35.132517, 129.106692);
        setPoint("19", 35.132660, 129.106689);
        setPoint("20", 35.132800, 129.106689);

        //Set Spinner
        spinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {selected = spinner.getSelectedItem().toString();}
            @Override
            public void onNothingSelected(AdapterView<?> parent) {}
        });

        //GPS
        gpsTracker = new GpsTracker(MapActivity.this); //GPS변수
        if (!checkLocationServicesStatus()) showDialogForLocationServiceSetting();
        else checkRunTimePermission();

        //Get Latitude & Longitude
        latitude = gpsTracker.getLatitude();    //위도
        longitude = gpsTracker.getLongitude();  //경도

        //Google Map
        SupportMapFragment mapFragment = (SupportMapFragment)getSupportFragmentManager().findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        //Button Event
        btn.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View v) {
                //send data
                byte[] data = selected.getBytes();
                try {out.write(data);}  catch (IOException e) {e.printStackTrace();}

                //close
                try {in.close();}       catch (IOException e) {e.printStackTrace();}
                try {out.close();}      catch (IOException e) {e.printStackTrace();}

                //change to WebActivity
                startActivity(mvWeb);
            }
        });
    }

    @Override
    public void onRequestPermissionsResult (int permsRequestCode, @NonNull String[] permissions, @NonNull int[] grandResults){
        if (permsRequestCode == PERMISSIONS_REQUEST_CODE && grandResults.length == REQUIRED_PERMISSIONS.length) {
            // 요청 코드가 PERMISSIONS_REQUEST_CODE 이고, 요청한 퍼미션 개수만큼 수신되었다면
            boolean check_result = true;

            // 모든 퍼미션을 허용했는지 체크합니다.
            for (int result : grandResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    check_result = false;
                    break;
                }
            }

            if (check_result) {
                //위치 값을 가져올 수 있음
            } else {
                // 거부한 퍼미션이 있다면 앱을 사용할 수 없는 이유를 설명해주고 앱을 종료합니다.2 가지 경우가 있습니다.
                if (ActivityCompat.shouldShowRequestPermissionRationale(this, REQUIRED_PERMISSIONS[0])
                        || ActivityCompat.shouldShowRequestPermissionRationale(this, REQUIRED_PERMISSIONS[1])) {
                    Toast.makeText(MapActivity.this, "퍼미션이 거부되었습니다. 앱을 다시 실행하여 퍼미션을 허용해주세요.", Toast.LENGTH_LONG).show();
                    finish();
                } else {
                    Toast.makeText(MapActivity.this, "퍼미션이 거부되었습니다. 설정(앱 정보)에서 퍼미션을 허용해야 합니다. ", Toast.LENGTH_LONG).show();
                }
            }
        }
    }
    void checkRunTimePermission(){
        //런타임 퍼미션 처리
        // 1. 위치 퍼미션을 가지고 있는지 체크합니다.
        int hasFineLocationPermission = ContextCompat.checkSelfPermission(MapActivity.this, Manifest.permission.ACCESS_FINE_LOCATION);
        int hasCoarseLocationPermission = ContextCompat.checkSelfPermission(MapActivity.this, Manifest.permission.ACCESS_COARSE_LOCATION);

        if (hasFineLocationPermission == PackageManager.PERMISSION_GRANTED && hasCoarseLocationPermission == PackageManager.PERMISSION_GRANTED) {
            // 2. 이미 퍼미션을 가지고 있다면
            // ( 안드로이드 6.0 이하 버전은 런타임 퍼미션이 필요없기 때문에 이미 허용된 걸로 인식합니다.)
            // 3.  위치 값을 가져올 수 있음
        } else {
            //2. 퍼미션 요청을 허용한 적이 없다면 퍼미션 요청이 필요합니다. 2가지 경우(3-1, 4-1)가 있습니다.
            // 3-1. 사용자가 퍼미션 거부를 한 적이 있는 경우에는
            if (ActivityCompat.shouldShowRequestPermissionRationale(MapActivity.this, REQUIRED_PERMISSIONS[0])) {
                // 3-2. 요청을 진행하기 전에 사용자가에게 퍼미션이 필요한 이유를 설명해줄 필요가 있습니다.
                Toast.makeText(MapActivity.this, "이 앱을 실행하려면 위치 접근 권한이 필요합니다.", Toast.LENGTH_LONG).show();
                // 3-3. 사용자게에 퍼미션 요청을 합니다. 요청 결과는 onRequestPermissionResult에서 수신됩니다.
                ActivityCompat.requestPermissions(MapActivity.this, REQUIRED_PERMISSIONS,
                        PERMISSIONS_REQUEST_CODE);
            } else {
                // 4-1. 사용자가 퍼미션 거부를 한 적이 없는 경우에는 퍼미션 요청을 바로 합니다.
                // 요청 결과는 onRequestPermissionResult에서 수신됩니다.
                ActivityCompat.requestPermissions(MapActivity.this, REQUIRED_PERMISSIONS,
                        PERMISSIONS_REQUEST_CODE);
            }
        }
    }
    public String getCurrentAddress(double latitude, double longitude){
        //지오코더... GPS를 주소로 변환
        Geocoder geocoder = new Geocoder(this, Locale.getDefault());
        List<Address> addresses;
        try {
            addresses = geocoder.getFromLocation(latitude, longitude, 7);
        } catch (IOException ioException) {
            //네트워크 문제
            Toast.makeText(this, "지오코더 서비스 사용불가", Toast.LENGTH_LONG).show();
            return "지오코더 서비스 사용불가";
        } catch (IllegalArgumentException illegalArgumentException) {
            Toast.makeText(this, "잘못된 GPS 좌표", Toast.LENGTH_LONG).show();
            return "잘못된 GPS 좌표";
        }

        if (addresses == null || addresses.size() == 0) {
            Toast.makeText(this, "주소 미발견", Toast.LENGTH_LONG).show();
            return "주소 미발견";
        }

        Address address = addresses.get(0);
        return address.getAddressLine(0).toString() + "\n";
    }
    private void showDialogForLocationServiceSetting () {
        AlertDialog.Builder builder = new AlertDialog.Builder(MapActivity.this);
        builder.setTitle("위치 서비스 비활성화");
        builder.setMessage("앱을 사용하기 위해서는 위치 서비스가 필요합니다.\n"
                + "위치 설정을 수정하실래요?");
        builder.setCancelable(true);
        builder.setPositiveButton("설정", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int id) {
                Intent callGPSSettingIntent
                        = new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                startActivityForResult(callGPSSettingIntent, GPS_ENABLE_REQUEST_CODE);
            }
        });
        builder.setNegativeButton("취소", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int id) {
                dialog.cancel();
            }
        });
        builder.create().show();
    }
    @Override
    protected void onActivityResult ( int requestCode, int resultCode, Intent data){
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case GPS_ENABLE_REQUEST_CODE:
                //사용자가 GPS 활성 시켰는지 검사
                if (checkLocationServicesStatus()) {
                    if (checkLocationServicesStatus()) {
                        Log.d("@@@", "onActivityResult : GPS 활성화 되있음");
                        checkRunTimePermission();
                        return;
                    }
                }
                break;
        }
    }
    public boolean checkLocationServicesStatus(){
        LocationManager locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
                || locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
    }

    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        makerOp = new MarkerOptions();
        LatLng base = new LatLng(latitude,longitude);

        //Current GPS Position Marking
        makerOp.position(base).title("Current Position.");
        mMap.addMarker(makerOp);
        mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(base,16));    //color = RED

        //DroneZone Base GPS Position Marking
        LatLng base2 = new LatLng(dzLatitude.get(0),dzLongitude.get(0));
        makerOp.position(base2).title(dzNum.get(0)).icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_CYAN));    //color = CYAN
        mMap.addMarker(makerOp);

        //Dronezone GPS Position Marking
        for(int i=1;i< dzNum.size();i++){
            LatLng subBase = new LatLng(dzLatitude.get(i),dzLongitude.get(i));
            makerOp.position(subBase).title(dzNum.get(i)).icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_BLUE));    //color = BLUE
            mMap.addMarker(makerOp);
        }
    }

    public void setPoint(String num, Double x, Double y){
        dzNum.add(num);     dzLatitude.add(x); dzLongitude.add(y);
    }
}
