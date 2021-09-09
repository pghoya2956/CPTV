package com.example.dronenetwork;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.appcompat.app.AppCompatActivity;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;

public class WebActivity extends AppCompatActivity {
    private WebView webView;
    private WebSettings webSettings;
    private Socket socket;
    private Thread clientThread;
    private InputStream in;
    private OutputStream out;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_web);

        //클라이언트 연결 쓰레드 시작
        clientThread = new Thread(new Runnable() {
            @Override
            public void run() {
                try{    
                    // 여기 IP만 수정
                    try {socket = new Socket("192.168.0.5",22044);}     catch (IOException e) {e.printStackTrace();}
                    try {in = socket.getInputStream();}                            catch (IOException e) {e.printStackTrace();}
                    try {out = socket.getOutputStream();}                          catch (IOException e) {e.printStackTrace();}
                } catch (Exception e) {e.printStackTrace();}
            }
        });
        clientThread.start();

        webView = (WebView)findViewById(R.id.webView);

        webView.setWebViewClient(new WebViewClient());
        webSettings = webView.getSettings(); //세부 세팅 등록
        webSettings.setJavaScriptEnabled(true); // 웹페이지 자바스클비트 허용 여부
        webSettings.setSupportMultipleWindows(false); // 새창 띄우기 허용 여부
        webSettings.setJavaScriptCanOpenWindowsAutomatically(false); // 자바스크립트 새창 띄우기(멀티뷰) 허용 여부
        webSettings.setLoadWithOverviewMode(true); // 메타태그 허용 여부
        webSettings.setUseWideViewPort(true); // 화면 사이즈 맞추기 허용 여부
        webSettings.setSupportZoom(false); // 화면 줌 허용 여부
        webSettings.setBuiltInZoomControls(false); // 화면 확대 축소 허용 여부
        webSettings.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.SINGLE_COLUMN); // 컨텐츠 사이즈 맞추기
        webSettings.setCacheMode(WebSettings.LOAD_NO_CACHE); // 브라우저 캐시 허용 여부
        webSettings.setDomStorageEnabled(true); // 로컬저장소 허용 여부

        webView.loadUrl("http://www.naver.com"); // 웹뷰에 표시할 웹사이트 주소, 웹뷰 시작

        /*
           byte[] data = selected.getBytes();
                try {out.write(data);}  catch (IOException e) {e.printStackTrace();}

                //close
                try {in.close();}       catch (IOException e) {e.printStackTrace();}
                try {out.close();}      catch (IOException e) {e.printStackTrace();}
                try {socket.close();}   catch (IOException e) {e.printStackTrace();}
         */
    }
}
