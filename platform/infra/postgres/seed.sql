INSERT INTO users (id,email,password_hash,role) VALUES
('11111111-1111-1111-1111-111111111111','customer@pulse.local','$2b$12$4g0BAmtmXgVQq4bR5T6pD.5C8YdwEHkKI28yi0RrAqBIVHFeq4m5m','customer'),
('22222222-2222-2222-2222-222222222222','agent@pulse.local','$2b$12$4g0BAmtmXgVQq4bR5T6pD.5C8YdwEHkKI28yi0RrAqBIVHFeq4m5m','support_agent')
ON CONFLICT (email) DO NOTHING;

INSERT INTO accounts (id,account_number,user_id,full_name,phone,billing_address,status) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','PLS-100001','11111111-1111-1111-1111-111111111111','Demo Customer','+15555550100','100 Pulse Avenue','active')
ON CONFLICT (account_number) DO NOTHING;

INSERT INTO plans (id,code,name,monthly_price,description) VALUES
('30000000-0000-0000-0000-000000000001','STARTER','Pulse Starter',35.00,'5G starter plan with 20GB high-speed data'),
('30000000-0000-0000-0000-000000000002','PLUS','Pulse Plus',65.00,'Unlimited talk, text and premium 5G data'),
('30000000-0000-0000-0000-000000000003','FAMILY','Pulse Family',110.00,'Up to four lines with shared benefits')
ON CONFLICT (code) DO NOTHING;

INSERT INTO account_plans (id,account_id,plan_id,active) VALUES
('40000000-0000-0000-0000-000000000001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','30000000-0000-0000-0000-000000000002',true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO devices (id,account_id,line_number,device_identifier,model,financed,payoff_amount,upgrade_eligible_at) VALUES
('50000000-0000-0000-0000-000000000001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa','+15555550100','IMEI-DEMO-001','PulsePhone Pro',false,0,now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO invoices (id,account_id,period_start,period_end,subtotal,tax,total,status,due_at) VALUES
('60000000-0000-0000-0000-000000000001','aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',CURRENT_DATE - 30,CURRENT_DATE,65,4.55,69.55,'open',now()+interval '14 days')
ON CONFLICT (id) DO NOTHING;

INSERT INTO knowledge_documents (id,title,content,metadata) VALUES
('70000000-0000-0000-0000-000000000001','Upgrade policy','Customers with no remaining device payoff and an account in good standing may upgrade immediately. Financed devices must be paid off before upgrade.','{"category":"devices","audience":"customer"}'),
('70000000-0000-0000-0000-000000000002','Plan change policy','Plan upgrades can be scheduled immediately or for the next billing cycle. Downgrades take effect at the next billing cycle to avoid loss of paid benefits.','{"category":"plans","audience":"customer"}')
ON CONFLICT (id) DO NOTHING;
