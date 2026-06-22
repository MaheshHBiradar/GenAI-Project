// Neo4j Schema Initialization Script
// ABCL Relationship Graph Linkage constraints and indexes

CREATE CONSTRAINT customer_id_unique IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_id IS UNIQUE;
CREATE CONSTRAINT loan_id_unique IF NOT EXISTS FOR (l:Loan) REQUIRE l.loan_id IS UNIQUE;
CREATE CONSTRAINT payment_id_unique IF NOT EXISTS FOR (p:Payment) REQUIRE p.payment_id IS UNIQUE;
CREATE CONSTRAINT account_hash_unique IF NOT EXISTS FOR (a:Account) REQUIRE a.account_hash IS UNIQUE;
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (ag:Agent) REQUIRE ag.agent_id IS UNIQUE;
CREATE CONSTRAINT employee_id_unique IF NOT EXISTS FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE;
CREATE CONSTRAINT dsa_id_unique IF NOT EXISTS FOR (d:DSAMaster) REQUIRE d.dsa_id IS UNIQUE;
CREATE CONSTRAINT branch_id_unique IF NOT EXISTS FOR (b:Branch) REQUIRE b.branch_id IS UNIQUE;

// Indexes for performance
CREATE INDEX customer_name_index IF NOT EXISTS FOR (c:Customer) ON (c.full_name);
CREATE INDEX loan_lan_index IF NOT EXISTS FOR (l:Loan) ON (l.lan);
CREATE INDEX payment_ref_index IF NOT EXISTS FOR (p:Payment) ON (p.transaction_ref);
