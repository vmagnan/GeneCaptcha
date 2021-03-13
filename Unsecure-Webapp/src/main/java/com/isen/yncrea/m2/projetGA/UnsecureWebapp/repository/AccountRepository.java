package com.isen.yncrea.m2.projetGA.UnsecureWebapp.repository;

import com.isen.yncrea.m2.projetGA.UnsecureWebapp.domain.Account;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AccountRepository extends JpaRepository<Account, Long> {
    Account findByUsername(String username);

}
