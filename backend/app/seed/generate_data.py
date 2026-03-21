"""Generate realistic sample healthcare pricing data."""

import random
from datetime import date

HOSPITALS = [
    {"name": "Memorial General Hospital", "city": "Los Angeles", "state": "CA", "zip_code": "90012", "lat": 34.06, "lon": -118.24, "ein": "95-1234567"},
    {"name": "Pacific Medical Center", "city": "San Francisco", "state": "CA", "zip_code": "94102", "lat": 37.78, "lon": -122.42, "ein": "94-2345678"},
    {"name": "Cedar Valley Hospital", "city": "San Diego", "state": "CA", "zip_code": "92101", "lat": 32.72, "lon": -117.16, "ein": "95-3456789"},
    {"name": "Lone Star Medical Center", "city": "Houston", "state": "TX", "zip_code": "77001", "lat": 29.76, "lon": -95.37, "ein": "74-4567890"},
    {"name": "Dallas Regional Hospital", "city": "Dallas", "state": "TX", "zip_code": "75201", "lat": 32.78, "lon": -96.80, "ein": "75-5678901"},
    {"name": "Austin Community Hospital", "city": "Austin", "state": "TX", "zip_code": "78701", "lat": 30.27, "lon": -97.74, "ein": "74-6789012"},
    {"name": "Empire State Medical Center", "city": "New York", "state": "NY", "zip_code": "10001", "lat": 40.75, "lon": -73.99, "ein": "13-7890123"},
    {"name": "Hudson Valley Hospital", "city": "Albany", "state": "NY", "zip_code": "12207", "lat": 42.65, "lon": -73.76, "ein": "14-8901234"},
    {"name": "Brooklyn Community Health", "city": "Brooklyn", "state": "NY", "zip_code": "11201", "lat": 40.69, "lon": -73.99, "ein": "11-9012345"},
    {"name": "Sunshine Regional Medical", "city": "Miami", "state": "FL", "zip_code": "33101", "lat": 25.77, "lon": -80.19, "ein": "59-0123456"},
    {"name": "Tampa Bay Hospital", "city": "Tampa", "state": "FL", "zip_code": "33602", "lat": 27.95, "lon": -82.46, "ein": "59-1234560"},
    {"name": "Orlando Health Center", "city": "Orlando", "state": "FL", "zip_code": "32801", "lat": 28.54, "lon": -81.38, "ein": "59-2345670"},
    {"name": "Lakeside Medical Center", "city": "Chicago", "state": "IL", "zip_code": "60601", "lat": 41.88, "lon": -87.63, "ein": "36-3456780"},
    {"name": "Prairie View Hospital", "city": "Springfield", "state": "IL", "zip_code": "62701", "lat": 39.78, "lon": -89.65, "ein": "37-4567890"},
    {"name": "Midwest Regional Health", "city": "Naperville", "state": "IL", "zip_code": "60540", "lat": 41.79, "lon": -88.15, "ein": "36-5678900"},
]

PROCEDURES = [
    # Imaging
    {"code": "70553", "type": "CPT", "desc": "Magnetic resonance imaging brain with and without contrast", "name": "Brain MRI with Contrast", "cat": "Imaging", "base_min": 1200, "base_max": 4500},
    {"code": "74177", "type": "CPT", "desc": "CT abdomen and pelvis with contrast", "name": "CT Scan - Abdomen", "cat": "Imaging", "base_min": 800, "base_max": 3500},
    {"code": "71046", "type": "CPT", "desc": "Radiologic examination chest 2 views", "name": "Chest X-Ray (2 views)", "cat": "Imaging", "base_min": 100, "base_max": 600},
    {"code": "76856", "type": "CPT", "desc": "Ultrasound pelvic nonobstetric complete", "name": "Pelvic Ultrasound", "cat": "Imaging", "base_min": 300, "base_max": 1200},
    {"code": "73721", "type": "CPT", "desc": "MRI joint of lower extremity without contrast", "name": "Knee MRI", "cat": "Imaging", "base_min": 1000, "base_max": 3800},
    {"code": "77067", "type": "CPT", "desc": "Screening mammography bilateral", "name": "Mammogram (Screening)", "cat": "Imaging", "base_min": 200, "base_max": 800},
    {"code": "70551", "type": "CPT", "desc": "MRI brain without contrast", "name": "Brain MRI without Contrast", "cat": "Imaging", "base_min": 900, "base_max": 3500},
    {"code": "72148", "type": "CPT", "desc": "MRI lumbar spine without contrast", "name": "Lower Back MRI", "cat": "Imaging", "base_min": 1000, "base_max": 3800},
    # Lab
    {"code": "85025", "type": "CPT", "desc": "Complete blood count with differential", "name": "Complete Blood Count (CBC)", "cat": "Lab", "base_min": 15, "base_max": 150},
    {"code": "80053", "type": "CPT", "desc": "Comprehensive metabolic panel", "name": "Comprehensive Metabolic Panel", "cat": "Lab", "base_min": 20, "base_max": 200},
    {"code": "80061", "type": "CPT", "desc": "Lipid panel", "name": "Cholesterol / Lipid Panel", "cat": "Lab", "base_min": 25, "base_max": 250},
    {"code": "81001", "type": "CPT", "desc": "Urinalysis with microscopy", "name": "Urinalysis", "cat": "Lab", "base_min": 10, "base_max": 100},
    {"code": "84443", "type": "CPT", "desc": "Thyroid stimulating hormone", "name": "Thyroid Test (TSH)", "cat": "Lab", "base_min": 20, "base_max": 200},
    {"code": "83036", "type": "CPT", "desc": "Hemoglobin A1c", "name": "A1C (Diabetes Test)", "cat": "Lab", "base_min": 20, "base_max": 180},
    {"code": "87804", "type": "CPT", "desc": "Infectious agent detection influenza", "name": "Flu Test", "cat": "Lab", "base_min": 25, "base_max": 200},
    {"code": "87635", "type": "CPT", "desc": "SARS-CoV-2 COVID-19 amplified probe", "name": "COVID-19 Test (PCR)", "cat": "Lab", "base_min": 50, "base_max": 300},
    # Surgery
    {"code": "27447", "type": "CPT", "desc": "Total knee replacement arthroplasty", "name": "Total Knee Replacement", "cat": "Surgery", "base_min": 20000, "base_max": 65000},
    {"code": "44970", "type": "CPT", "desc": "Laparoscopic appendectomy", "name": "Appendectomy (Laparoscopic)", "cat": "Surgery", "base_min": 8000, "base_max": 35000},
    {"code": "66984", "type": "CPT", "desc": "Cataract surgery with lens insertion", "name": "Cataract Surgery", "cat": "Surgery", "base_min": 3000, "base_max": 12000},
    {"code": "47562", "type": "CPT", "desc": "Laparoscopic cholecystectomy", "name": "Gallbladder Removal", "cat": "Surgery", "base_min": 8000, "base_max": 30000},
    {"code": "49505", "type": "CPT", "desc": "Inguinal hernia repair", "name": "Hernia Repair", "cat": "Surgery", "base_min": 5000, "base_max": 20000},
    {"code": "27130", "type": "CPT", "desc": "Total hip replacement arthroplasty", "name": "Total Hip Replacement", "cat": "Surgery", "base_min": 22000, "base_max": 70000},
    # ER
    {"code": "99283", "type": "CPT", "desc": "Emergency department visit moderate severity", "name": "ER Visit - Moderate", "cat": "Emergency", "base_min": 500, "base_max": 2500},
    {"code": "99285", "type": "CPT", "desc": "Emergency department visit high severity", "name": "ER Visit - Severe", "cat": "Emergency", "base_min": 1500, "base_max": 6000},
    {"code": "99284", "type": "CPT", "desc": "Emergency department visit moderately high severity", "name": "ER Visit - Moderately Severe", "cat": "Emergency", "base_min": 800, "base_max": 4000},
    # Preventive
    {"code": "45378", "type": "CPT", "desc": "Colonoscopy diagnostic", "name": "Colonoscopy (Diagnostic)", "cat": "Preventive", "base_min": 1500, "base_max": 5000},
    {"code": "45380", "type": "CPT", "desc": "Colonoscopy with biopsy", "name": "Colonoscopy with Biopsy", "cat": "Preventive", "base_min": 2000, "base_max": 6500},
    {"code": "99395", "type": "CPT", "desc": "Preventive visit established patient 18-39", "name": "Annual Physical (18-39)", "cat": "Preventive", "base_min": 150, "base_max": 500},
    {"code": "99396", "type": "CPT", "desc": "Preventive visit established patient 40-64", "name": "Annual Physical (40-64)", "cat": "Preventive", "base_min": 200, "base_max": 600},
    # Office Visits
    {"code": "99213", "type": "CPT", "desc": "Office visit established patient low complexity", "name": "Doctor Visit - Basic", "cat": "Office Visit", "base_min": 100, "base_max": 350},
    {"code": "99214", "type": "CPT", "desc": "Office visit established patient moderate complexity", "name": "Doctor Visit - Moderate", "cat": "Office Visit", "base_min": 150, "base_max": 500},
    {"code": "99215", "type": "CPT", "desc": "Office visit established patient high complexity", "name": "Doctor Visit - Complex", "cat": "Office Visit", "base_min": 250, "base_max": 700},
    {"code": "99203", "type": "CPT", "desc": "New patient office visit low complexity", "name": "New Patient Visit - Basic", "cat": "Office Visit", "base_min": 150, "base_max": 450},
    {"code": "99205", "type": "CPT", "desc": "New patient office visit high complexity", "name": "New Patient Visit - Complex", "cat": "Office Visit", "base_min": 300, "base_max": 800},
    # Therapy / Rehab
    {"code": "97110", "type": "CPT", "desc": "Therapeutic exercises 15 min", "name": "Physical Therapy Session", "cat": "Therapy", "base_min": 50, "base_max": 250},
    {"code": "90837", "type": "CPT", "desc": "Psychotherapy 60 minutes", "name": "Therapy Session (60 min)", "cat": "Therapy", "base_min": 100, "base_max": 350},
    # Maternity
    {"code": "59400", "type": "CPT", "desc": "Routine obstetric care vaginal delivery", "name": "Vaginal Delivery (Total Care)", "cat": "Maternity", "base_min": 5000, "base_max": 18000},
    {"code": "59510", "type": "CPT", "desc": "Routine obstetric care cesarean delivery", "name": "C-Section (Total Care)", "cat": "Maternity", "base_min": 8000, "base_max": 28000},
    # Cardiac
    {"code": "93000", "type": "CPT", "desc": "Electrocardiogram complete", "name": "EKG / ECG", "cat": "Cardiac", "base_min": 50, "base_max": 400},
    {"code": "93306", "type": "CPT", "desc": "Echocardiography transthoracic complete", "name": "Echocardiogram", "cat": "Cardiac", "base_min": 400, "base_max": 2500},
    # Dental (hospital-based)
    {"code": "D7140", "type": "CDT", "desc": "Extraction erupted tooth", "name": "Tooth Extraction", "cat": "Dental", "base_min": 100, "base_max": 500},
    # Dermatology
    {"code": "11102", "type": "CPT", "desc": "Tangential biopsy of skin single lesion", "name": "Skin Biopsy", "cat": "Dermatology", "base_min": 150, "base_max": 600},
    # Sleep
    {"code": "95810", "type": "CPT", "desc": "Polysomnography sleep study", "name": "Sleep Study", "cat": "Sleep Medicine", "base_min": 1000, "base_max": 5000},
    # Allergy
    {"code": "95004", "type": "CPT", "desc": "Percutaneous allergy skin tests", "name": "Allergy Skin Test", "cat": "Allergy", "base_min": 60, "base_max": 400},
    # Endoscopy
    {"code": "43239", "type": "CPT", "desc": "Upper GI endoscopy with biopsy", "name": "Upper Endoscopy with Biopsy", "cat": "Gastroenterology", "base_min": 1500, "base_max": 5500},
    # Urology
    {"code": "52000", "type": "CPT", "desc": "Cystourethroscopy", "name": "Bladder Scope (Cystoscopy)", "cat": "Urology", "base_min": 800, "base_max": 3500},
    # Neurology
    {"code": "95819", "type": "CPT", "desc": "Electroencephalogram with sleep", "name": "EEG (Brain Wave Test)", "cat": "Neurology", "base_min": 400, "base_max": 2000},
    # Pulmonary
    {"code": "94010", "type": "CPT", "desc": "Spirometry", "name": "Breathing Test (Spirometry)", "cat": "Pulmonary", "base_min": 50, "base_max": 400},
    # Infusion
    {"code": "96413", "type": "CPT", "desc": "Chemotherapy IV infusion first hour", "name": "Chemotherapy Infusion (1st hour)", "cat": "Oncology", "base_min": 500, "base_max": 5000},
]

PAYERS = [
    {"name": "Blue Cross Blue Shield", "plans": ["PPO", "HMO", "High Deductible"]},
    {"name": "Aetna", "plans": ["PPO", "HMO"]},
    {"name": "UnitedHealthcare", "plans": ["Choice Plus PPO", "Navigate HMO", "HDHP"]},
    {"name": "Cigna", "plans": ["Open Access Plus", "LocalPlus"]},
    {"name": "Humana", "plans": ["Gold Plus HMO", "PPO"]},
    {"name": "Kaiser Permanente", "plans": ["HMO"]},
]

# States with higher cost of living get a price multiplier
STATE_MULTIPLIER = {
    "CA": 1.30,
    "NY": 1.35,
    "IL": 1.10,
    "TX": 0.95,
    "FL": 0.90,
}


def generate_hospitals():
    results = []
    for h in HOSPITALS:
        results.append({
            "name": h["name"],
            "ein": h["ein"],
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Elm', 'Medical Center', 'University', 'Park'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
            "city": h["city"],
            "state": h["state"],
            "zip_code": h["zip_code"],
            "latitude": h["lat"],
            "longitude": h["lon"],
            "last_updated": date(2025, random.randint(1, 12), random.randint(1, 28)),
        })
    return results


def generate_procedures():
    results = []
    for p in PROCEDURES:
        results.append({
            "billing_code": p["code"],
            "code_type": p["type"],
            "description": p["desc"],
            "plain_language_name": p["name"],
            "category": p["cat"],
        })
    return results


def generate_payers():
    results = []
    for p in PAYERS:
        for plan in p["plans"]:
            results.append({"name": p["name"], "plan_name": plan})
    return results


def generate_prices(hospitals, procedures, payers):
    random.seed(42)
    results = []
    for h_idx, hospital in enumerate(hospitals):
        state = HOSPITALS[h_idx]["state"]
        multiplier = STATE_MULTIPLIER.get(state, 1.0)
        # Add per-hospital variation
        hospital_factor = random.uniform(0.85, 1.15)

        for p_idx, procedure in enumerate(procedures):
            proc_info = PROCEDURES[p_idx]
            base = random.uniform(proc_info["base_min"], proc_info["base_max"])
            gross = round(base * multiplier * hospital_factor, 2)
            cash = round(gross * random.uniform(0.35, 0.65), 2)

            payer_rates = []
            for pay_idx, payer in enumerate(payers):
                rate = round(gross * random.uniform(0.25, 0.55), 2)
                payer_rates.append(rate)
                results.append({
                    "hospital_idx": h_idx,
                    "procedure_idx": p_idx,
                    "payer_idx": pay_idx,
                    "gross_charge": gross,
                    "discounted_cash_price": cash,
                    "negotiated_rate": rate,
                    "min_negotiated_rate": None,  # filled below
                    "max_negotiated_rate": None,
                })

            # Set min/max across payers for this hospital-procedure pair
            min_rate = min(payer_rates)
            max_rate = max(payer_rates)
            for r in results[-(len(payers)):]:
                r["min_negotiated_rate"] = min_rate
                r["max_negotiated_rate"] = max_rate

            # Cash price row (no payer)
            results.append({
                "hospital_idx": h_idx,
                "procedure_idx": p_idx,
                "payer_idx": None,
                "gross_charge": gross,
                "discounted_cash_price": cash,
                "negotiated_rate": None,
                "min_negotiated_rate": min_rate,
                "max_negotiated_rate": max_rate,
            })

    return results
