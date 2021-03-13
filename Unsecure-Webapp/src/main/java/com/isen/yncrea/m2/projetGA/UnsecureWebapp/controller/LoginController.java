package com.isen.yncrea.m2.projetGA.UnsecureWebapp.controller;

import com.isen.yncrea.m2.projetGA.UnsecureWebapp.domain.Account;
import com.isen.yncrea.m2.projetGA.UnsecureWebapp.form.LoginForm;
import com.isen.yncrea.m2.projetGA.UnsecureWebapp.repository.AccountRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class LoginController {

    @Autowired
    private AccountRepository accounts;

    @GetMapping("/login")
    public String login(Model model) {
        LoginForm form = new LoginForm();
        model.addAttribute("loginForm",form);
        return "login";
    }

    @PostMapping("/login")
    public String loginPost(LoginForm form) {
        System.out.println("Form / Username = "+form.getUsername()+" | Password = "+form.getPassword());
        Account acc = accounts.findByUsername(form.getUsername());
        // Si le compte n'existe pas --> NO
        if(acc == null)
            return "NO";

        //TODO : Vérifier le password
        if(acc.getPassword().equals(form.getPassword()))
            return "YES";
        else
            return "NO";
    }
}
