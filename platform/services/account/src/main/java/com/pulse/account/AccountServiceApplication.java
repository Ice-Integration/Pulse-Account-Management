package com.pulse.account;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@SpringBootApplication
public class AccountServiceApplication {
  public static void main(String[] args) { SpringApplication.run(AccountServiceApplication.class, args); }
}

@RestController
@RequestMapping("/accounts")
class AccountController {
  private final JdbcTemplate jdbc;
  private final String serviceKey;

  AccountController(JdbcTemplate jdbc, @Value("${pulse.service-key}") String serviceKey) {
    if (serviceKey.isBlank()) throw new IllegalStateException("pulse.service-key must be set");
    this.jdbc = jdbc;
    this.serviceKey = serviceKey;
  }

  private void requireServiceKey(String provided) {
    if (provided == null || !provided.equals(serviceKey)) {
      throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "invalid_service_key");
    }
  }

  @GetMapping("/{id}/owner")
  Map<String,Object> owner(@PathVariable UUID id, @RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    var rows = jdbc.queryForList("SELECT user_id FROM accounts WHERE id=?", id);
    if (rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "account_not_found");
    return rows.getFirst();
  }

  @GetMapping("/{id}")
  Map<String,Object> get(@PathVariable UUID id, @RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    var rows = jdbc.queryForList("SELECT id,account_number,full_name,phone,billing_address,status FROM accounts WHERE id=?", id);
    if (rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "account_not_found");
    var account = rows.getFirst();
    account.put("devices", jdbc.queryForList("SELECT id,line_number,device_identifier,model,financed,payoff_amount,upgrade_eligible_at FROM devices WHERE account_id=?", id));
    account.put("plans", jdbc.queryForList("SELECT p.id,p.code,p.name,p.monthly_price,p.description,ap.effective_at FROM account_plans ap JOIN plans p ON p.id=ap.plan_id WHERE ap.account_id=? AND ap.active=true", id));
    return account;
  }

  @PatchMapping("/{id}")
  Map<String,Object> update(@PathVariable UUID id, @RequestBody AccountUpdate body, @RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    int updated = jdbc.update("UPDATE accounts SET phone=COALESCE(?,phone), billing_address=COALESCE(?,billing_address), updated_at=now() WHERE id=?", body.phone(), body.billingAddress(), id);
    if (updated == 0) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "account_not_found");
    jdbc.update("INSERT INTO audit_logs(actor_user_id,account_id,action,metadata) VALUES (NULL,?,'account.updated',jsonb_build_object('source','account-service'))", id);
    return get(id, key);
  }

  @GetMapping("/{id}/upgrade-eligibility")
  List<Map<String,Object>> eligibility(@PathVariable UUID id, @RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    return jdbc.queryForList("SELECT id,line_number,model,financed,payoff_amount,upgrade_eligible_at, (NOT financed OR payoff_amount=0 OR upgrade_eligible_at<=?) AS eligible FROM devices WHERE account_id=?", OffsetDateTime.now(), id);
  }

  @GetMapping("/{id}/orders")
  List<Map<String,Object>> orders(@PathVariable UUID id, @RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    return jdbc.queryForList("SELECT id,type,status,total,created_at FROM orders WHERE account_id=? ORDER BY created_at DESC", id);
  }

  @GetMapping("/plans/catalog")
  List<Map<String,Object>> plans(@RequestHeader(value = "X-Service-Key", required = false) String key) {
    requireServiceKey(key);
    return jdbc.queryForList("SELECT id,code,name,monthly_price,description FROM plans WHERE active=true ORDER BY monthly_price");
  }

  record AccountUpdate(String phone, String billingAddress) {}
}
