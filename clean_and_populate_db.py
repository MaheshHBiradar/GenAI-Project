import os
import sys
import time
import uuid
import random
from datetime import datetime, date, timedelta
from sqlalchemy import text, func
import bcrypt

sys.path.insert(0, "./abcl_ai_platform")
from app.database import engine, SessionLocal
from app.models.sentinel import (
    Base, User, Role, Employee, Branch, Customer, Case, Payment, Target, FraudScore, RiskScore,
    Permission, RolePermission, Agency, Agent, DSAMaster, CustomerBankAccount, Loan, LoanRepaymentSchedule,
    LoanAllocation, CollectionVisit, CollectionTarget, FraudRule, FraudAlert, AnomalyFeature, FundingSourceCluster,
    FundingSourceClusterMember, ThirdPartyRelationship, CircularTransaction, EmployeeLogin, CustomerAccessLog,
    ApprovalTransaction, DataExport, CaseEvidence, CaseTimeline, CaseNote, CaseEscalation, CustomerConfirmation,
    MessageTemplate, MLModel, MLPrediction, FeedbackLearning, AuditLog, APIIngestionLog, CIBILInquiry, EscalationMatrix,
    PaymentSourceFlag
)

class IndianNameGenerator:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan", "Shaurya",
            "Atharv", "Anvesha", "Aanya", "Diya", "Pihu", "Prisha", "Ananya", "Aadhya", "Saanvi", "Sanya",
            "Rahul", "Amit", "Sanjay", "Vijay", "Rajesh", "Ramesh", "Suresh", "Dinesh", "Ganesh", "Mahesh",
            "Anil", "Sunil", "Raj", "Rohan", "Vikram", "Ajay", "Sandeep", "Deepak", "Pankaj", "Manish",
            "Pooja", "Neha", "Aarti", "Priya", "Jyoti", "Kiran", "Kavita", "Sunita", "Anita", "Ritu",
            "Rohit", "Hardik", "Virat", "Shikhar", "Jasprit", "Ravindra", "Bhuvneshwar", "Yuzvendra", "Kuldeep", "Rishabh",
            "Krunal", "Surya", "Ishani", "Avani", "Riya", "Sneha", "Tanya", "Meera", "Radha", "Rukmini",
            "Dev", "Kabir", "Rudra", "Karan", "Abhishek", "Aakash", "Varun", "Siddharth", "Yash", "Pranav",
            "Kavya", "Ishita", "Sriti", "Aditi", "Shruti", "Tanvi", "Simran", "Preeti", "Payal", "Shreya"
        ]
        self.last_names = [
            "Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Mehta", "Joshi", "Shah", "Trivedi",
            "Chatterjee", "Mukherjee", "Banerjee", "Bose", "Sen", "Das", "Choudhury", "Roy", "Nair", "Pillai",
            "Menon", "Iyer", "Iyengar", "Rao", "Reddy", "Naidu", "Chowdary", "Prasad", "Yadav", "Maurya",
            "Koli", "Patil", "Deshmukh", "Kulkarni", "Joshi", "Bhavsar", "Mishra", "Pandey", "Dubey", "Tiwari",
            "Sinha", "Sahay", "Srivastava", "Saxena", "Johri", "Mathur", "Nayan", "Kapoor", "Khan", "Malhotra",
            "Chawla", "Bhasin", "Ahluwalia", "Grover", "Sethi", "Bakshi", "Thakur", "Rathore", "Shekhawat", "Solanki"
        ]
        self.agency_prefixes = [
            "Birla", "Tata", "Reliance", "HDFC", "ICICI", "SBI", "Bajaj", "Kotak", "Axis", "L&T",
            "Mahindra", "Muthoot", "Manappuram", "Cholamandalam", "Shriram", "IndusInd", "Yes Bank", "IDFC First", "Bandhan", "Sundaram"
        ]
        self.agency_suffixes = [
            "Recovery Services", "Collection Partners", "Vigilance Agency", "Credit & Collection Associates",
            "Financial Recovery Solutions", "Debt Management Systems", "Collections & Recovery Group"
        ]

    def get_name(self):
        first = self.rng.choice(self.first_names)
        last = self.rng.choice(self.last_names)
        return f"{first} {last}"

    def get_agency(self):
        prefix = self.rng.choice(self.agency_prefixes)
        suffix = self.rng.choice(self.agency_suffixes)
        return f"{prefix} {suffix}"

def clean_and_populate():
    db = SessionLocal()
    raw_conn = engine.raw_connection()
    gen = IndianNameGenerator(42)
    
    try:
        # Step 1: Truncate all tables
        print("[SENTINEL] Truncating all database tables...")
        with raw_conn.cursor() as cur:
            cur.execute("SET session_replication_role = 'replica';")
            for table_name in reversed(Base.metadata.sorted_tables):
                print(f"  Truncating {table_name.name}...")
                cur.execute(f'TRUNCATE TABLE "{table_name.name}" CASCADE;')
            cur.execute("SET session_replication_role = 'origin';")
            raw_conn.commit()
        print("[SENTINEL] Truncation complete.")

        # Step 2: Seed Roles and Permissions
        print("[SENTINEL] Seeding Roles and Permissions...")
        roles_data = [
            {"role_name": "Admin", "role_level": 1, "description": "System Administrator"},
            {"role_name": "Collection Manager", "role_level": 2, "description": "Vigilance & Team Manager"},
            {"role_name": "Agency Supervisor", "role_level": 3, "description": "Field Collection Agent Supervisor"}
        ]
        roles_dict = {}
        for r_spec in roles_data:
            role = Role(role_id=uuid.uuid4(), role_name=r_spec["role_name"], role_level=r_spec["role_level"], description=r_spec["description"])
            db.add(role)
            db.flush()
            roles_dict[r_spec["role_name"]] = role

        permissions_data = [
            {"module": "Dashboard", "code": "VIEW_DASHBOARD", "desc": "View dashboard KPIs and charts"},
            {"module": "Agent", "code": "VIEW_AGENT", "desc": "View agent profiles and fraud metrics"},
            {"module": "Case", "code": "VIEW_CASE", "desc": "View case detail and timeline"},
            {"module": "Case", "code": "APPROVE_CASE", "desc": "Approve cases and overrides"},
            {"module": "Audit", "code": "VIEW_AUDIT", "desc": "View audit trails"}
        ]
        for p_spec in permissions_data:
            perm = Permission(permission_id=uuid.uuid4(), module_name=p_spec["module"], permission_code=p_spec["code"], description=p_spec["desc"])
            db.add(perm)
            db.flush()
            # Link to Admin Role
            rp = RolePermission(id=uuid.uuid4(), role_id=roles_dict["Admin"].role_id, permission_id=perm.permission_id)
            db.add(rp)

        # Step 3: Seed Branches
        print("[SENTINEL] Seeding Branches...")
        branch_specs = [
            {"code": "MUM01", "name": "Mumbai Corporate Branch", "city": "Mumbai", "state": "Maharashtra", "zone": "West"},
            {"code": "DEL01", "name": "Delhi Central Branch", "city": "Delhi", "state": "Delhi", "zone": "North"},
            {"code": "BLR01", "name": "Bengaluru Tech Hub Branch", "city": "Bengaluru", "state": "Karnataka", "zone": "South"},
            {"code": "KOL01", "name": "Kolkata Metro Branch", "city": "Kolkata", "state": "West Bengal", "zone": "East"},
            {"code": "CHN01", "name": "Chennai Main Branch", "city": "Chennai", "state": "Tamil Nadu", "zone": "South"}
        ]
        branches = []
        for b_spec in branch_specs:
            br = Branch(
                branch_id=uuid.uuid4(),
                branch_code=b_spec["code"],
                branch_name=b_spec["name"],
                city=b_spec["city"],
                state=b_spec["state"],
                zone=b_spec["zone"],
                region=b_spec["zone"],
                risk_category="LOW" if b_spec["city"] != "Mumbai" else "MEDIUM",
                is_active=True
            )
            db.add(br)
            db.flush()
            branches.append(br)
        db.commit()

        # Step 4: Seed Agencies
        print("[SENTINEL] Seeding Agencies...")
        agencies = []
        for i in range(10):
            brand = gen.get_agency()
            agency = Agency(
                agency_id=uuid.uuid4(),
                agency_code=f"AGY{10000+i}",
                agency_name=brand,
                branch_id=random.choice(branches).branch_id,
                agency_type="Collection" if i % 2 == 0 else "Recovery",
                status="ACTIVE",
                onboarding_date=date.today() - timedelta(days=random.randint(100, 500))
            )
            db.add(agency)
            db.flush()
            agencies.append(agency)
        db.commit()

        # Step 5: Seed Employees
        print("[SENTINEL] Seeding Employees...")
        employees = []
        # Create some managers first
        managers_emp = []
        for i in range(10):
            emp = Employee(
                employee_id=uuid.uuid4(),
                employee_code=f"EMP-MGR{100+i}",
                full_name=gen.get_name(),
                department="Vigilance",
                designation="Collection Manager",
                branch_id=random.choice(branches).branch_id,
                reporting_manager_id=None,
                approval_limit=50000.00,
                joining_date=date.today() - timedelta(days=random.randint(400, 800)),
                status="ACTIVE",
                risk_score=0.00
            )
            db.add(emp)
            db.flush()
            managers_emp.append(emp)
            employees.append(emp)

        # Create agent employees
        agents_emp = []
        for i in range(100):
            emp = Employee(
                employee_id=uuid.uuid4(),
                employee_code=f"EMP-AGT{1000+i}",
                full_name=gen.get_name(),
                department="Collections",
                designation="Collection Officer",
                branch_id=random.choice(branches).branch_id,
                reporting_manager_id=random.choice(managers_emp).employee_id,
                approval_limit=10000.00,
                joining_date=date.today() - timedelta(days=random.randint(100, 300)),
                status="ACTIVE",
                risk_score=0.00
            )
            db.add(emp)
            db.flush()
            agents_emp.append(emp)
            employees.append(emp)
        db.commit()

        # Step 6: Seed Users
        print("[SENTINEL] Seeding Users...")
        def get_hash(pw: str) -> str:
            return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
        demo_specs = [
            {"username": "admin", "email": "admin@abcl.example", "password": "12345678", "role_name": "Admin", "flat_role": "admin"},
            {"username": "manager", "email": "manager@abcl.example", "password": "12345678", "role_name": "Collection Manager", "flat_role": "manager"},
            {"username": "agent", "email": "agent@abcl.example", "password": "12345678", "role_name": "Agency Supervisor", "flat_role": "agent"}
        ]
        
        seeded_users = []
        for spec in demo_specs:
            role = roles_dict[spec["role_name"]]
            user = User(
                user_id=uuid.uuid4(),
                employee_id=None,
                username=spec["username"],
                email=spec["email"],
                mobile="9000000000",
                password_hash=get_hash(spec["password"]),
                role_id=role.role_id,
                role=spec["flat_role"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                branch_id=random.choice(branches).branch_id
            )
            db.add(user)
            db.flush()
            seeded_users.append(user)

        # Link seeded manager and agent to employee records so reporting works
        seeded_mgr = [u for u in seeded_users if u.username == "manager"][0]
        seeded_mgr.employee_id = managers_emp[0].employee_id
        
        seeded_agt = [u for u in seeded_users if u.username == "agent"][0]
        seeded_agt.employee_id = agents_emp[0].employee_id
        # seeded agent reports to seeded manager
        agents_emp[0].reporting_manager_id = managers_emp[0].employee_id
        db.commit()

        # Create user accounts for managers and agents
        users = list(seeded_users)
        
        for idx, mgr_emp in enumerate(managers_emp):
            # Skip first manager employee since seeded 'manager' links to it
            if idx == 0:
                continue
            username = mgr_emp.full_name.lower().replace(" ", ".")
            user = User(
                user_id=uuid.uuid4(),
                employee_id=mgr_emp.employee_id,
                username=username,
                email=f"{username}@abcl.example",
                mobile=f"9876543{idx:03d}",
                password_hash=get_hash("12345678"),
                role_id=roles_dict["Collection Manager"].role_id,
                role="manager",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                branch_id=mgr_emp.branch_id
            )
            db.add(user)
            db.flush()
            users.append(user)

        agent_users = []
        # The seeded 'agent' user counts as agent 0
        agent_users.append(seeded_agt)

        for idx, agt_emp in enumerate(agents_emp):
            if idx == 0:
                continue
            username = agt_emp.full_name.lower().replace(" ", ".")
            user = User(
                user_id=uuid.uuid4(),
                employee_id=agt_emp.employee_id,
                username=username,
                email=f"{username}@abcl.example",
                mobile=f"9988776{idx:03d}",
                password_hash=get_hash("12345678"),
                role_id=roles_dict["Agency Supervisor"].role_id,
                role="agent",
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                branch_id=agt_emp.branch_id
            )
            db.add(user)
            db.flush()
            users.append(user)
            agent_users.append(user)
        db.commit()

        # Step 7: Seed DSAMaster and Agents
        print("[SENTINEL] Seeding DSA and Field Agent records...")
        dsas = []
        for i in range(10):
            dsa = DSAMaster(
                dsa_id=uuid.uuid4(),
                dsa_code=f"DSA{5000+i}",
                dsa_name=f"{gen.get_name()} & Associates",
                agency_id=random.choice(agencies).agency_id,
                branch_id=random.choice(branches).branch_id,
                status="ACTIVE",
                risk_score=0.00
            )
            db.add(dsa)
            db.flush()
            dsas.append(dsa)

        agents_records = []
        # Linked directly to agent user accounts
        for idx, ag_user in enumerate(agent_users):
            agent = Agent(
                agent_id=uuid.uuid4(),
                agent_code=f"COL{10000+idx}",
                agent_name=ag_user.username.replace(".", " ").title(),
                agency_id=random.choice(agencies).agency_id,
                branch_id=ag_user.branch_id,
                territory=f"Zone-{random.randint(1, 10)}",
                mobile=ag_user.mobile,
                status="ACTIVE",
                risk_score=0.00
            )
            db.add(agent)
            db.flush()
            agents_records.append(agent)
        db.commit()

        # Step 8: Seed Customers
        print("[SENTINEL] Seeding Customers...")
        customers = []
        for i in range(2000):
            name = gen.get_name()
            email_base = name.lower().replace(" ", ".")
            cust = Customer(
                customer_id=uuid.uuid4(),
                customer_code=f"CUST{100000+i}",
                full_name=name,
                mobile_masked=f"XXXXXX{random.randint(1000, 9999)}",
                email_masked=f"{email_base}@masked.example",
                pan_hash=f"PANHASH{i:08d}",
                aadhaar_hash=f"AADHASH{i:08d}",
                address_hash=f"ADDRHASH{i:08d}",
                customer_category="Salaried" if i % 2 == 0 else "Self Employed",
                risk_segment="LOW" if i % 3 != 0 else "MEDIUM" if i % 5 != 0 else "HIGH",
                customer_vintage_months=random.randint(12, 120),
                branch_id=random.choice(branches).branch_id,
                agent_id=random.choice(agent_users).user_id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(200, 600)),
                mobile_raw=f"9123456{i:03d}",
                pan_number=f"ABCDE{random.randint(1000, 9999)}F",
                aadhaar_masked=f"XXXX-XXXX-{random.randint(1000, 9999)}",
                cibil_score=random.randint(650, 850),
                address=f"Street {i}, Main Road, Bengaluru - 560001"
            )
            db.add(cust)
            db.flush()
            customers.append(cust)
            
            # Create bank account
            cba = CustomerBankAccount(
                account_id=uuid.uuid4(),
                customer_id=cust.customer_id,
                bank_name="State Bank of India" if i % 2 == 0 else "HDFC Bank",
                account_number_hash=f"ACCHASH{i:08d}",
                account_last4=f"{random.randint(1000, 9999)}",
                ifsc_code="SBIN0000123" if i % 2 == 0 else "HDFC0000456",
                account_type="Savings",
                is_declared_repayment_account=True,
                is_mandate_account=True,
                verification_status="VERIFIED",
                valid_from=date.today() - timedelta(days=365)
            )
            db.add(cba)
        db.commit()

        # Step 9: Seed Loans and Allocations
        print("[SENTINEL] Seeding Loans and schedules...")
        loans = []
        products = ["Personal Loan", "Auto Loan", "Home Loan", "Business Loan", "MSME Loan"]
        for idx, cust in enumerate(customers):
            # 1 loan per customer
            loan = Loan(
                loan_id=uuid.uuid4(),
                lan=f"LAN{200000+idx}",
                customer_id=cust.customer_id,
                product_type=random.choice(products),
                loan_amount=random.randint(50000, 1000000),
                disbursement_date=date.today() - timedelta(days=random.randint(180, 360)),
                outstanding_amount=random.randint(10000, 800000),
                dpd=0 if idx % 3 != 0 else random.randint(31, 120), # Delinquency
                loan_status="ACTIVE",
                branch_id=cust.branch_id,
                dsa_id=random.choice(dsas).dsa_id,
                created_at=datetime.utcnow() - timedelta(days=365),
                loan_account_number=f"LAN{200000+idx}",
                sanctioned_amount=random.randint(50000, 1000000)
            )
            loan.emi_amount = float(loan.loan_amount) / 12
            loan.delinquency_bucket = "NPA" if loan.dpd > 90 else "SMA-2" if loan.dpd > 60 else "SMA-1" if loan.dpd > 30 else "ACTIVE"
            db.add(loan)
            db.flush()
            loans.append(loan)

            # Create loan allocation
            matching_agent = db.query(Agent).filter(Agent.branch_id == loan.branch_id).first() or agents_records[0]
            alloc = LoanAllocation(
                allocation_id=uuid.uuid4(),
                loan_id=loan.loan_id,
                agent_id=matching_agent.agent_id,
                agency_id=matching_agent.agency_id,
                branch_id=loan.branch_id,
                allocation_start_date=loan.disbursement_date + timedelta(days=30),
                allocation_status="ACTIVE"
            )
            db.add(alloc)

            # Repayment schedule (6 installments)
            for j in range(1, 7):
                sch = LoanRepaymentSchedule(
                    schedule_id=uuid.uuid4(),
                    loan_id=loan.loan_id,
                    installment_no=j,
                    due_date=loan.disbursement_date + timedelta(days=j * 30),
                    emi_amount=loan.emi_amount,
                    principal_amount=loan.emi_amount * 0.9,
                    interest_amount=loan.emi_amount * 0.1,
                    paid_amount=loan.emi_amount if j < 4 else 0.00,
                    status="PAID" if j < 4 else "OVERDUE" if loan.dpd > j*30 else "DUE"
                )
                db.add(sch)
        db.commit()

        # Step 10: Seed Payments (Span last 6 months for chart trends)
        print("[SENTINEL] Generating repayment records...")
        payments = []
        start_date = datetime.now() - timedelta(days=180)
        
        # We need a solid Total Collections sum (around 7 Crore or similar)
        # 12,000 repayments with random sums
        for i in range(12000):
            assoc_loan = random.choice(loans)
            # Find customer
            cust = db.query(Customer).filter(Customer.customer_id == assoc_loan.customer_id).first()
            
            p_date = start_date + timedelta(days=random.randint(1, 179), hours=random.randint(9, 18))
            amount = float(assoc_loan.emi_amount or 15000)
            
            pay = Payment(
                payment_id=uuid.uuid4(),
                transaction_ref=f"TXN{10000000+i}",
                loan_id=assoc_loan.loan_id,
                customer_id=assoc_loan.customer_id,
                payment_datetime=p_date,
                amount=amount,
                payment_mode=random.choice(["UPI", "CASH", "NEFT", "RTGS"]),
                source_account_hash=f"SRCHASH{random.randint(10000, 99999)}",
                source_account_last4=f"{random.randint(1000, 9999)}",
                destination_account_hash=f"DESTHASH{random.randint(10000, 99999)}",
                payment_channel=random.choice(["App", "Web", "Terminal"]),
                device_id=f"DEV-{random.randint(1000, 9999)}",
                latitude=20.5937 + random.uniform(-2.0, 2.0),
                longitude=78.9629 + random.uniform(-2.0, 2.0),
                is_declared_source=True if i % 10 != 0 else False,
                is_third_party=False if i % 12 != 0 else True,
                reversal_flag=False,
                created_at=p_date,
                agent_id=cust.agent_id if cust else random.choice(agent_users).user_id,
                status="SUCCESS",
                is_flagged=False
            )
            db.add(pay)
            db.flush()
            payments.append(pay)
        db.commit()

        # Step 11: Seed Targets and CollectionTargets
        print("[SENTINEL] Seeding targets...")
        current_month = datetime.now().strftime("%Y-%m")
        for ag_user in agent_users:
            collected = float(db.query(func.sum(Payment.amount)).filter(
                Payment.agent_id == ag_user.user_id
            ).scalar() or 0.00)
            
            target = Target(
                target_id=uuid.uuid4(),
                agent_id=ag_user.user_id,
                month=current_month,
                target_amount=250000.00,
                collected_amount=collected,
                target_date=date.today(),
                created_at=datetime.utcnow()
            )
            db.add(target)
            
            # Map collection targets mapping
            agent_rec = db.query(Agent).filter(Agent.mobile == ag_user.mobile).first()
            if agent_rec:
                col_target = CollectionTarget(
                    target_id=uuid.uuid4(),
                    agent_id=agent_rec.agent_id,
                    agency_id=agent_rec.agency_id,
                    branch_id=agent_rec.branch_id,
                    target_month=date.today().replace(day=1),
                    target_amount=250000.00,
                    achieved_amount=collected,
                    target_closure_date=date.today() + timedelta(days=10)
                )
                db.add(col_target)
        db.commit()

        # Step 12: Seed Fraud Rules, Risk Scores and Fraud Scores
        print("[SENTINEL] Populating agent risk models...")
        rule = FraudRule(
            rule_id=uuid.uuid4(),
            rule_code="RUL001",
            rule_name="Undeclared Source Payment",
            module="Collection",
            rule_type="Threshold",
            severity="HIGH",
            rule_expression={"field": "is_declared_source", "op": "eq", "value": False},
            is_active=True
        )
        db.add(rule)
        db.commit()

        agent_ids = [u.user_id for u in agent_users]
        high_risk_agents = random.sample(agent_ids, 15)
        top_dashboard_scores = [0.874, 0.792, 0.741, 0.655, 0.589]
        
        for idx, ag_id in enumerate(agent_ids):
            # Get a sample payment
            p = db.query(Payment).filter(Payment.agent_id == ag_id).first()
            if not p:
                continue
            
            score_val = 0.0
            if ag_id in high_risk_agents:
                hr_idx = high_risk_agents.index(ag_id)
                if hr_idx < 5:
                    score_val = top_dashboard_scores[hr_idx]
                else:
                    score_val = random.uniform(0.551, 0.580)
            else:
                score_val = random.uniform(0.04, 0.28)
                
            risk_level = "CRITICAL" if score_val > 0.75 else "HIGH" if score_val > 0.55 else "MEDIUM" if score_val > 0.30 else "LOW"
            
            # FraudScore (deprecated, queried in dashboard KPIs)
            fs = FraudScore(
                score_id=uuid.uuid4(),
                repayment_id=p.payment_id,
                agent_id=ag_id,
                customer_id=p.customer_id,
                spike_detection_score=score_val * 0.9,
                source_mismatch_score=score_val * 0.8,
                third_party_score=score_val * 0.75,
                collusion_score=score_val * 0.85,
                behavior_anomaly_score=score_val * 0.7,
                risk_scoring_score=score_val,
                cibil_monitor_score=0.1,
                case_mgmt_score=score_val * 0.95,
                composite_score=score_val,
                risk_level=risk_level,
                explanation={
                    "SRC_MISMATCH": f"Payment from undeclared source account. Risk: {score_val*100:.1f}%",
                    "COMMON_ACCOUNT": f"Funder account linked to multiple customers.",
                    "LOGIN_ANOMALY": f"Login geolocation mismatch from usual agent coordinates."
                },
                workflow_trace=["SpikeDetectionAgent", "SourceMismatchAgent", "ThirdPartyAgent", "RiskScoringAgent"]
            )
            db.add(fs)

            # RiskScore (aligned table)
            rs = RiskScore(
                risk_score_id=uuid.uuid4(),
                entity_type="AGENT",
                entity_id=ag_id,
                score=score_val * 100,
                risk_level=risk_level,
                reason_codes=["SRC_MISMATCH", "COMMON_ACCOUNT", "LOGIN_ANOMALY"],
                model_version="v3.0",
                calculated_at=datetime.utcnow()
            )
            db.add(rs)
        db.commit()

        # Step 13: Seed Cases & Fraud Alerts (Create exactly 1527 open cases for KPIs)
        print("[SENTINEL] Seeding 1,527 active fraud investigation cases...")
        
        # Create a single rule ID fallback if needed
        rule_id = rule.rule_id
        
        # Batch inserting cases for speed
        bulk_cases = []
        bulk_alerts = []
        
        # Use agents and customers lists
        for i in range(1527):
            ag_user = random.choice(agent_users)
            cust = random.choice(customers)
            loan = db.query(Loan).filter(Loan.customer_id == cust.customer_id).first() or loans[0]
            
            alert_id = uuid.uuid4()
            case_id = uuid.uuid4()
            
            p_ref = f"TXN{10000000+random.randint(1, 11000)}"
            score_val = random.uniform(0.56, 0.95)
            
            # Create alert
            alert = FraudAlert(
                alert_id=alert_id,
                alert_code=f"ALT{100000+i}",
                rule_id=rule_id,
                entity_type="AGENT",
                entity_id=ag_user.user_id,
                entity_name=ag_user.username.replace(".", " ").title(),
                loan_id=loan.loan_id,
                customer_id=cust.customer_id,
                alert_type=random.choice(["Undeclared Repayment Account", "Spike in Collection Volume", "Third Party Geolocation Anomaly"]),
                severity="CRITICAL" if score_val > 0.75 else "HIGH",
                risk_score=score_val,
                alert_status="OPEN" if i < 1520 else "ASSIGNED",
                explanation=f"Agent parsed payment under non-repayment source account: {p_ref}.",
                evidence_json={"transaction_ref": p_ref, "risk": score_val},
                generated_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                is_read=False,
                is_actioned=False,
                message=f"Fraud alert raised for Agent {ag_user.username}"
            )
            bulk_alerts.append(alert)

            # Create case
            status = "OPEN" if i < 1400 else "INVESTIGATING"
            case = Case(
                case_id=case_id,
                case_number=f"CAS-{2026:04d}-{100000+i}",
                alert_id=alert_id,
                case_type=alert.alert_type,
                severity=alert.severity,
                case_status=status,
                assigned_to=random.choice([u.user_id for u in users if u.role == "manager"]),
                assigned_by=seeded_users[0].user_id,
                branch_id=cust.branch_id,
                sla_due_at=datetime.utcnow() + timedelta(days=3),
                created_at=alert.generated_at,
                composite_score=score_val,
                ai_reasoning=f"AI reasoning traces high probability collusion index: {score_val*100:.1f}%. Source payment mismatch linked to multiple accounts.",
                agent_id=ag_user.user_id,
                customer_id=cust.customer_id
            )
            bulk_cases.append(case)

        # Ingest in chunks
        print("  Saving fraud alerts...")
        db.bulk_save_objects(bulk_alerts)
        db.flush()
        print("  Saving cases...")
        db.bulk_save_objects(bulk_cases)
        db.flush()
        db.commit()
        
        # Add some resolved cases to show cleared stats
        cleared_cases = []
        cleared_alerts = []
        for i in range(150):
            ag_user = random.choice(agent_users)
            cust = random.choice(customers)
            loan = loans[0]
            alert_id = uuid.uuid4()
            case_id = uuid.uuid4()
            
            alert = FraudAlert(
                alert_id=alert_id,
                alert_code=f"ALT-CLR-{i}",
                rule_id=rule_id,
                entity_type="AGENT",
                entity_id=ag_user.user_id,
                entity_name=ag_user.username.replace(".", " ").title(),
                loan_id=loan.loan_id,
                customer_id=cust.customer_id,
                alert_type="Cleared Repayment",
                severity="LOW",
                risk_score=0.15,
                alert_status="CLOSED",
                generated_at=datetime.utcnow() - timedelta(days=random.randint(10, 40)),
                is_read=True,
                is_actioned=True
            )
            cleared_alerts.append(alert)
            
            case = Case(
                case_id=case_id,
                case_number=f"CAS-{2026:04d}-CLR-{i}",
                alert_id=alert_id,
                case_type=alert.alert_type,
                severity=alert.severity,
                case_status="CLEARED",
                assigned_to=random.choice([u.user_id for u in users if u.role == "manager"]),
                assigned_by=seeded_users[0].user_id,
                branch_id=cust.branch_id,
                created_at=alert.generated_at,
                composite_score=0.15,
                closed_at=datetime.utcnow() - timedelta(days=2),
                closure_status="RESOLVED_GENUINE",
                closure_remarks="Verified borrower paid via cousin account under genuine medical emergency.",
                agent_id=ag_user.user_id,
                customer_id=cust.customer_id
            )
            cleared_cases.append(case)
            
        db.bulk_save_objects(cleared_alerts)
        db.bulk_save_objects(cleared_cases)
        db.commit()
        print("[SENTINEL] Cases database seeding complete.")

        # Step 14: Funding source clusters and other anomalies
        print("[SENTINEL] Populating cluster relationships...")
        for i in range(10):
            acc = f"ACC{random.randint(10000000, 99999999)}"
            cluster = FundingSourceCluster(
                cluster_id=uuid.uuid4(),
                source_account_hash=acc,
                customer_count=5,
                loan_count=5,
                total_amount=150000.00,
                first_seen_at=datetime.utcnow() - timedelta(days=30),
                last_seen_at=datetime.utcnow(),
                risk_level="HIGH"
            )
            db.add(cluster)
            db.flush()
            
            # Map members
            for m in range(5):
                cust = customers[random.randint(0, 1999)]
                loan = db.query(Loan).filter(Loan.customer_id == cust.customer_id).first() or loans[0]
                payment = db.query(Payment).filter(Payment.loan_id == loan.loan_id).first() or payments[0]
                
                member = FundingSourceClusterMember(
                    member_id=uuid.uuid4(),
                    cluster_id=cluster.cluster_id,
                    customer_id=cust.customer_id,
                    loan_id=loan.loan_id,
                    payment_id=payment.payment_id
                )
                db.add(member)
        db.commit()

        # Step 15: Sync Graph Database (Neo4j)
        print("[SENTINEL] Checking Neo4j connection for relationship sync...")
        from app.config import settings
        if settings.NEO4J_ENABLED:
            try:
                from app.services.graph_db import GraphDBService
                gs = GraphDBService(db)
                if gs.using_neo4j:
                    print("[SENTINEL] Graph database connection verified, syncing relationship graphs...")
                    gs.sync_sample_graph(limit=2000)
                    print("[SENTINEL] Neo4j graph relationships synced successfully.")
                else:
                    print("[WARN] Neo4j is enabled but driver connectivity failed. Skipping graph sync.")
            except Exception as ge:
                print(f"[WARN] Neo4j graph sync failed: {ge}")
        else:
            print("[SENTINEL] Neo4j is disabled (NEO4J_ENABLED=False). Falling back to SQL relational metrics.")

        print("[SENTINEL] Programmatic database cleaning, seeding, and alignment successfully completed!")

    except Exception as e:
        db.rollback()
        raw_conn.rollback()
        print(f"[ERROR] Seeding process encountered a failure: {e}")
        raise
    finally:
        db.close()
        raw_conn.close()

if __name__ == "__main__":
    clean_and_populate()
