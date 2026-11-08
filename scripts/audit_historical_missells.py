import csv
import json
from pathlib import Path

# Load product rules
products = {}
with open('data/product_catalogue.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        pid = r['product_id']
        tiers = [int(t.strip()) for t in r['available_city_tiers'].split(';') if t.strip()]
        min_emp = int(r['min_employees']) if r['min_employees'] else 0
        min_sites = int(r['min_sites']) if r['min_sites'] else 1
        req_gst = r['requires_gstin'].strip().upper() == 'Y'
        req_one_of = [x.strip() for x in r['requires_one_of'].split('|') if x.strip()] if r['requires_one_of'] else []
        products[pid] = {
            'tiers': tiers,
            'min_emp': min_emp,
            'min_sites': min_sites,
            'requires_gst': req_gst,
            'requires_one_of': req_one_of,
        }

total_activated = 0
violations = {
    'BELOW_MIN_EMPLOYEES': 0,
    'TIER_UNAVAILABLE': 0,
    'NEEDS_ACTIVE_GSTIN': 0,
    'MISSING_DEPENDENCY': 0,
}
violated_leads = []

with open('data/smb_leads.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['stage_reached'] != 'Activated' or not r['bundle_products']:
            continue
        total_activated += 1
        lead_id = r['lead_id']
        tier = int(r['city_tier'])
        emp = int(r['employee_count']) if r['employee_count'] else 1
        has_gst = r['has_gstin'].strip().lower() == 'true'
        
        # Parse bundle e.g. P01x1;P07x2
        items = []
        for part in r['bundle_products'].split(';'):
            part = part.strip()
            if not part:
                continue
            pid = part.split('x')[0].strip()
            items.append(pid)
        
        lead_violated = False
        # Check rule 1: tier
        for pid in items:
            p = products.get(pid)
            if not p:
                continue
            if tier not in p['tiers']:
                violations['TIER_UNAVAILABLE'] += 1
                lead_violated = True
            if emp < p['min_emp']:
                violations['BELOW_MIN_EMPLOYEES'] += 1
                lead_violated = True
            if p['requires_gst'] and not has_gst:
                violations['NEEDS_ACTIVE_GSTIN'] += 1
                lead_violated = True
            if p['requires_one_of']:
                if not any(req_pid in items for req_pid in p['requires_one_of']):
                    violations['MISSING_DEPENDENCY'] += 1
                    lead_violated = True
        if lead_violated:
            violated_leads.append(lead_id)

print(f"Total Activated Leads: {total_activated}")
print(f"Total Unique Mis-Sold Leads: {len(set(violated_leads))} ({len(set(violated_leads))/total_activated*100:.1f}%)")
print("Violations breakdown:")
for k, v in violations.items():
    print(f"  {k}: {v}")
