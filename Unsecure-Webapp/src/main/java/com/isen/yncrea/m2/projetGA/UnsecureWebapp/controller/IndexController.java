package com.isen.yncrea.m2.projetGA.UnsecureWebapp.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class IndexController {

    @GetMapping("/")
    public String welcome(Model model) {
        model.addAttribute("message", "Bienvenue sur un site pas très secure");
        return "welcome";
    }
}
