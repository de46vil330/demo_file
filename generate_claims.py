"""
Generates 100 sample CMS-1500 claims and writes them to claims_dataset.csv
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

# ── Reference data ─────────────────────────────────────────────────────────────

INSURANCE_TYPES = ["Medicare", "Medicaid", "TRICARE", "Group Health Plan", "Other"]

PLACE_OF_SERVICE = {
    "11": "Office",
    "21": "Inpatient Hospital",
    "22": "Outpatient Hospital",
    "23": "Emergency Room",
    "31": "Skilled Nursing Facility",
}

CPT_CODES = {
    "99213": ("Office visit, established, low complexity",      150.00),
    "99214": ("Office visit, established, moderate complexity", 210.00),
    "99215": ("Office visit, established, high complexity",     280.00),
    "99203": ("Office visit, new patient, low complexity",      175.00),
    "99204": ("Office visit, new patient, moderate complexity", 245.00),
    "93000": ("ECG with interpretation",                        95.00),
    "85027": ("Complete blood count (CBC)",                     45.00),
    "80053": ("Comprehensive metabolic panel",                  55.00),
    "71046": ("Chest X-ray, 2 views",                          110.00),
    "36415": ("Routine venipuncture",                           25.00),
}

ICD10_CODES = [
    "Z00.00",   # General adult medical exam
    "I10",      # Essential hypertension
    "E11.9",    # Type 2 diabetes, uncomplicated
    "J06.9",    # Acute upper respiratory infection
    "M54.5",    # Low back pain
    "F41.1",    # Generalized anxiety disorder
    "E78.5",    # Hyperlipidemia
    "J18.9",    # Pneumonia, unspecified
    "N39.0",    # Urinary tract infection
    "K21.0",    # GERD with esophagitis
]

STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
          "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
          "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
          "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
          "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def rand_date(start_year=2023, end_year=2024):
    start = datetime(start_year, 1, 1)
    end   = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def fmt_date(dt):
    return dt.strftime("%m/%d/%Y")

def rand_npi():
    return str(random.randint(1000000000, 9999999999))

def rand_id(prefix="", length=10):
    return prefix + "".join([str(random.randint(0, 9)) for _ in range(length)])

# ── Generator ──────────────────────────────────────────────────────────────────

def generate_claim(claim_id):
    # Patient
    sex            = random.choice(["M", "F"])
    first          = fake.first_name_male() if sex == "M" else fake.first_name_female()
    last           = fake.last_name()
    dob            = rand_date(1940, 2005)
    patient_name   = f"{last}, {first}"
    patient_addr   = fake.street_address()
    patient_city   = fake.city()
    patient_state  = random.choice(STATES)
    patient_zip    = fake.zipcode()
    patient_phone  = fake.numerify("(###) ###-####")

    # Insurance
    ins_type       = random.choice(INSURANCE_TYPES)
    ins_id         = rand_id("INS", 9)
    group_number   = rand_id("GRP", 7)
    plan_name      = fake.company() + " Health Plan"
    relationship   = random.choice(["Self", "Spouse", "Child", "Other"])

    # Insured (may differ from patient)
    if relationship == "Self":
        insured_name = patient_name
        insured_dob  = dob
        insured_sex  = sex
    else:
        insured_sex  = random.choice(["M", "F"])
        insured_fn   = fake.first_name_male() if insured_sex == "M" else fake.first_name_female()
        insured_ln   = last
        insured_name = f"{insured_ln}, {insured_fn}"
        insured_dob  = rand_date(1950, 1985)

    # Condition
    related_employment = random.choice(["Yes", "No"])
    related_auto       = "Yes" if random.random() < 0.05 else "No"
    related_other      = "Yes" if random.random() < 0.03 else "No"

    # Dates of service
    dos_from   = rand_date(2023, 2024)
    dos_to     = dos_from + timedelta(days=random.randint(0, 1))

    # Referring provider
    ref_first  = fake.first_name()
    ref_last   = fake.last_name()
    ref_npi    = rand_npi()

    # Service line
    cpt_code   = random.choice(list(CPT_CODES.keys()))
    cpt_desc, charge = CPT_CODES[cpt_code]
    modifier   = random.choice(["", "25", "59", "GT", ""])
    pos_code   = random.choice(list(PLACE_OF_SERVICE.keys()))
    units      = random.randint(1, 3)
    total_charge = round(charge * units, 2)

    # Diagnosis
    diag1      = random.choice(ICD10_CODES)
    diag2      = random.choice([c for c in ICD10_CODES if c != diag1]) if random.random() > 0.4 else ""

    # Prior auth
    prior_auth = rand_id("PA", 8) if random.random() > 0.6 else ""

    # Billing / rendering provider
    billing_name  = fake.company() + " Medical Group"
    billing_addr  = fake.street_address()
    billing_city  = fake.city()
    billing_state = random.choice(STATES)
    billing_zip   = fake.zipcode()
    billing_phone = fake.numerify("(###) ###-####")
    billing_npi   = rand_npi()
    billing_ein   = fake.numerify("##-#######")

    rendering_fn  = fake.first_name()
    rendering_ln  = fake.last_name()
    rendering_npi = rand_npi()

    # Financials
    amount_paid   = round(total_charge * random.uniform(0, 0.8), 2)
    accept_assign = random.choice(["Yes", "No"])

    return {
        # Box 1
        "box01_insurance_type":         ins_type,
        # Box 1a
        "box01a_insured_id":            ins_id,
        # Box 2
        "box02_patient_name":           patient_name,
        # Box 3
        "box03_patient_dob":            fmt_date(dob),
        "box03_patient_sex":            sex,
        # Box 4
        "box04_insured_name":           insured_name,
        # Box 5
        "box05_patient_address":        patient_addr,
        "box05_patient_city":           patient_city,
        "box05_patient_state":          patient_state,
        "box05_patient_zip":            patient_zip,
        "box05_patient_phone":          patient_phone,
        # Box 6
        "box06_patient_relationship":   relationship,
        # Box 9d
        "box09d_insurance_plan_name":   plan_name,
        # Box 10
        "box10a_related_employment":    related_employment,
        "box10b_related_auto":          related_auto,
        "box10c_related_other":         related_other,
        # Box 11
        "box11_group_number":           group_number,
        "box11a_insured_dob":           fmt_date(insured_dob),
        "box11a_insured_sex":           insured_sex,
        "box11c_insurance_plan_name":   plan_name,
        # Box 14
        "box14_date_of_illness":        fmt_date(dos_from),
        # Box 17
        "box17_referring_provider":     f"{ref_last}, {ref_first}",
        "box17b_referring_npi":         ref_npi,
        # Box 21 – Diagnoses
        "box21_diag1_icd10":            diag1,
        "box21_diag2_icd10":            diag2,
        # Box 23
        "box23_prior_auth":             prior_auth,
        # Box 24 – Service line
        "box24a_dos_from":              fmt_date(dos_from),
        "box24a_dos_to":                fmt_date(dos_to),
        "box24b_place_of_service":      pos_code,
        "box24d_cpt_code":              cpt_code,
        "box24d_modifier":              modifier,
        "box24d_cpt_description":       cpt_desc,
        "box24e_diag_pointer":          "1",
        "box24f_charge":                f"{charge:.2f}",
        "box24g_units":                 units,
        # Box 25
        "box25_federal_tax_id":         billing_ein,
        # Box 26
        "box26_patient_account_no":     f"ACCT-{claim_id:05d}",
        # Box 27
        "box27_accept_assignment":      accept_assign,
        # Box 28
        "box28_total_charge":           f"{total_charge:.2f}",
        # Box 29
        "box29_amount_paid":            f"{amount_paid:.2f}",
        # Box 31
        "box31_rendering_provider":     f"{rendering_ln}, {rendering_fn}",
        "box31_rendering_npi":          rendering_npi,
        # Box 32 – Service facility
        "box32_facility_name":          billing_name,
        "box32_facility_address":       billing_addr,
        "box32_facility_city":          billing_city,
        "box32_facility_state":         billing_state,
        "box32_facility_zip":           billing_zip,
        "box32a_facility_npi":          billing_npi,
        # Box 33 – Billing provider
        "box33_billing_name":           billing_name,
        "box33_billing_phone":          billing_phone,
        "box33_billing_address":        billing_addr,
        "box33_billing_city":           billing_city,
        "box33_billing_state":          billing_state,
        "box33_billing_zip":            billing_zip,
        "box33a_billing_npi":           billing_npi,
    }


def main():
    claims = [generate_claim(i + 1) for i in range(100)]
    output_file = "claims_dataset.csv"

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=claims[0].keys())
        writer.writeheader()
        writer.writerows(claims)

    print(f"Generated {len(claims)} claims -> {output_file}")


if __name__ == "__main__":
    main()
