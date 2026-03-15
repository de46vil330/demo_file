"""
Reads dat/claims_dataset.csv and generates dat/claims_report.html
with an interactive table, summary cards, and charts.
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT  = Path("dat/claims_dataset.csv")
OUTPUT = Path("dat/claims_report.html")


def load_claims():
    with open(INPUT, newline="") as f:
        return list(csv.DictReader(f))


def build_summary(claims):
    total_billed  = sum(float(c["box28_total_charge"]) for c in claims)
    total_paid    = sum(float(c["box29_amount_paid"])   for c in claims)
    ins_counts    = Counter(c["box01_insurance_type"]   for c in claims)
    pos_map = {"11":"Office","21":"Inpatient Hospital","22":"Outpatient Hospital",
               "23":"Emergency Room","31":"Skilled Nursing Facility"}
    pos_counts    = Counter(pos_map.get(c["box24b_place_of_service"], c["box24b_place_of_service"])
                            for c in claims)
    cpt_counts    = Counter((c["box24d_cpt_code"], c["box24d_cpt_description"]) for c in claims)
    diag_counts   = Counter(c["box21_diag1_icd10"]      for c in claims)
    state_counts  = Counter(c["box05_patient_state"]    for c in claims)

    return {
        "total_claims":  len(claims),
        "total_billed":  total_billed,
        "total_paid":    total_paid,
        "avg_charge":    total_billed / len(claims),
        "ins_counts":    dict(ins_counts.most_common()),
        "pos_counts":    dict(pos_counts.most_common()),
        "cpt_counts":    {f"{code} – {desc}": cnt for (code, desc), cnt in cpt_counts.most_common(10)},
        "diag_counts":   dict(diag_counts.most_common(10)),
        "state_counts":  dict(state_counts.most_common(10)),
        "rel_hierarchy": build_hierarchy(claims),
    }


def build_hierarchy(claims):
    """Relationship → Insurance Type → [claim summaries]"""
    tree = defaultdict(lambda: defaultdict(list))
    for c in claims:
        rel = c["box06_patient_relationship"]
        ins = c["box01_insurance_type"]
        tree[rel][ins].append({
            "acct":    c["box26_patient_account_no"],
            "patient": c["box02_patient_name"],
            "dos":     c["box24a_dos_from"],
            "cpt":     c["box24d_cpt_code"],
            "desc":    c["box24d_cpt_description"],
            "diag":    c["box21_diag1_icd10"],
            "charge":  float(c["box28_total_charge"]),
            "paid":    float(c["box29_amount_paid"]),
        })
    # Sort relationships: Self first, then alphabetical
    order = ["Self", "Spouse", "Child", "Other"]
    return {r: dict(tree[r]) for r in order if r in tree}


def render_hierarchy(hierarchy):
    html = ""
    rel_colors = {"Self": "#1a3a5c", "Spouse": "#2e6da4", "Child": "#27a069", "Other": "#e05c2a"}
    for rel, ins_groups in hierarchy.items():
        total_claims = sum(len(v) for v in ins_groups.values())
        total_billed = sum(c["charge"] for v in ins_groups.values() for c in v)
        color = rel_colors.get(rel, "#555")
        html += f"""
  <div class="h-group">
    <div class="h-rel" onclick="toggleNode(this)" style="border-left: 4px solid {color}">
      <span class="h-arrow">▶</span>
      <span class="h-label">{rel}</span>
      <span class="h-meta">{total_claims} claims &nbsp;|&nbsp; ${total_billed:,.2f} billed</span>
    </div>
    <div class="h-children" style="display:none">"""

        for ins, claim_list in ins_groups.items():
            ins_billed = sum(c["charge"] for c in claim_list)
            html += f"""
      <div class="h-ins-group">
        <div class="h-ins" onclick="toggleNode(this)">
          <span class="h-arrow">▶</span>
          <span class="h-label">{ins}</span>
          <span class="h-meta">{len(claim_list)} claims &nbsp;|&nbsp; ${ins_billed:,.2f} billed</span>
        </div>
        <div class="h-children" style="display:none">
          <table class="h-table">
            <thead><tr>
              <th>Account</th><th>Patient</th><th>DOS</th>
              <th>CPT</th><th>Description</th><th>ICD-10</th>
              <th>Billed</th><th>Paid</th>
            </tr></thead>
            <tbody>"""
            for c in claim_list:
                html += f"""
              <tr>
                <td>{c['acct']}</td>
                <td>{c['patient']}</td>
                <td>{c['dos']}</td>
                <td><span class="badge">{c['cpt']}</span></td>
                <td class="small">{c['desc']}</td>
                <td><span class="badge diag">{c['diag']}</span></td>
                <td class="amount">${c['charge']:,.2f}</td>
                <td class="amount paid">${c['paid']:,.2f}</td>
              </tr>"""
            html += """
            </tbody>
          </table>
        </div>
      </div>"""

        html += """
    </div>
  </div>"""
    return html


def render_html(claims, s):
    # Build table rows
    rows_html = ""
    for c in claims:
        rows_html += f"""
        <tr>
          <td>{c['box26_patient_account_no']}</td>
          <td>{c['box02_patient_name']}</td>
          <td>{c['box03_patient_dob']}</td>
          <td>{c['box03_patient_sex']}</td>
          <td>{c['box01_insurance_type']}</td>
          <td>{c['box06_patient_relationship']}</td>
          <td>{c['box24a_dos_from']}</td>
          <td><span class="badge">{c['box24d_cpt_code']}</span></td>
          <td class="small">{c['box24d_cpt_description']}</td>
          <td><span class="badge diag">{c['box21_diag1_icd10']}</span></td>
          <td>{c['box24b_place_of_service']}</td>
          <td class="amount">${float(c['box24f_charge']):.2f}</td>
          <td class="amount">${float(c['box28_total_charge']):.2f}</td>
          <td class="amount paid">${float(c['box29_amount_paid']):.2f}</td>
          <td>{c['box27_accept_assignment']}</td>
          <td class="small">{c['box17_referring_provider']}</td>
        </tr>"""

    ins_labels  = json.dumps(list(s["ins_counts"].keys()))
    ins_data    = json.dumps(list(s["ins_counts"].values()))
    pos_labels  = json.dumps(list(s["pos_counts"].keys()))
    pos_data    = json.dumps(list(s["pos_counts"].values()))
    cpt_labels  = json.dumps(list(s["cpt_counts"].keys()))
    cpt_data    = json.dumps(list(s["cpt_counts"].values()))
    diag_labels = json.dumps(list(s["diag_counts"].keys()))
    diag_data   = json.dumps(list(s["diag_counts"].values()))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CMS-1500 Claims Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f0f2f5; color: #222; }}
  header {{ background: #1a3a5c; color: #fff; padding: 1.2rem 2rem; }}
  header h1 {{ font-size: 1.4rem; font-weight: 600; }}
  header p  {{ font-size: 0.85rem; opacity: .7; margin-top: .2rem; }}

  .cards {{ display: flex; gap: 1rem; padding: 1.5rem 2rem 0; flex-wrap: wrap; }}
  .card {{ background: #fff; border-radius: 8px; padding: 1rem 1.4rem;
           flex: 1; min-width: 160px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .card .label {{ font-size: .75rem; color: #666; text-transform: uppercase; letter-spacing: .05em; }}
  .card .value {{ font-size: 1.6rem; font-weight: 700; margin-top: .2rem; color: #1a3a5c; }}

  .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;
             padding: 1.5rem 2rem; }}
  .chart-box {{ background: #fff; border-radius: 8px; padding: 1rem 1.2rem;
               box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .chart-box h3 {{ font-size: .85rem; color: #444; margin-bottom: .8rem;
                  text-transform: uppercase; letter-spacing: .05em; }}

  .table-wrap {{ margin: 0 2rem 2rem; background: #fff; border-radius: 8px;
                 box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden; }}
  .table-toolbar {{ display: flex; align-items: center; justify-content: space-between;
                    padding: .8rem 1.2rem; border-bottom: 1px solid #eee; }}
  .table-toolbar h3 {{ font-size: .95rem; font-weight: 600; }}
  .table-toolbar input {{ padding: .4rem .8rem; border: 1px solid #ddd; border-radius: 6px;
                          font-size: .85rem; width: 220px; outline: none; }}
  .table-toolbar input:focus {{ border-color: #1a3a5c; }}
  .scroll {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
  thead tr {{ background: #1a3a5c; color: #fff; }}
  thead th {{ padding: .6rem .8rem; text-align: left; white-space: nowrap;
              font-weight: 500; cursor: pointer; user-select: none; }}
  thead th:hover {{ background: #254d78; }}
  tbody tr:nth-child(even) {{ background: #f8f9fb; }}
  tbody tr:hover {{ background: #e8f0fb; }}
  td {{ padding: .5rem .8rem; white-space: nowrap; }}
  td.small {{ max-width: 180px; white-space: nowrap; overflow: hidden;
              text-overflow: ellipsis; }}
  td.amount {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.paid {{ color: #1a7a4a; font-weight: 600; }}
  .badge {{ background: #e8f0fb; color: #1a3a5c; padding: .15rem .5rem;
            border-radius: 4px; font-size: .78rem; font-weight: 600; }}
  .badge.diag {{ background: #fef3e2; color: #9a5000; }}
  .no-results {{ text-align: center; padding: 2rem; color: #888; }}

  /* Hierarchy */
  .hierarchy-wrap {{ margin: 0 2rem 2rem; background: #fff; border-radius: 8px;
                     box-shadow: 0 1px 4px rgba(0,0,0,.08); overflow: hidden; }}
  .hierarchy-wrap .section-header {{ display: flex; align-items: center; justify-content: space-between;
                                      padding: .8rem 1.2rem; border-bottom: 1px solid #eee; }}
  .hierarchy-wrap .section-header h3 {{ font-size: .95rem; font-weight: 600; }}
  .hierarchy-wrap .section-header button {{ font-size: .78rem; padding: .3rem .7rem; border: 1px solid #ddd;
                                             border-radius: 5px; cursor: pointer; background: #f8f9fb; }}
  .h-group {{ border-bottom: 1px solid #f0f0f0; }}
  .h-rel {{ display: flex; align-items: center; gap: .6rem; padding: .7rem 1.2rem;
            cursor: pointer; background: #f8f9fb; font-weight: 600; font-size: .88rem; }}
  .h-rel:hover {{ background: #eef2fb; }}
  .h-ins-group {{ margin-left: 2rem; border-left: 2px solid #e0e8f0; }}
  .h-ins {{ display: flex; align-items: center; gap: .6rem; padding: .55rem 1rem;
            cursor: pointer; font-size: .84rem; font-weight: 500; }}
  .h-ins:hover {{ background: #f0f5fc; }}
  .h-arrow {{ font-size: .65rem; color: #888; transition: transform .2s; min-width: 10px; }}
  .h-arrow.open {{ transform: rotate(90deg); }}
  .h-label {{ flex: 0 0 auto; }}
  .h-meta {{ margin-left: auto; font-size: .78rem; color: #777; font-weight: 400; }}
  .h-children {{ padding-left: .5rem; }}
  .h-table {{ width: 100%; border-collapse: collapse; font-size: .8rem; margin: .4rem 0 .6rem 1rem; width: calc(100% - 1rem); }}
  .h-table thead tr {{ background: #e8f0fb; }}
  .h-table th {{ padding: .4rem .7rem; text-align: left; font-weight: 500; color: #1a3a5c; white-space: nowrap; }}
  .h-table td {{ padding: .4rem .7rem; border-bottom: 1px solid #f4f4f4; white-space: nowrap; }}
  .h-table tr:last-child td {{ border-bottom: none; }}
  .h-table tr:hover td {{ background: #f5f8ff; }}
  .h-table td.small {{ max-width: 200px; overflow: hidden; text-overflow: ellipsis; }}
  .h-table td.amount {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .h-table td.paid {{ color: #1a7a4a; font-weight: 600; }}
</style>
</head>
<body>

<header>
  <h1>CMS-1500 Claims Dashboard</h1>
  <p>Sample dataset &mdash; {s['total_claims']} claims</p>
</header>

<div class="cards">
  <div class="card">
    <div class="label">Total Claims</div>
    <div class="value">{s['total_claims']}</div>
  </div>
  <div class="card">
    <div class="label">Total Billed</div>
    <div class="value">${s['total_billed']:,.2f}</div>
  </div>
  <div class="card">
    <div class="label">Total Paid</div>
    <div class="value">${s['total_paid']:,.2f}</div>
  </div>
  <div class="card">
    <div class="label">Avg Charge</div>
    <div class="value">${s['avg_charge']:,.2f}</div>
  </div>
  <div class="card">
    <div class="label">Collection Rate</div>
    <div class="value">{(s['total_paid']/s['total_billed']*100):.1f}%</div>
  </div>
</div>

<div class="charts">
  <div class="chart-box">
    <h3>Insurance Type</h3>
    <canvas id="insChart"></canvas>
  </div>
  <div class="chart-box">
    <h3>Place of Service</h3>
    <canvas id="posChart"></canvas>
  </div>
  <div class="chart-box">
    <h3>Top CPT Codes</h3>
    <canvas id="cptChart"></canvas>
  </div>
  <div class="chart-box">
    <h3>Top Diagnoses (ICD-10)</h3>
    <canvas id="diagChart"></canvas>
  </div>
</div>

<div class="hierarchy-wrap">
  <div class="section-header">
    <h3>Claims Hierarchy &mdash; by Relationship</h3>
    <div style="display:flex;gap:.5rem">
      <button onclick="expandAll()">Expand All</button>
      <button onclick="collapseAll()">Collapse All</button>
    </div>
  </div>
  {render_hierarchy(s['rel_hierarchy'])}
</div>

<div class="table-wrap">
  <div class="table-toolbar">
    <h3>Claim Records</h3>
    <input type="text" id="search" placeholder="Search claims..."/>
  </div>
  <div class="scroll">
    <table id="claimsTable">
      <thead>
        <tr>
          <th>Account #</th>
          <th>Patient</th>
          <th>DOB</th>
          <th>Sex</th>
          <th>Insurance</th>
          <th>Relationship</th>
          <th>DOS</th>
          <th>CPT</th>
          <th>Description</th>
          <th>ICD-10</th>
          <th>POS</th>
          <th>Charge</th>
          <th>Total</th>
          <th>Paid</th>
          <th>Assignment</th>
          <th>Referring Provider</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        {rows_html}
      </tbody>
    </table>
  </div>
</div>

<script>
const COLORS = ['#1a3a5c','#2e6da4','#4a9fd4','#f4a521','#e05c2a',
                '#27a069','#8e44ad','#c0392b','#16a085','#d35400'];

function makeChart(id, type, labels, data, opts={{}}) {{
  new Chart(document.getElementById(id), {{
    type,
    data: {{ labels, datasets: [{{ data, backgroundColor: COLORS,
              borderColor: type === 'bar' ? COLORS : '#fff',
              borderWidth: type === 'bar' ? 0 : 2 }}] }},
    options: {{ plugins: {{ legend: {{ display: type !== 'bar' }} }},
                scales: type === 'bar' ? {{ y: {{ beginAtZero: true }} }} : {{}},
                ...opts }}
  }});
}}

makeChart('insChart',  'doughnut', {ins_labels},  {ins_data});
makeChart('posChart',  'doughnut', {pos_labels},  {pos_data});
new Chart(document.getElementById('cptChart'), {{
  type: 'bar',
  data: {{ labels: {cpt_labels}, datasets: [{{ data: {cpt_data},
    backgroundColor: COLORS, borderWidth: 0 }}] }},
  options: {{
    indexAxis: 'y',
    plugins: {{ legend: {{ display: false }} }},
    scales: {{ x: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }}
  }}
}});
makeChart('diagChart', 'bar',      {diag_labels}, {diag_data});

// Hierarchy toggles
function toggleNode(el) {{
  const children = el.nextElementSibling;
  const arrow    = el.querySelector('.h-arrow');
  const open     = children.style.display !== 'none';
  children.style.display = open ? 'none' : 'block';
  arrow.classList.toggle('open', !open);
}}
function expandAll() {{
  document.querySelectorAll('.h-children').forEach(el => el.style.display = 'block');
  document.querySelectorAll('.h-arrow').forEach(el => el.classList.add('open'));
}}
function collapseAll() {{
  document.querySelectorAll('.h-children').forEach(el => el.style.display = 'none');
  document.querySelectorAll('.h-arrow').forEach(el => el.classList.remove('open'));
}}

// Search / filter
document.getElementById('search').addEventListener('input', function() {{
  const q = this.value.toLowerCase();
  const rows = document.querySelectorAll('#tableBody tr');
  let visible = 0;
  rows.forEach(row => {{
    const match = row.textContent.toLowerCase().includes(q);
    row.style.display = match ? '' : 'none';
    if (match) visible++;
  }});
  const noRes = document.getElementById('noResults');
  if (visible === 0 && !noRes) {{
    const tr = document.createElement('tr');
    tr.id = 'noResults';
    tr.innerHTML = '<td colspan="16" class="no-results">No matching claims found.</td>';
    document.getElementById('tableBody').appendChild(tr);
  }} else if (visible > 0 && noRes) {{
    noRes.remove();
  }}
}});

// Column sort
document.querySelectorAll('thead th').forEach((th, col) => {{
  let asc = true;
  th.addEventListener('click', () => {{
    const tbody = document.getElementById('tableBody');
    const rows  = Array.from(tbody.querySelectorAll('tr[style=""], tr:not([style])'))
                       .filter(r => r.id !== 'noResults');
    rows.sort((a, b) => {{
      const av = a.cells[col]?.textContent.trim() ?? '';
      const bv = b.cells[col]?.textContent.trim() ?? '';
      const an = parseFloat(av.replace(/[$,]/g, ''));
      const bn = parseFloat(bv.replace(/[$,]/g, ''));
      if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
      return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    }});
    rows.forEach(r => tbody.appendChild(r));
    asc = !asc;
  }});
}});
</script>
</body>
</html>"""


def main():
    claims  = load_claims()
    summary = build_summary(claims)
    html    = render_html(claims, summary)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Report written -> {OUTPUT}")


if __name__ == "__main__":
    main()
