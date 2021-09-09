package com.example.dronenetwork;

import android.os.Bundle;
import android.app.Activity;
import android.os.Handler;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import android.widget.ImageView;
import androidx.annotation.NonNull;
import java.lang.Runnable;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

public class SignActivity extends Activity {
    private FirebaseAuth mAuth;
    ImageView approveImage;
    private int successCheck;

    @Override
    protected void onCreate(Bundle savedInstanceState){
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sign);
        approveImage = (ImageView) findViewById(R.id.image6);
        approveImage.setVisibility(View.INVISIBLE);
        // Initialize Firebase Auth
        mAuth = FirebaseAuth.getInstance();
        successCheck = 0;

        findViewById(R.id.sign).setOnClickListener(onClickListener);
        findViewById(R.id.back).setOnClickListener(onClickListener);
    }
    @Override
    public void onStart() {
        super.onStart();
        // Check if user is signed in (non-null) and update UI accordingly.
        FirebaseUser currentUser = mAuth.getCurrentUser();
    }

    View.OnClickListener onClickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            switch (v.getId()){
                case R.id.sign:
                    signUp();
                     new Handler().postDelayed(new Runnable() {
                        @Override
                        public void run() {
                            if(successCheck==1)finish();}
                    },4000);
                    break;
                case R.id.back:
                    finish();
                    break;
            }
        }
    };

    private void signUp(){
        String email = ((EditText)findViewById(R.id.txt_id)).getText().toString();
        String password = ((EditText)findViewById(R.id.txt_pw)).getText().toString();
        String passwordCheck = ((EditText)findViewById(R.id.txt_pw2)).getText().toString();

        //공란 방지
        if(email.length() > 0 && password.length() > 0){
            //비밀번호와 체크 비교
            if(password.equals(passwordCheck)){
                mAuth.createUserWithEmailAndPassword(email, password)
                        .addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                            @Override
                            public void onComplete(@NonNull Task<AuthResult> task) {
                                if (task.isSuccessful()) {
                                    // Sign in success, update UI with the signed-in user's information
                                    Toast.makeText(SignActivity.this, "회원가입이 완료되었습니다.", Toast.LENGTH_LONG).show();
                                    successCheck = 1;
                                    FirebaseUser user = mAuth.getCurrentUser();
                                    approveImage.setVisibility(View.VISIBLE);
                                    //UI
                                } else {
                                    // If sign in fails, display a message to the user.
                                    Toast.makeText(SignActivity.this, "회원가입에 실패하였습니다.", Toast.LENGTH_LONG).show();
                                    //UI
                                }
                            }
                        });
            }
            else {
                Toast.makeText(SignActivity.this, "비밀번호가 일치하지 않습니다.", Toast.LENGTH_LONG).show();
            }
        }
    }
}
