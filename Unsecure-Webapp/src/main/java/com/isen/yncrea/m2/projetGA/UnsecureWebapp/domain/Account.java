package com.isen.yncrea.m2.projetGA.UnsecureWebapp.domain;

import lombok.Getter;
import lombok.Setter;

import javax.persistence.*;

@Getter
@Setter
@Entity
public class Account {
    @Id
    @Column
    @GeneratedValue
    private Long id;

    @Column(length = 100)
    private String username;

    @Column(length = 100)
    private String password;
}
