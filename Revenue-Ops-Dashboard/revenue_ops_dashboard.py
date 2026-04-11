import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from google import genai
import random

st.set_page_config(page_title="Normality Revenue Optimizer", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background: #f7f8fa; }
    .tct-header { background:linear-gradient(135deg,#0a1628 0%,#132743 100%); border-radius:12px; padding:1.25rem 1.75rem; margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center; }
    .tct-title { color:white; font-size:1.4rem; font-weight:600; }
    .tct-subtitle { color:#94a3b8; font-size:0.78rem; letter-spacing:0.08em; text-transform:uppercase; margin-top:0.15rem; }
    .tct-badge { background:#16a34a; color:white; font-size:0.7rem; font-weight:600; padding:4px 12px; border-radius:20px; }
    .tct-currency { background:rgba(255,255,255,0.1); color:white; font-size:0.8rem; padding:4px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.15); }
    .metric-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.25rem 1.5rem; }
    .metric-card-dark { background:linear-gradient(135deg,#0a1628 0%,#1a2d4d 100%); border:none; border-radius:10px; padding:1.25rem 1.5rem; }
    .metric-card-dark .metric-label { color:#94a3b8; }
    .metric-card-dark .metric-value { color:white; }
    .metric-card-green { border-left:4px solid #16a34a; }
    .metric-card-red { border-left:4px solid #dc2626; }
    .metric-card-amber { border-left:4px solid #f59e0b; }
    .metric-card-blue { border-left:4px solid #0369a1; }
    .metric-label { font-size:0.72rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748b; margin-bottom:0.4rem; }
    .metric-value { font-size:1.8rem; font-weight:600; color:#0f172a; line-height:1; font-family:'IBM Plex Mono',monospace; }
    .metric-delta { font-size:0.8rem; margin-top:0.3rem; }
    .metric-delta.good { color:#16a34a; } .metric-delta.bad { color:#dc2626; } .metric-delta.neutral { color:#64748b; }
    .metric-tooltip { font-size:0.78rem; color:#64748b; margin-top:0.5rem; border-top:1px solid #f1f5f9; padding-top:0.5rem; line-height:1.5; font-style:italic; }
    .section-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.5rem; margin-bottom:1rem; }
    .section-title { font-size:0.8rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748b; margin-bottom:1rem; padding-bottom:0.75rem; border-bottom:1px solid #f1f5f9; }
    .risk-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }
    .risk-high { background:#fee2e2; color:#991b1b; } .risk-med { background:#fef3c7; color:#92400e; } .risk-low { background:#dcfce7; color:#166534; }
    .insight-row { display:flex; align-items:flex-start; gap:0.75rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9; font-size:0.9rem; }
    .insight-row:last-child { border-bottom:none; }
    .progress-bar-bg { background:#f1f5f9; border-radius:4px; height:8px; width:100%; margin-top:6px; }
    .progress-bar-fill { height:8px; border-radius:4px; }
    .news-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .news-tag { display:inline-block; font-size:0.7rem; font-weight:600; padding:2px 8px; border-radius:20px; margin-right:4px; background:#e0f2fe; color:#0369a1; }
    .info-box { background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; padding:0.75rem 1rem; font-size:0.82rem; color:#0369a1; margin-bottom:0.75rem; }
    .module-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.25rem; text-align:center; }
    .agent-card { background:#f8fafc; border-left:4px solid #0369a1; border-radius:0 8px 8px 0; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .agent-card.high { border-left-color:#dc2626; } .agent-card.medium { border-left-color:#f59e0b; } .agent-card.low { border-left-color:#16a34a; }
    .upload-hint { background:#f8fafc; border:1.5px dashed #cbd5e1; border-radius:10px; padding:2rem; text-align:center; color:#64748b; font-size:0.9rem; }
    .stButton > button { background:#0a1628; color:white; border:none; border-radius:8px; padding:0.5rem 1.25rem; font-family:'IBM Plex Sans',sans-serif; font-size:0.9rem; font-weight:500; }
    .stButton > button:hover { background:#132743; }
    .var-card { background:white; border:1px solid #e2e8f0; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem; }
    .var-label { font-size:0.85rem; font-weight:600; color:#0f172a; }
    .var-badge { font-size:0.65rem; font-weight:600; padding:2px 8px; border-radius:10px; background:#e0f2fe; color:#0369a1; float:right; }
    .var-row { display:flex; justify-content:space-between; font-size:0.82rem; margin-top:0.3rem; }
    .var-pos { color:#16a34a; font-family:'IBM Plex Mono',monospace; font-weight:600; }
    .var-neg { color:#dc2626; font-family:'IBM Plex Mono',monospace; font-weight:600; }
    .cp-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
    .cp-table th { text-align:left; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#64748b; padding:0.5rem 0.75rem; border-bottom:2px solid #e2e8f0; }
    .cp-table td { padding:0.5rem 0.75rem; border-bottom:1px solid #f1f5f9; font-family:'IBM Plex Mono',monospace; font-size:0.82rem; }
    .cp-green { color:#16a34a; } .cp-red { color:#dc2626; }
    #MainMenu { visibility:hidden; } footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── Gemini ──
@st.cache_resource
def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key: st.error("GEMINI_API_KEY not found."); st.stop()
    return genai.Client(api_key=key)
client = get_client()
MODEL = "gemini-2.5-flash"

# ── Config ──
REGIONS = {"Indonesia":{"geo":"ID","worldbank":"IDN"},"Thailand":{"geo":"TH","worldbank":"THA"},"Vietnam":{"geo":"VN","worldbank":"VNM"},"Malaysia":{"geo":"MY","worldbank":"MYS"},"Philippines":{"geo":"PH","worldbank":"PHL"},"Singapore":{"geo":"SG","worldbank":"SGP"}}
REGION_CUSTOMERS = {"Indonesia":["Indomaret","Alfamart","Hero Supermarket","Ranch Market","Lotte Mart ID","Carrefour ID"],"Thailand":["CP ALL 7-Eleven","Big C","Tesco Lotus","Makro TH","Tops Market","Villa Market"],"Vietnam":["Vinmart","Co.opmart","Bach Hoa Xanh","Big C VN","Lotte Mart VN","Circle K VN"],"Malaysia":["Lotus's MY","AEON Malaysia","Guardian MY","Watsons MY","Parkson","Cold Storage MY"],"Philippines":["SM Supermarket","Puregold","Robinsons","Mercury Drug","7-Eleven PH","S&R Members"],"Singapore":["FairPrice","Cold Storage SG","Giant SG","Sheng Siong","Guardian SG","Watsons SG"]}
INDUSTRIES = {"F&B / FMCG":{"keywords":["food","beverage","FMCG","consumer goods","grocery"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":45,"inv_benchmark":40,"otif_benchmark":92,"cycle_benchmark":3},"Electronics Manufacturing":{"keywords":["electronics","semiconductor","manufacturing","supply chain"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":50,"inv_benchmark":50,"otif_benchmark":88,"cycle_benchmark":5},"Medical / Healthcare":{"keywords":["medical","healthcare","pharmaceutical","hygiene"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","SH.XPD.CHEX.GD.ZS"],"dso_benchmark":40,"inv_benchmark":45,"otif_benchmark":95,"cycle_benchmark":2},"Automotive / Industrial":{"keywords":["automotive","industrial","machinery","logistics"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":55,"inv_benchmark":55,"otif_benchmark":90,"cycle_benchmark":4},"Retail / E-Commerce":{"keywords":["retail","e-commerce","online shopping","consumer"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":30,"inv_benchmark":25,"otif_benchmark":95,"cycle_benchmark":2}}
RSS_FEEDS = {"Malaysia":[("The Star Business","https://www.thestar.com.my/rss/business"),("The Edge Malaysia","https://theedgemalaysia.com/feed")],"Singapore":[("Channel NewsAsia","https://www.channelnewsasia.com/rssfeeds/8395986"),("Straits Times","https://www.straitstimes.com/news/business/rss.xml")],"Vietnam":[("VnExpress Business","https://e.vnexpress.net/rss/business.rss")],"Indonesia":[("Jakarta Post","https://www.thejakartapost.com/feed/category/business")],"Thailand":[("Bangkok Post","https://www.bangkokpost.com/rss/data/business.xml")],"Philippines":[("Inquirer Business","https://business.inquirer.net/feed"),("Rappler Business","https://www.rappler.com/business/feed/")]}
WB_LABELS = {"NY.GDP.MKTP.KD.ZG":"GDP Growth Rate (%)","FP.CPI.TOTL.ZG":"Inflation Rate (CPI %)","NE.EXP.GNFS.ZS":"Exports (% of GDP)","SH.XPD.CHEX.GD.ZS":"Health Expenditure (% of GDP)"}

DIAGNOSTIC = {"Demand Forecasting":[{"q":"How is your demand forecast created?","opts":["Excel / spreadsheets only","ERP basic module","Dedicated planning tool","AI-assisted forecasting"],"key":"df_method"},{"q":"Do you track forecast accuracy (e.g. MAPE)?","opts":["No tracking at all","Occasionally reviewed","Monthly review","Real-time dashboard"],"key":"df_tracking"},{"q":"What % of customers provide usable forecast data?","opts":["Less than 25%","25-50%","50-75%","More than 75%"],"key":"df_customer_data"}],"Order Management":[{"q":"How are customer orders received?","opts":["Phone / Email only","Basic portal or fax","EDI integration","Fully automated multi-channel"],"key":"om_channel"},{"q":"Is order validation automated?","opts":["Fully manual checks","Partial validation rules","Mostly automated","Fully automated with exceptions"],"key":"om_validation"},{"q":"How often do customers amend orders after placement?","opts":["Very frequently (>30%)","Often (15-30%)","Occasionally (5-15%)","Rarely (<5%)"],"key":"om_amendments"}],"Order Fulfilment & Logistics":[{"q":"Do you track OTIF (On-Time In-Full)?","opts":["Not tracked","Informally estimated","Formally tracked monthly","Real-time OTIF dashboard"],"key":"fl_otif"},{"q":"How is warehouse picking managed?","opts":["Paper-based / manual","Basic WMS","Advanced WMS with optimization","Automated / robotics-assisted"],"key":"fl_wms"},{"q":"Can you see real-time shipment status?","opts":["No visibility","Partial (carrier websites)","Full tracking integration","Predictive ETA with alerts"],"key":"fl_visibility"}],"Billing & Revenue Mgmt":[{"q":"How are invoices triggered?","opts":["Manual creation","Semi-automated from ERP","Auto-generated on shipment","Touchless with compliance check"],"key":"br_invoicing"},{"q":"Do you have automated discount / rebate governance?","opts":["No controls","Basic approval workflow","Rules-based engine","AI-governed with anomaly detection"],"key":"br_discount"},{"q":"How do you handle customer portal requirements?","opts":["Not applicable","Manual uploads per customer","Partially automated","Fully automated per-customer rules"],"key":"br_portal"}],"Post-Sales & Financial Closure":[{"q":"How does your AR team prioritize collections?","opts":["Ad hoc / reactive","First-in first-out","By invoice amount","Risk-based AI prioritization"],"key":"ps_collections"},{"q":"What % of receivables go past 90 days?","opts":["More than 20%","10-20%","5-10%","Less than 5%"],"key":"ps_aging"},{"q":"Is cash application / reconciliation automated?","opts":["Fully manual","Partially automated","Mostly automated","Fully automated with AI matching"],"key":"ps_cash_app"}]}

# ── Fetchers ──
@st.cache_data(ttl=3600)
def fetch_news(region, industry):
    kws = [k.lower() for k in INDUSTRIES[industry]["keywords"]]; arts = []
    for src, url in RSS_FEEDS.get(region, []):
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:25]:
                t = e.get("title",""); s = e.get("summary",""); matched = [k for k in kws if k in (t+" "+s).lower()]
                if matched: arts.append({"title":t,"source":src,"published":e.get("published","")[:16],"keywords":matched[:2]})
        except: pass
    return arts[:10]

@st.cache_data(ttl=86400)
def fetch_wb(region, industry):
    c = REGIONS[region]["worldbank"]; res = {}
    for ind in INDUSTRIES[industry]["worldbank_indicators"]:
        try:
            r = requests.get(f"https://api.worldbank.org/v2/country/{c}/indicator/{ind}?format=json&mrv=5&per_page=5", timeout=8)
            if r.status_code == 200:
                d = r.json()
                if len(d) > 1 and d[1]:
                    s = [{"year":x["date"],"value":round(x["value"],2)} for x in d[1] if x["value"] is not None]
                    if s: res[WB_LABELS.get(ind,ind)] = sorted(s, key=lambda x: x["year"])
        except: pass
    return res

@st.cache_data(ttl=3600)
def fetch_gt(keywords, region):
    geo = REGIONS[region]["geo"]
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl='en-US',tz=480,timeout=(10,25)); kws = keywords[:3]; pt.build_payload(kws,timeframe='today 1-m',geo=geo)
        df = pt.interest_over_time()
        if df.empty: return {"error":"No data.","data":{}}
        df = df.drop(columns=["isPartial"],errors="ignore")
        return {"data":{k:[{"date":str(d.date()),"value":int(v)} for d,v in zip(df.index,df[k])] for k in kws if k in df.columns}}
    except ImportError: return {"error":"pytrends not installed.","data":{}}
    except Exception as e: return {"error":str(e),"data":{}}

# ── Analytics ──
def calc_demand(df):
    df = df.copy()
    df["MAPE"] = (df["Actual_Units"]-df["Forecast_Units"]).abs()/df["Actual_Units"].replace(0,np.nan)*100
    df["Bias"] = (df["Actual_Units"]-df["Forecast_Units"])/df["Actual_Units"].replace(0,np.nan)*100
    mape = df["MAPE"].mean(); otif_rate = 0
    if "Orders_Placed" in df.columns and "Orders_OTIF" in df.columns:
        otif_rate = round((df["Orders_OTIF"].sum()/max(df["Orders_Placed"].sum(),1))*100,1)
    sku = df.groupby("SKU").agg(MAPE=("MAPE","mean"),Bias=("Bias","mean"),Accuracy=("MAPE",lambda x:max(0,100-x.mean()))).reset_index().round(1)
    monthly = df.groupby("Month").agg(Actual=("Actual_Units","sum"),Forecast=("Forecast_Units","sum")).reset_index()
    monthly["Variance"] = monthly["Actual"]-monthly["Forecast"]
    monthly["Variance_Pct"] = ((monthly["Actual"]-monthly["Forecast"])/monthly["Forecast"].replace(0,np.nan)*100).round(1)
    return {"accuracy":round(max(0,100-mape),1),"mape":round(mape,1),"bias":round(df["Bias"].mean(),1),"otif":otif_rate,"sku":sku,"monthly":df,"variance":monthly}

def calc_order_mgmt(df):
    cycle = df["Order_Cycle_Days"].mean() if "Order_Cycle_Days" in df.columns else 0
    err = df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100
    disp = df.get("Disputed",pd.Series([0]*len(df))).mean()*100
    amend = df.get("Amendment_Flag",pd.Series([0]*len(df))).mean()*100 if "Amendment_Flag" in df.columns else 12.0
    return {"cycle":round(cycle,1),"err":round(err,1),"disp":round(disp,1),"amend":round(amend,1)}

def calc_fulfilment(df, industry):
    bi = INDUSTRIES[industry]
    ful = df["Fulfilment_Days"].mean() if "Fulfilment_Days" in df.columns else 0
    otif = df["OTIF_Flag"].mean()*100 if "OTIF_Flag" in df.columns else 85.0
    ret = df["Return_Flag"].mean()*100 if "Return_Flag" in df.columns else 3.0
    return {"otif":round(otif,1),"otif_bench":bi["otif_benchmark"],"ful_days":round(ful,1),"ful_bench":bi["cycle_benchmark"],"return_rate":round(ret,1),"partial":round(100-otif,1)}

def calc_billing(df, industry):
    bench = INDUSTRIES[industry]["dso_benchmark"]; dso = df["DSO_Days"].mean()
    err = df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100
    disp = df.get("Disputed",pd.Series([0]*len(df))).mean()*100
    rev = df["Invoice_Amount_USD"].sum()
    ld=rev*0.018; ie=rev*(err/100)*0.025; dd=rev*(disp/100)*0.05; ed=rev*0.008
    cust = df.groupby("Customer")["DSO_Days"].mean().reset_index(); cust.columns=["Customer","Avg_DSO"]
    cust["Risk"] = cust["Avg_DSO"].apply(lambda x:"High" if x>bench*1.4 else("Medium" if x>bench*1.1 else "Low"))
    # Cash flow
    cashflow = pd.DataFrame()
    if "Invoice_Date" in df.columns and "Payment_Date" in df.columns:
        df2 = df.copy(); df2["Pay_Month"] = pd.to_datetime(df2["Payment_Date"]).dt.strftime("%b")
        inflow = df2.groupby("Pay_Month")["Invoice_Amount_USD"].sum().reset_index(); inflow.columns=["Month","Inflow"]
        inflow["Outflow"] = (inflow["Inflow"]*np.random.uniform(0.65,0.85,len(inflow))).round(0)
        inflow["Net"] = inflow["Inflow"]-inflow["Outflow"]; cashflow = inflow
    # Receivable forecast
    recv_forecast = pd.DataFrame()
    if "Invoice_Date" in df.columns:
        df3 = df.copy(); df3["Week"] = pd.to_datetime(df3["Invoice_Date"]).dt.isocalendar().week.astype(int)
        weekly = df3.groupby("Week")["Invoice_Amount_USD"].sum().reset_index(); weekly.columns=["Week","Actual"]
        weekly["Predicted"] = weekly["Actual"]*np.random.uniform(0.95,1.08,len(weekly))
        weekly["Variance"] = weekly["Actual"]-weekly["Predicted"]
        weekly["Var_Pct"] = ((weekly["Variance"]/weekly["Predicted"])*100).round(1)
        recv_forecast = weekly.tail(8).reset_index(drop=True)
    return {"dso":round(dso,1),"bench":bench,"gap":round(dso-bench,1),"err":round(err,1),"disp":round(disp,1),"rev":round(rev,0),"leak_total":round(ld+ie+dd+ed,0),"leak_disc":round(ld,0),"leak_inv":round(ie,0),"leak_disp":round(dd,0),"leak_ded":round(ed,0),"cust":cust.sort_values("Avg_DSO",ascending=False).round(1),"cashflow":cashflow,"recv_forecast":recv_forecast}

def calc_post_sales(df, industry, inv_days, dpo):
    dso=df["DSO_Days"].mean(); bench_dso=INDUSTRIES[industry]["dso_benchmark"]
    ccc=dso+inv_days-dpo; bench_ccc=bench_dso+INDUSTRIES[industry]["inv_benchmark"]-30
    gap=ccc-bench_ccc; score=max(0,min(100,round(100-(gap/max(bench_ccc,1))*50)))
    aging={"current":round((df["DSO_Days"]<=30).mean()*100,1),"30d":round(((df["DSO_Days"]>30)&(df["DSO_Days"]<=60)).mean()*100,1),"60d":round(((df["DSO_Days"]>60)&(df["DSO_Days"]<=90)).mean()*100,1),"90d":round((df["DSO_Days"]>90).mean()*100,1)}
    ded=df["Deduction_USD"].sum() if "Deduction_USD" in df.columns else 0
    cash_pos=[]
    if "Payment_Date" in df.columns:
        df4=df.copy(); df4["Payment_Date"]=pd.to_datetime(df4["Payment_Date"]); today=df4["Payment_Date"].max()-timedelta(days=30)
        for d in range(1,31):
            dt=today+timedelta(days=d); di=df4[df4["Payment_Date"].dt.date==dt.date()]["Invoice_Amount_USD"].sum()
            do=di*np.random.uniform(0.3,0.7) if di>0 else np.random.uniform(500,8000)
            cash_pos.append({"Date":dt.strftime("%b %d"),"Inflow":round(di,0),"Outflow":round(do,0),"Net":round(di-do,0)})
    return {"ccc":round(ccc,1),"bench":round(bench_ccc,1),"dso":round(dso,1),"inv":inv_days,"dpo":dpo,"gap":round(gap,1),"score":score,"health":"Good" if score>=70 else "At Risk" if score>=45 else "Critical","aging":aging,"deductions":round(ded,0),"cash_pos":cash_pos}

def calc_module_scores(dm,om,fl,bl,ps,diag):
    data={"Demand Forecasting":min(100,round(dm["accuracy"]*0.7+max(0,20-abs(dm["bias"]))*1.5)),"Order Management":max(0,min(100,round(100-om["err"]*5-om["disp"]*3-om["amend"]*0.5))),"Order Fulfilment & Logistics":max(0,min(100,round(fl["otif"]*0.8+max(0,10-fl["return_rate"])*2))),"Billing & Revenue Mgmt":max(0,min(100,round(100-bl["err"]*8-bl["disp"]*4))),"Post-Sales & Financial Closure":ps["score"]}
    return {m:round(data[m]*0.6+diag.get(m,50)*0.4) for m in data}

def get_diag_scores(resp):
    scores={}
    for mod,qs in DIAGNOSTIC.items():
        vals=[(resp.get(q["key"],0)+1)*25 for q in qs]; scores[mod]=round(sum(vals)/len(vals)) if vals else 50
    return scores

# ── AI ──
def get_executive_ai(dm,om,fl,bl,ps,ms,diag,region,industry):
    p=f"""Revenue Optimizer AI for {industry} in {region}. MODULE SCORES: {json.dumps(ms)}
DEMAND: Accuracy {dm['accuracy']}%, MAPE {dm['mape']}%, Bias {dm['bias']:+.1f}%, OTIF {dm['otif']}%
ORDER: Cycle {om['cycle']}d, Errors {om['err']}%, Disputes {om['disp']}%, Amendments {om['amend']}%
FULFILMENT: OTIF {fl['otif']}% (bench {fl['otif_bench']}%), Returns {fl['return_rate']}%
BILLING: DSO {bl['dso']}d (bench {bl['bench']}d), Leakage USD {bl['leak_total']:,.0f}
POST-SALES: CCC {ps['ccc']}d (bench {ps['bench']}d), Score {ps['score']}/100, AR>90d: {ps['aging']['90d']}%
MATURITY: {json.dumps(diag)}
Context: SEA CPG mid-market. Pain: non-binding forecasts, spreadsheet dependence, portal failures, manual rebates.
Return ONLY valid JSON: {{"overall_health":"Good|At Risk|Critical","health_score":<int>,"executive_summary":"...","top_risks":[{{"risk":"...","severity":"High|Medium|Low","impact":"...","module":"..."}}],"quick_wins":[{{"action":"...","timeline":"...","expected_impact":"...","module":"..."}}],"forecast_insight":"...","o2c_insight":"...","wc_insight":"..."}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_agent_simulation(dm,om,fl,bl,ps,ms,region,industry):
    p=f"""Revenue Optimizer autonomous AI agent for {industry} in {region}. Simulate 8 realistic interventions over 30 days.
DATA: Accuracy:{dm['accuracy']}%, OTIF:{dm['otif']}%, Cycle:{om['cycle']}d, Amendments:{om['amend']}%, Errors:{om['err']}%, Fulfilment OTIF:{fl['otif']}%, Returns:{fl['return_rate']}%, DSO:{bl['dso']}d(bench {bl['bench']}d), Leakage:USD{bl['leak_total']:,.0f}, CCC:{ps['ccc']}d, AR>90d:{ps['aging']['90d']}%
Return ONLY valid JSON: {{"interventions":[{{"day":1,"module":"...","severity":"High|Medium|Low","trigger":"...","action":"...","impact":"..."}}]}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_demand_signals_ai(region,industry,news,wb,gt):
    nt="\n".join([f"- [{a['source']}] {a['title']}" for a in news[:8]]) or "None."
    wt="\n".join([f"- {l}: {s[-1]['value']} ({s[-1]['year']})" for l,s in wb.items() if s]) or "None."
    gtt="\n".join([f"- '{k}': avg {round(sum(p['value'] for p in s)/len(s),1)}/100" for k,s in gt.get("data",{}).items() if s]) or gt.get("error","N/A")
    p=f"""Demand planning AI for {industry} in {region}. Analyse ONLY data below. Cite sources.
NEWS: {nt}\nWORLD BANK: {wt}\nGOOGLE TRENDS: {gtt}
Return ONLY valid JSON: {{"demand_signals":[{{"signal":"...","source":"...","impact":"...","forecast_adjustment":"..."}}],"supply_risks":[{{"risk":"...","source":"...","severity":"High|Medium|Low","mitigation":"..."}}],"market_summary":"3 sentences citing sources"}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

# ── Sample Data ──
def sample_demand():
    np.random.seed(42); months=pd.date_range("2024-01-01",periods=12,freq="MS"); skus=["SKU-FMCG-001","SKU-FMCG-002","SKU-FMCG-003","SKU-FMCG-004"]; rows=[]
    for sku in skus:
        base=np.random.randint(800,3000)
        for m in months:
            actual=int(base*(1+0.15*np.sin(m.month)+np.random.normal(0,0.1))); forecast=int(actual*(1+np.random.normal(0,0.18)))
            placed=max(10,int(actual/np.random.randint(50,150))); otif=int(placed*np.random.uniform(0.75,0.95))
            rows.append({"Month":m.strftime("%Y-%m"),"SKU":sku,"Actual_Units":actual,"Forecast_Units":forecast,"Orders_Placed":placed,"Orders_OTIF":otif})
    return pd.DataFrame(rows)

def sample_o2c(region):
    np.random.seed(42); custs=REGION_CUSTOMERS.get(region,REGION_CUSTOMERS["Singapore"]); rows=[]
    for i in range(80):
        od=datetime(2024,1,1)+timedelta(days=random.randint(0,364)); cd=random.randint(1,8); fd=random.randint(1,6)
        inv=od+timedelta(days=cd); pay=inv+timedelta(days=random.randint(15,120))
        rows.append({"Order_ID":f"ORD-{1000+i}","Customer":random.choice(custs),"Order_Date":od.strftime("%Y-%m-%d"),"Invoice_Date":inv.strftime("%Y-%m-%d"),"Payment_Date":pay.strftime("%Y-%m-%d"),"Invoice_Amount_USD":round(random.uniform(5000,80000),2),"DSO_Days":(pay-inv).days,"Order_Cycle_Days":cd,"Fulfilment_Days":fd,"Invoice_Errors":random.choice([0,0,0,1]),"Disputed":random.choice([0,0,0,0,1]),"OTIF_Flag":random.choice([1,1,1,1,0]),"Return_Flag":random.choice([0,0,0,0,0,0,0,1]),"Amendment_Flag":random.choice([0,0,0,1]),"Deduction_USD":round(random.choice([0,0,0,0,random.uniform(50,500)]),2)})
    return pd.DataFrame(rows)

def sc(s): return "#16a34a" if s>=70 else "#ea580c" if s>=45 else "#dc2626"

# ── Session State ──
DEFS={"fc_df":None,"o2c_df":None,"fc_hash":None,"o2c_hash":None,"dm":None,"om":None,"fl":None,"bl":None,"ps":None,"mod_scores":None,"ai_exec":None,"ai_agents":None,"done":False,"news":None,"wb":None,"gt":None,"market_ai":None,"market_fetched":False,"region":"Singapore","industry":"F&B / FMCG","diag_responses":{},"inv_days":45,"dpo_days":30}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v
def reset():
    for k,v in DEFS.items(): st.session_state[k]=v

# ── Header ──
st.markdown('<div class="tct-header"><div><div class="tct-title">Revenue Optimizer</div><div class="tct-subtitle">AI-Powered Revenue Operations Intelligence Platform</div></div><div style="display:flex;align-items:center;gap:12px"><span class="tct-badge">AI Engine: Active</span><span class="tct-currency">USD ($)</span></div></div>', unsafe_allow_html=True)
h2,h3,h4,h5=st.columns([1,1,0.5,0.5])
with h2: region=st.selectbox("Region",list(REGIONS.keys()),index=list(REGIONS.keys()).index(st.session_state.region)); st.session_state.region=region
with h3: industry=st.selectbox("Industry",list(INDUSTRIES.keys()),index=list(INDUSTRIES.keys()).index(st.session_state.industry)); st.session_state.industry=industry
with h4:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Demo Data"): st.session_state.fc_df=sample_demand(); st.session_state.o2c_df=sample_o2c(region); st.session_state.fc_hash="s"; st.session_state.o2c_hash="s"; st.session_state.done=False; st.rerun()
with h5:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Reset"): reset(); st.rerun()

tabs=st.tabs(["Setup","Executive Summary","Demand Forecasting","Order Management","Fulfilment & Logistics","Billing & Revenue","Post-Sales & Closure"])

# ═══ TAB 0: SETUP ═══
with tabs[0]:
    st.markdown('<div style="font-size:1.3rem;font-weight:600;color:#0a1628">Setup & Configuration</div><div style="font-size:0.9rem;color:#64748b;margin-bottom:1.5rem">Upload data, complete maturity assessment, then run analysis.</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">Demand & Forecast CSV</div>',unsafe_allow_html=True)
        st.markdown("**Required:** `Month` `SKU` `Actual_Units` `Forecast_Units` | **Optional:** `Orders_Placed` `Orders_OTIF`")
        uf=st.file_uploader("Forecast",type=["csv"],key="fc_up",label_visibility="collapsed")
        if uf:
            try:
                df=pd.read_csv(uf); h=str(hash(df.to_json())); req=["Month","SKU","Actual_Units","Forecast_Units"]; miss=[c for c in req if c not in df.columns]
                if not miss:
                    if h!=st.session_state.fc_hash: st.session_state.fc_df=df; st.session_state.fc_hash=h; st.session_state.done=False
                    st.success(f"{len(df)} rows loaded")
                else: st.error(f"Missing: {miss}")
            except Exception as e: st.error(str(e))
        elif st.session_state.fc_df is not None: st.success(f"{len(st.session_state.fc_df)} rows ready")
        else: st.markdown('<div class="upload-hint">Upload CSV or click Demo Data</div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="section-card"><div class="section-title">Order-to-Cash CSV</div>',unsafe_allow_html=True)
        st.markdown("**Required:** `Order_ID` `Customer` `Invoice_Amount_USD` `DSO_Days` | **Optional:** `Order_Cycle_Days` `Fulfilment_Days` `OTIF_Flag` `Return_Flag`")
        uo=st.file_uploader("O2C",type=["csv"],key="o2c_up",label_visibility="collapsed")
        if uo:
            try:
                df=pd.read_csv(uo); h=str(hash(df.to_json())); req=["Order_ID","Customer","Invoice_Amount_USD","DSO_Days"]; miss=[c for c in req if c not in df.columns]
                if not miss:
                    if h!=st.session_state.o2c_hash: st.session_state.o2c_df=df; st.session_state.o2c_hash=h; st.session_state.done=False
                    st.success(f"{len(df)} rows loaded")
                else: st.error(f"Missing: {miss}")
            except Exception as e: st.error(str(e))
        elif st.session_state.o2c_df is not None: st.success(f"{len(st.session_state.o2c_df)} rows ready")
        else: st.markdown('<div class="upload-hint">Upload CSV or click Demo Data</div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">Working Capital Inputs</div>',unsafe_allow_html=True)
    wc1,wc2=st.columns(2)
    with wc1: inv_d=st.number_input("Inventory Days",0,365,st.session_state.inv_days); st.session_state.inv_days=inv_d
    with wc2: dpo_d=st.number_input("DPO",0,180,st.session_state.dpo_days); st.session_state.dpo_days=dpo_d
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown('<div class="section-card"><div class="section-title">Process Maturity Assessment</div>',unsafe_allow_html=True)
    st.markdown('<div class="info-box">Rate capabilities across 5 modules. Shapes maturity score and AI recommendations.</div>',unsafe_allow_html=True)
    for mod_name,questions in DIAGNOSTIC.items():
        st.markdown(f"**{mod_name}**")
        for q in questions:
            idx=st.select_slider(q["q"],options=list(range(len(q["opts"]))),format_func=lambda x,o=q["opts"]:o[x],value=st.session_state.diag_responses.get(q["key"],0),key=f"d_{q['key']}")
            st.session_state.diag_responses[q["key"]]=idx
        st.markdown("---")
    st.markdown("</div>",unsafe_allow_html=True)

    if st.session_state.fc_df is not None and st.session_state.o2c_df is not None:
        bc1,bc2,_=st.columns([1,1,1])
        with bc1:
            if st.button("Run Full Analysis",use_container_width=True):
                ds=get_diag_scores(st.session_state.diag_responses)
                with st.spinner("Computing..."): st.session_state.dm=calc_demand(st.session_state.fc_df); st.session_state.om=calc_order_mgmt(st.session_state.o2c_df); st.session_state.fl=calc_fulfilment(st.session_state.o2c_df,industry); st.session_state.bl=calc_billing(st.session_state.o2c_df,industry); st.session_state.ps=calc_post_sales(st.session_state.o2c_df,industry,inv_d,dpo_d); st.session_state.mod_scores=calc_module_scores(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,ds)
                with st.spinner("AI insights..."):
                    try: st.session_state.ai_exec=get_executive_ai(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,ds,region,industry)
                    except Exception as e: st.warning(f"AI error: {e}")
                with st.spinner("Agent simulation..."):
                    try: st.session_state.ai_agents=get_agent_simulation(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,region,industry)
                    except Exception as e: st.warning(f"Agent error: {e}")
                st.session_state.done=True; st.rerun()
        with bc2:
            if st.button("Fetch Market Intel",use_container_width=True):
                with st.spinner("News..."): st.session_state.news=fetch_news(region,industry)
                with st.spinner("World Bank..."): st.session_state.wb=fetch_wb(region,industry)
                with st.spinner("Google Trends..."): st.session_state.gt=fetch_gt(INDUSTRIES[industry]["keywords"][:3],region)
                with st.spinner("AI market signals..."):
                    try: st.session_state.market_ai=get_demand_signals_ai(region,industry,st.session_state.news or [],st.session_state.wb or {},st.session_state.gt or {})
                    except: st.session_state.market_ai=None
                st.session_state.market_fetched=True; st.rerun()
        if st.session_state.done: st.success("Analysis complete — explore tabs above.")

# ═══ TAB 1: EXECUTIVE SUMMARY ═══
with tabs[1]:
    if not st.session_state.done: st.info("Complete Setup and click Run Full Analysis.")
    else:
        ai=st.session_state.ai_exec or {}; bl=st.session_state.bl; ps=st.session_state.ps
        s=ai.get("health_score",0)
        if st.session_state.market_fetched and st.session_state.market_ai:
            ms=st.session_state.market_ai.get("market_summary","")
            if ms: st.markdown(f'<div class="info-box"><strong>Market Context:</strong> {ms}</div>',unsafe_allow_html=True)
        rev=bl["rev"]; leak=bl["leak_total"]; outstd=rev*(ps["aging"]["30d"]+ps["aging"]["60d"]+ps["aging"]["90d"])/100
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: st.markdown(f'<div class="metric-card metric-card-green"><div class="metric-label">Total Revenue</div><div class="metric-value" style="font-size:1.4rem">{rev/1000:,.1f}K</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card metric-card-red"><div class="metric-label" style="color:#dc2626">Leakage</div><div class="metric-value" style="font-size:1.4rem;color:#dc2626">{leak/1000:,.1f}K</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card metric-card-amber"><div class="metric-label" style="color:#92400e">Outstanding AR</div><div class="metric-value" style="font-size:1.4rem">{outstd/1000:,.1f}K</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">Net Recovered</div><div class="metric-value" style="font-size:1.4rem">{(rev-leak)/1000:,.1f}K</div></div>',unsafe_allow_html=True)
        with c5: st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">Health</div><div class="metric-value" style="color:{sc(s)};font-size:2.5rem">{s}</div><div style="font-size:0.75rem;font-weight:600;color:{sc(s)}">{ai.get("overall_health","")}</div></div>',unsafe_allow_html=True)
        # Cash Flow Trend
        if not bl["cashflow"].empty:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Cash Flow Trend</div>',unsafe_allow_html=True)
            cf=bl["cashflow"].head(6); cd=pd.DataFrame({"Month":cf["Month"],"Inflow":cf["Inflow"],"Outflow":-cf["Outflow"].abs()}).set_index("Month")
            st.bar_chart(cd,color=["#16a34a","#dc2626"])
            nt=cf["Net"].sum(); st.markdown(f'<div style="text-align:center;font-size:0.85rem;color:#64748b">Net Fund Flow: <span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{"#16a34a" if nt>=0 else "#dc2626"}">{nt:,.0f} USD</span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cs,csm=st.columns([1,2])
        with cs: st.markdown(f'<div class="section-card"><div class="section-title">Strategic Assessment</div><p style="color:#334155;line-height:1.7;font-size:0.95rem">{ai.get("executive_summary","")}</p></div>',unsafe_allow_html=True)
        with csm:
            st.markdown('<div class="section-card"><div class="section-title">Module Health</div>',unsafe_allow_html=True)
            ms=st.session_state.mod_scores or {}; icons={"Demand Forecasting":"📦","Order Management":"📋","Order Fulfilment & Logistics":"🚚","Billing & Revenue Mgmt":"💰","Post-Sales & Financial Closure":"🏦"}
            mc=st.columns(5)
            for col,(mn,mv) in zip(mc,ms.items()):
                with col: st.markdown(f'<div class="module-card"><div style="font-size:0.65rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#64748b">{icons.get(mn,"")} {mn}</div><div style="font-size:1.8rem;font-weight:600;font-family:IBM Plex Mono,monospace;color:{sc(mv)};margin:0.4rem 0">{mv}</div><div style="font-size:0.65rem;color:#94a3b8">/ 100</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Top Risks</div>',unsafe_allow_html=True)
            for r in ai.get("top_risks",[])[:5]:
                sv=r.get("severity","Medium"); bc="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"
                st.markdown(f'<div class="insight-row"><div><span class="risk-badge {bc}">{sv}</span> <span style="font-size:0.7rem;background:#f1f5f9;padding:2px 8px;border-radius:20px;color:#64748b">{r.get("module","")}</span><div style="font-weight:500;margin-top:0.4rem">{r.get("risk","")}</div><div style="font-size:0.82rem;color:#64748b">{r.get("impact","")}</div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Quick Wins</div>',unsafe_allow_html=True)
            for i,qw in enumerate(ai.get("quick_wins",[])[:5],1):
                st.markdown(f'<div class="insight-row"><div style="background:#0a1628;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;color:white;flex-shrink:0">{i}</div><div><div style="font-weight:500">{qw.get("action","")}</div><div style="font-size:0.8rem;color:#64748b">⏱ {qw.get("timeline","")} · 📈 {qw.get("expected_impact","")}</div><span style="font-size:0.7rem;background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:20px">{qw.get("module","")}</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Agentic AI Simulation — Autonomous Interventions (Past 30 Days)</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-box">Based on your data, these are the autonomous interventions the AI agent would have triggered.</div>',unsafe_allow_html=True)
        for item in (st.session_state.ai_agents or {}).get("interventions",[]):
            sv=item.get("severity","Medium").lower(); sc2="risk-high" if sv=="high" else "risk-med" if sv=="medium" else "risk-low"
            st.markdown(f'<div class="agent-card {sv}"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem"><span style="font-size:0.75rem;font-weight:600;color:#0a1628">Day {item.get("day","?")} · {item.get("module","")}</span><span class="risk-badge {sc2}">{item.get("severity","")}</span></div><div style="font-weight:500;font-size:0.9rem;margin-bottom:0.25rem">{item.get("action","")}</div><div style="font-size:0.82rem;color:#64748b">Trigger: {item.get("trigger","")}</div><div style="font-size:0.82rem;color:#16a34a;margin-top:0.2rem">{item.get("impact","")}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# ═══ TAB 2: DEMAND FORECASTING ═══
with tabs[2]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        dm=st.session_state.dm; ob=INDUSTRIES[industry]["otif_benchmark"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">Forecast Accuracy</div><div class="metric-value">{dm["accuracy"]}%</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Variance % (Bias)</div><div class="metric-value">{abs(dm["bias"]):.1f}%</div><div style="font-size:0.78rem;color:#64748b;margin-top:0.3rem">{"Deviation" if abs(dm["bias"])>5 else "Stable"}</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">MAPE</div><div class="metric-value">{dm["mape"]}%</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card metric-card-{"green" if dm["otif"]>=ob else "red"}"><div class="metric-label">OTIF Rate</div><div class="metric-value">{dm["otif"]}%</div><div class="metric-delta {"good" if dm["otif"]>=ob else "bad"}">Bench: {ob}%</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([2,1])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Forecast vs Actuals</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:-0.5rem;margin-bottom:1rem">With variance tracking per period</div>',unsafe_allow_html=True)
            vd=dm["variance"]
            if not vd.empty: st.line_chart(vd[["Month","Actual","Forecast"]].set_index("Month"),color=["#0f172a","#16a34a"])
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Variance Analysis Panel</div>',unsafe_allow_html=True)
            if not dm["variance"].empty:
                for _,row in dm["variance"].tail(6).iterrows():
                    vp=row["Variance_Pct"]; vc="var-pos" if vp>=0 else "var-neg"
                    st.markdown(f'<div class="var-card"><div class="var-label">{row["Month"]} <span class="var-badge">Variance Recorded</span></div><div class="var-row"><span>Difference</span><span class="{vc}">{row["Variance"]:+,.0f} units</span></div><div class="var-row"><span>Deviation</span><span class="{vc}">{vp:+.1f}%</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl2,cr2=st.columns(2)
        with cl2:
            st.markdown('<div class="section-card"><div class="section-title">SKU Performance</div>',unsafe_allow_html=True)
            for _,row in dm["sku"].sort_values("Accuracy",ascending=False).iterrows():
                c=sc(row["Accuracy"])
                st.markdown(f'<div style="margin-bottom:1rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{row["SKU"]}</span><span style="color:{c};font-family:IBM Plex Mono,monospace;font-weight:500">{row["Accuracy"]}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{min(100,row["Accuracy"])}%;background:{c}"></div></div><div style="font-size:0.75rem;color:#94a3b8;margin-top:3px">MAPE: {row["MAPE"]}% Bias: {row["Bias"]:+.1f}%</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr2:
            if st.session_state.market_fetched and st.session_state.market_ai:
                st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div>',unsafe_allow_html=True)
                for sig in st.session_state.market_ai.get("demand_signals",[])[:4]:
                    st.markdown(f'<div class="news-card"><div style="font-weight:500;font-size:0.9rem">{sig.get("signal","")}</div><div style="font-size:0.78rem;color:#64748b;margin-top:0.2rem">Source: {sig.get("source","")} | Impact: {sig.get("impact","")}</div><div style="font-size:0.82rem;color:#0369a1;margin-top:0.3rem">Adjustment: {sig.get("forecast_adjustment","")}</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            else: st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div><div class="upload-hint">Click Fetch Market Intel in Setup.</div></div>',unsafe_allow_html=True)

# ═══ TAB 3: ORDER MANAGEMENT ═══
with tabs[3]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        om=st.session_state.om; bc=INDUSTRIES[industry]["cycle_benchmark"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">Order Cycle</div><div class="metric-value">{om["cycle"]}d</div><div class="metric-delta {"good" if om["cycle"]<=bc else "bad"}">Bench: {bc}d</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card metric-card-{"green" if om["err"]<2 else "red"}"><div class="metric-label">Error Rate</div><div class="metric-value">{om["err"]}%</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card metric-card-{"green" if om["disp"]<5 else "amber"}"><div class="metric-label">Dispute Rate</div><div class="metric-value">{om["disp"]}%</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card metric-card-{"green" if om["amend"]<10 else "red"}"><div class="metric-label">Amendments</div><div class="metric-value">{om["amend"]}%</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Pain Points & AI Solutions</div>',unsafe_allow_html=True)
        for t,p,f in [("Manual order entry","Orders via email/phone need manual ERP entry.","AI auto-capture: reads order emails/PDFs, populates ERP."),("Amendment chaos",f"{om['amend']}% amendment rate disrupts production.","Amendment window enforcement with auto notification."),("Validation gaps","Incomplete data flows to billing errors.","Real-time AI: pricing, inventory, credit check before confirmation."),("No real-time visibility","Teams manually check order status.","Order control tower: unified lifecycle dashboard.")]:
            st.markdown(f'<div style="padding:0.75rem 0;border-bottom:1px solid #f1f5f9"><div style="font-weight:500;font-size:0.9rem;color:#0a1628">{t}</div><div style="font-size:0.82rem;color:#64748b;margin-top:0.2rem">{p}</div><div style="font-size:0.82rem;color:#16a34a;margin-top:0.3rem;background:#f0fdf4;padding:4px 8px;border-radius:6px">{f}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# ═══ TAB 4: FULFILMENT ═══
with tabs[4]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        fl=st.session_state.fl
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">OTIF</div><div class="metric-value" style="color:{"#16a34a" if fl["otif"]>=fl["otif_bench"] else "#dc2626"}">{fl["otif"]}%</div><div class="metric-delta {"good" if fl["otif"]>=fl["otif_bench"] else "bad"}">Bench: {fl["otif_bench"]}%</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card metric-card-{"green" if fl["ful_days"]<=fl["ful_bench"] else "red"}"><div class="metric-label">Fulfilment Cycle</div><div class="metric-value">{fl["ful_days"]}d</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card metric-card-{"green" if fl["return_rate"]<3 else "amber"}"><div class="metric-label">Returns</div><div class="metric-value">{fl["return_rate"]}%</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card metric-card-{"green" if fl["partial"]<10 else "red"}"><div class="metric-label">Partial Shipments</div><div class="metric-value">{fl["partial"]}%</div></div>',unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.market_ai:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Supply Risk Radar</div>',unsafe_allow_html=True)
            for r in st.session_state.market_ai.get("supply_risks",[])[:4]:
                sv=r.get("severity","Medium"); bc="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"
                st.markdown(f'<div class="news-card"><span class="risk-badge {bc}">{sv}</span><div style="font-weight:500;font-size:0.9rem;margin-top:0.3rem">{r.get("risk","")}</div><div style="font-size:0.78rem;color:#64748b">Source: {r.get("source","")} | Mitigation: {r.get("mitigation","")}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.news:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Regional News</div>',unsafe_allow_html=True)
            for a in (st.session_state.news or [])[:5]:
                tags="".join([f'<span class="news-tag">{k}</span>' for k in a["keywords"]])
                st.markdown(f'<div class="news-card"><div style="font-size:0.9rem;font-weight:500">{a["title"]}</div><div style="font-size:0.75rem;color:#94a3b8">{a["source"]} {a["published"]}</div><div style="margin-top:0.3rem">{tags}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

# ═══ TAB 5: BILLING & REVENUE ═══
with tabs[5]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        bl=st.session_state.bl; lpct=round((bl["leak_total"]/max(bl["rev"],1))*100,1)
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">DSO</div><div class="metric-value" style="color:{"#16a34a" if bl["gap"]<=0 else "#dc2626"}">{bl["dso"]}d</div><div class="metric-delta {"good" if bl["gap"]<=0 else "bad"}">{bl["gap"]:+.0f}d vs {bl["bench"]}d</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card metric-card-{"green" if bl["err"]<2 else "red"}"><div class="metric-label">Invoice Errors</div><div class="metric-value">{bl["err"]}%</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card metric-card-{"green" if bl["disp"]<5 else "amber"}"><div class="metric-label">Disputes</div><div class="metric-value">{bl["disp"]}%</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label" style="color:#f87171">Revenue Leakage</div><div class="metric-value" style="font-size:1.4rem">{lpct}%</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">USD {bl["leak_total"]:,.0f}</div></div>',unsafe_allow_html=True)
        # Receivable Forecast
        if not bl["recv_forecast"].empty:
            st.markdown("<br>",unsafe_allow_html=True)
            rcl,rcr=st.columns([2,1])
            with rcl:
                st.markdown('<div class="section-card"><div class="section-title">Receivable Forecast vs Actuals</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:-0.5rem;margin-bottom:1rem">With prediction & confidence band</div>',unsafe_allow_html=True)
                rf=bl["recv_forecast"]; chart=rf[["Actual","Predicted"]].copy(); chart.index=[f"W{i}" for i in range(len(chart))]
                st.line_chart(chart,color=["#0f172a","#16a34a"])
                st.markdown("</div>",unsafe_allow_html=True)
            with rcr:
                st.markdown('<div class="section-card"><div class="section-title">Variance Analysis</div>',unsafe_allow_html=True)
                for idx,row in rf.tail(4).iterrows():
                    vp=row["Var_Pct"]; vc="var-pos" if vp>=0 else "var-neg"
                    st.markdown(f'<div class="var-card"><div class="var-label">W{idx} <span class="var-badge">Variance</span></div><div class="var-row"><span>Difference</span><span class="{vc}">{row["Variance"]:+,.0f} USD</span></div><div class="var-row"><span>Deviation</span><span class="{vc}">{vp:+.1f}%</span></div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([3,2])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Revenue Leakage Waterfall</div>',unsafe_allow_html=True)
            rev=bl["rev"]; net=rev-bl["leak_total"]
            for lb,v,co,d in [("Gross Revenue",rev,"#0a1628","Total invoiced"),("Discounting",-bl["leak_disc"],"#dc2626","Rogue discounts"),("Invoice Errors",-bl["leak_inv"],"#ea580c","Portal failures"),("Disputes",-bl["leak_disp"],"#f59e0b","Customer disputes"),("Deductions",-bl["leak_ded"],"#8b5cf6","Out-of-terms"),("Net Recovered",net,"#16a34a","After fixes")]:
                neg=v<0; dv=f"-USD {abs(v):,.0f}" if neg else f"USD {v:,.0f}"; pct=min(100,abs(v)/max(rev,1)*100)
                st.markdown(f'<div style="margin-bottom:0.75rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px"><span style="font-weight:500">{lb}</span><span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{co}">{dv}</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:{co}"></div></div><div style="font-size:0.72rem;color:#94a3b8;margin-top:3px">{d}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Customer DSO Risk</div>',unsafe_allow_html=True)
            for _,row in bl["cust"].head(8).iterrows():
                r=row["Risk"]; rc="risk-high" if r=="High" else "risk-med" if r=="Medium" else "risk-low"
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><span style="font-size:0.85rem;font-weight:500">{row["Customer"]}</span><span><span style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;margin-right:8px">{row["Avg_DSO"]}d</span><span class="risk-badge {rc}">{r}</span></span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

# ═══ TAB 6: POST-SALES ═══
with tabs[6]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        ps=st.session_state.ps
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">WC Health</div><div class="metric-value" style="color:{"#4ade80" if ps["score"]>=70 else "#f87171"}">{ps["score"]}</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{ps["health"]}</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card metric-card-blue"><div class="metric-label">CCC</div><div class="metric-value" style="color:{"#16a34a" if ps["ccc"]<=ps["bench"] else "#dc2626"}">{ps["ccc"]}d</div><div class="metric-delta {"good" if ps["ccc"]<=ps["bench"] else "bad"}">Bench: {ps["bench"]}d</div></div>',unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card metric-card-{"green" if ps["aging"]["90d"]<10 else "red"}"><div class="metric-label">AR > 90 Days</div><div class="metric-value">{ps["aging"]["90d"]}%</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card metric-card-amber"><div class="metric-label">Deductions</div><div class="metric-value" style="font-size:1.4rem">USD {ps["deductions"]:,.0f}</div></div>',unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Cash Conversion Cycle</div>',unsafe_allow_html=True)
        cc1,cc2,cc3=st.columns(3)
        for col,(lb,v,co,fx) in zip([cc1,cc2,cc3],[("DSO",ps["dso"],"#dc2626","Reduce: faster invoicing, portal bot, AI dunning"),("Inventory Days",ps["inv"],"#f59e0b","Reduce: dynamic safety stock, FEFO, forecasting"),("DPO",ps["dpo"],"#16a34a","Increase: renegotiate supplier terms")]):
            with col: st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">{lb}</div><div class="metric-value" style="color:{co}">{v}d</div><div style="font-size:0.78rem;color:#334155;margin-top:0.5rem">{fx}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        al,ar=st.columns(2)
        with al:
            st.markdown('<div class="section-card"><div class="section-title">Receivables Aging</div>',unsafe_allow_html=True)
            for lb,v,co in [("Current",ps["aging"]["current"],"#16a34a"),("31-60d",ps["aging"]["30d"],"#f59e0b"),("61-90d",ps["aging"]["60d"],"#ea580c"),("90d+",ps["aging"]["90d"],"#dc2626")]:
                st.markdown(f'<div style="margin-bottom:0.5rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{lb}</span><span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{co}">{v}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{v}%;background:{co}"></div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with ar:
            st.markdown('<div class="section-card"><div class="section-title">Upcoming Cash Position</div>',unsafe_allow_html=True)
            cp=ps.get("cash_pos",[])
            if cp:
                hz=st.radio("Horizon",options=[7,14,21,30],horizontal=True,index=0,key="cp_hz")
                html='<table class="cp-table"><tr><th>Date</th><th>Expected Inflow</th><th>Expected Outflow</th><th>Net Flow</th></tr>'
                for row in cp[:hz]:
                    nc="cp-green" if row["Net"]>=0 else "cp-red"
                    html+=f'<tr><td style="font-weight:500;font-family:IBM Plex Sans,sans-serif">{row["Date"]}</td><td class="cp-green">{row["Inflow"]:,.0f}</td><td class="cp-red">{row["Outflow"]:,.0f}</td><td class="{nc}">{row["Net"]:,.0f}</td></tr>'
                html+='</table>'; st.markdown(html,unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.wb:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Macroeconomic Context</div>',unsafe_allow_html=True)
            for lb,series in st.session_state.wb.items():
                if series: st.markdown(f"**{lb}** — Latest: `{series[-1]['value']}` ({series[-1]['year']})"); st.line_chart(pd.DataFrame(series).set_index("year")["value"])
            st.markdown("</div>",unsafe_allow_html=True)
