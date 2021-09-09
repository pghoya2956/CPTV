package com.example.dronenetwork;

import android.content.Intent;
import android.os.Bundle;
import android.app.Activity;
import android.preference.EditTextPreference;
import android.view.View;
import android.content.Intent;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

public class LoginActivity extends Activity {
    private FirebaseAuth mAuth;
    private Intent mvSign;
    private Intent mvMain;
    ;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        mvSign = new Intent(this, SignActivity.class);
        mvMain = new Intent(this,MainActivity.class);

        // Initialize Firebase Auth
        mAuth = FirebaseAuth.getInstance();
        findViewById(R.id.sign).setOnClickListener(onClickListener);
        findViewById(R.id.login).setOnClickListener(onClickListener);
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
            switch (v.getId()) {
                case R.id.sign:
                    startActivity(mvSign);
                    break;
                case R.id.login:
                    login();
                    break;
            }
        }
    };

    private void login() {
        String email = ((EditText) findViewById(R.id.editText3)).getText().toString();
        String password = ((EditText) findViewById(R.id.editText4)).getText().toString();

        mAuth.signInWithEmailAndPassword(email, password)
                .addOnCompleteListener(this, new OnCompleteListener<AuthResult>() {
                    @Override
                    public void onComplete(@NonNull Task<AuthResult> task) {
                        if (task.isSuccessful()) {
                            // Sign in success, update UI with the signed-in user's information
                            Toast.makeText(LoginActivity.this, "로그인에 성공하였습니다.", Toast.LENGTH_LONG).show();
                            FirebaseUser user = mAuth.getCurrentUser();
                            startActivity(mvMain);
                        } else {
                            Toast.makeText(LoginActivity.this, "로그인에 실패하였습니다.", Toast.LENGTH_LONG).show();
                        }
                    }
                });
    }
}

