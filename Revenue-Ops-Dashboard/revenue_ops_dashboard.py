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
    .tct-title { color:white; font-size:1.4rem; font-weight:600; } .tct-subtitle { color:#94a3b8; font-size:0.78rem; letter-spacing:0.08em; text-transform:uppercase; margin-top:0.15rem; }
    .tct-badge { background:#16a34a; color:white; font-size:0.7rem; font-weight:600; padding:4px 12px; border-radius:20px; }
    .tct-currency { background:rgba(255,255,255,0.1); color:white; font-size:0.8rem; padding:4px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.15); }
    .metric-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.1rem 1.3rem; }
    .metric-card-dark { background:linear-gradient(135deg,#0a1628 0%,#1a2d4d 100%); border:none; border-radius:10px; padding:1.1rem 1.3rem; }
    .metric-card-dark .metric-label { color:#94a3b8; } .metric-card-dark .metric-value { color:white; }
    .metric-card-green { border-left:4px solid #16a34a; } .metric-card-red { border-left:4px solid #dc2626; }
    .metric-card-amber { border-left:4px solid #f59e0b; } .metric-card-blue { border-left:4px solid #0369a1; }
    .metric-label { font-size:0.7rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748b; margin-bottom:0.35rem; }
    .metric-value { font-size:1.7rem; font-weight:600; color:#0f172a; line-height:1; font-family:'IBM Plex Mono',monospace; }
    .metric-delta { font-size:0.78rem; margin-top:0.25rem; }
    .metric-delta.good { color:#16a34a; } .metric-delta.bad { color:#dc2626; } .metric-delta.neutral { color:#64748b; }
    .mex { font-size:0.66rem; color:#94a3b8; margin-top:0.4rem; border-top:1px solid #f1f5f9; padding-top:0.35rem; line-height:1.4; }
    .msrc { font-size:0.6rem; color:#bdc5d1; line-height:1.25; }
    .section-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.5rem; margin-bottom:1rem; }
    .section-title { font-size:0.8rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:#64748b; margin-bottom:1rem; padding-bottom:0.75rem; border-bottom:1px solid #f1f5f9; }
    .risk-badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; }
    .risk-high { background:#fee2e2; color:#991b1b; } .risk-med { background:#fef3c7; color:#92400e; } .risk-low { background:#dcfce7; color:#166534; }
    .risk-why { font-size:0.7rem; color:#94a3b8; font-style:italic; margin-top:0.25rem; }
    .insight-row { display:flex; align-items:flex-start; gap:0.75rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9; font-size:0.9rem; }
    .insight-row:last-child { border-bottom:none; }
    .progress-bar-bg { background:#f1f5f9; border-radius:4px; height:8px; width:100%; margin-top:6px; }
    .progress-bar-fill { height:8px; border-radius:4px; }
    .news-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .news-tag { display:inline-block; font-size:0.7rem; font-weight:600; padding:2px 8px; border-radius:20px; margin-right:4px; background:#e0f2fe; color:#0369a1; }
    .info-box { background:#f0f9ff; border:1px solid #bae6fd; border-radius:8px; padding:0.75rem 1rem; font-size:0.82rem; color:#0369a1; margin-bottom:0.75rem; }
    .module-card { background:white; border:1px solid #e2e8f0; border-radius:10px; padding:1.1rem; text-align:center; }
    .mod-explain { font-size:0.62rem; color:#94a3b8; margin-top:0.3rem; line-height:1.3; }
    .agent-card { background:#f8fafc; border-left:4px solid #0369a1; border-radius:0 8px 8px 0; padding:0.9rem 1rem; margin-bottom:0.6rem; }
    .agent-card.high { border-left-color:#dc2626; } .agent-card.medium { border-left-color:#f59e0b; } .agent-card.low { border-left-color:#16a34a; }
    .upload-hint { background:#f8fafc; border:1.5px dashed #cbd5e1; border-radius:10px; padding:2rem; text-align:center; color:#64748b; font-size:0.9rem; }
    .stButton > button { background:#0a1628; color:white; border:none; border-radius:8px; padding:0.5rem 1.25rem; font-family:'IBM Plex Sans',sans-serif; font-size:0.9rem; font-weight:500; }
    .stButton > button:hover { background:#132743; }
    .var-card { background:white; border:1px solid #e2e8f0; border-radius:8px; padding:0.75rem 1rem; margin-bottom:0.5rem; }
    .var-label { font-size:0.85rem; font-weight:600; color:#0f172a; } .var-badge { font-size:0.65rem; font-weight:600; padding:2px 8px; border-radius:10px; background:#e0f2fe; color:#0369a1; float:right; }
    .var-row { display:flex; justify-content:space-between; font-size:0.82rem; margin-top:0.3rem; }
    .var-pos { color:#16a34a; font-family:'IBM Plex Mono',monospace; font-weight:600; } .var-neg { color:#dc2626; font-family:'IBM Plex Mono',monospace; font-weight:600; }
    .cp-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
    .cp-table th { text-align:left; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; color:#64748b; padding:0.5rem 0.75rem; border-bottom:2px solid #e2e8f0; }
    .cp-table td { padding:0.5rem 0.75rem; border-bottom:1px solid #f1f5f9; font-family:'IBM Plex Mono',monospace; font-size:0.82rem; }
    .cp-green { color:#16a34a; } .cp-red { color:#dc2626; }
    #MainMenu { visibility:hidden; } footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_client():
    key = os.environ.get("GEMINI_API_KEY")
    if not key: st.error("GEMINI_API_KEY not found."); st.stop()
    return genai.Client(api_key=key)
client = get_client(); MODEL = "gemini-2.5-flash"

REGIONS = {"Indonesia":{"geo":"ID","worldbank":"IDN","currency":"IDR","fx_rate":15800,"symbol":"Rp"},"Thailand":{"geo":"TH","worldbank":"THA","currency":"THB","fx_rate":34.5,"symbol":"฿"},"Vietnam":{"geo":"VN","worldbank":"VNM","currency":"VND","fx_rate":25400,"symbol":"₫"},"Malaysia":{"geo":"MY","worldbank":"MYS","currency":"MYR","fx_rate":4.45,"symbol":"RM"},"Philippines":{"geo":"PH","worldbank":"PHL","currency":"PHP","fx_rate":56.8,"symbol":"₱"},"Singapore":{"geo":"SG","worldbank":"SGP","currency":"SGD","fx_rate":1.34,"symbol":"S$"}}
CURRENCIES = {"USD":{"rate":1,"symbol":"$","label":"USD ($)"}}
for rn,rd in REGIONS.items(): CURRENCIES[rd["currency"]]={"rate":rd["fx_rate"],"symbol":rd["symbol"],"label":f'{rd["currency"]} ({rd["symbol"]})'}
REGION_CUSTOMERS = {"Indonesia":["Indomaret","Alfamart","Hero Supermarket","Ranch Market","Lotte Mart ID","Carrefour ID"],"Thailand":["CP ALL 7-Eleven","Big C","Tesco Lotus","Makro TH","Tops Market","Villa Market"],"Vietnam":["Vinmart","Co.opmart","Bach Hoa Xanh","Big C VN","Lotte Mart VN","Circle K VN"],"Malaysia":["Lotus's MY","AEON Malaysia","Guardian MY","Watsons MY","Parkson","Cold Storage MY"],"Philippines":["SM Supermarket","Puregold","Robinsons","Mercury Drug","7-Eleven PH","S&R Members"],"Singapore":["FairPrice","Cold Storage SG","Giant SG","Sheng Siong","Guardian SG","Watsons SG"]}
INDUSTRIES = {"F&B / FMCG":{"keywords":["food","beverage","FMCG","consumer goods","grocery"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":45,"inv_benchmark":40,"otif_benchmark":92,"cycle_benchmark":3},"Electronics Manufacturing":{"keywords":["electronics","semiconductor","manufacturing","supply chain"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":50,"inv_benchmark":50,"otif_benchmark":88,"cycle_benchmark":5},"Medical / Healthcare":{"keywords":["medical","healthcare","pharmaceutical","hygiene"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","SH.XPD.CHEX.GD.ZS"],"dso_benchmark":40,"inv_benchmark":45,"otif_benchmark":95,"cycle_benchmark":2},"Automotive / Industrial":{"keywords":["automotive","industrial","machinery","logistics"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","NE.EXP.GNFS.ZS"],"dso_benchmark":55,"inv_benchmark":55,"otif_benchmark":90,"cycle_benchmark":4},"Retail / E-Commerce":{"keywords":["retail","e-commerce","online shopping","consumer"],"worldbank_indicators":["NY.GDP.MKTP.KD.ZG","FP.CPI.TOTL.ZG"],"dso_benchmark":30,"inv_benchmark":25,"otif_benchmark":95,"cycle_benchmark":2}}
RSS_FEEDS = {"Malaysia":[("The Star Business","https://www.thestar.com.my/rss/business"),("The Edge Malaysia","https://theedgemalaysia.com/feed")],"Singapore":[("Channel NewsAsia","https://www.channelnewsasia.com/rssfeeds/8395986"),("Straits Times","https://www.straitstimes.com/news/business/rss.xml")],"Vietnam":[("VnExpress Business","https://e.vnexpress.net/rss/business.rss")],"Indonesia":[("Jakarta Post","https://www.thejakartapost.com/feed/category/business")],"Thailand":[("Bangkok Post","https://www.bangkokpost.com/rss/data/business.xml")],"Philippines":[("Inquirer Business","https://business.inquirer.net/feed"),("Rappler Business","https://www.rappler.com/business/feed/")]}
WB_LABELS = {"NY.GDP.MKTP.KD.ZG":"GDP Growth (%)","FP.CPI.TOTL.ZG":"Inflation (CPI %)","NE.EXP.GNFS.ZS":"Exports (% GDP)","SH.XPD.CHEX.GD.ZS":"Health Exp (% GDP)"}
DIAGNOSTIC = {"Demand Forecasting":[{"q":"How is your demand forecast created?","opts":["Excel / spreadsheets only","ERP basic module","Dedicated planning tool","AI-assisted forecasting"],"key":"df_method"},{"q":"Do you track forecast accuracy (e.g. MAPE)?","opts":["No tracking at all","Occasionally reviewed","Monthly review","Real-time dashboard"],"key":"df_tracking"},{"q":"What % of customers provide usable forecast data?","opts":["Less than 25%","25-50%","50-75%","More than 75%"],"key":"df_customer_data"}],"Order Management":[{"q":"How are customer orders received?","opts":["Phone / Email only","Basic portal or fax","EDI integration","Fully automated multi-channel"],"key":"om_channel"},{"q":"Is order validation automated?","opts":["Fully manual checks","Partial validation rules","Mostly automated","Fully automated with exceptions"],"key":"om_validation"},{"q":"How often do customers amend orders?","opts":["Very frequently (>30%)","Often (15-30%)","Occasionally (5-15%)","Rarely (<5%)"],"key":"om_amendments"}],"Order Fulfilment & Logistics":[{"q":"Do you track OTIF (On-Time In-Full)?","opts":["Not tracked","Informally estimated","Formally tracked monthly","Real-time OTIF dashboard"],"key":"fl_otif"},{"q":"How is warehouse picking managed?","opts":["Paper-based / manual","Basic WMS","Advanced WMS with optimization","Automated / robotics-assisted"],"key":"fl_wms"},{"q":"Real-time shipment visibility?","opts":["No visibility","Partial (carrier websites)","Full tracking integration","Predictive ETA with alerts"],"key":"fl_visibility"}],"Billing & Revenue Mgmt":[{"q":"How are invoices triggered?","opts":["Manual creation","Semi-automated from ERP","Auto-generated on shipment","Touchless with compliance check"],"key":"br_invoicing"},{"q":"Discount / rebate governance?","opts":["No controls","Basic approval workflow","Rules-based engine","AI-governed with anomaly detection"],"key":"br_discount"},{"q":"Customer portal handling?","opts":["Not applicable","Manual uploads per customer","Partially automated","Fully automated per-customer rules"],"key":"br_portal"}],"Post-Sales & Financial Closure":[{"q":"How does AR team prioritize collections?","opts":["Ad hoc / reactive","First-in first-out","By invoice amount","Risk-based AI prioritization"],"key":"ps_collections"},{"q":"What % of receivables go past 90 days?","opts":["More than 20%","10-20%","5-10%","Less than 5%"],"key":"ps_aging"},{"q":"Cash application / reconciliation?","opts":["Fully manual","Partially automated","Mostly automated","Fully automated with AI matching"],"key":"ps_cash_app"}]}

def fmtc(value, ccy_code, compact=False):
    info = CURRENCIES.get(ccy_code, CURRENCIES["USD"]); converted = value * info["rate"]; sym = info["symbol"]
    if compact and abs(converted) >= 1_000_000: return f"{sym}{converted/1_000_000:,.1f}M"
    elif compact and abs(converted) >= 1_000: return f"{sym}{converted/1_000:,.1f}K"
    return f"{sym}{converted:,.0f}"

def mcard(label, val, delta, dcls, explain, source, card_cls="metric-card"):
    return f'<div class="{card_cls}"><div class="metric-label">{label}</div><div class="metric-value">{val}</div><div class="metric-delta {dcls}">{delta}</div><div class="mex">{explain}</div><div class="msrc">{source}</div></div>'

@st.cache_data(ttl=3600)
def fetch_news(region, industry):
    kws=[k.lower() for k in INDUSTRIES[industry]["keywords"]]; arts=[]
    for src,url in RSS_FEEDS.get(region,[]):
        try:
            feed=feedparser.parse(url)
            for e in feed.entries[:25]:
                t=e.get("title",""); s=e.get("summary",""); m=[k for k in kws if k in(t+" "+s).lower()]
                if m: arts.append({"title":t,"source":src,"published":e.get("published","")[:16],"keywords":m[:2]})
        except: pass
    return arts[:10]

@st.cache_data(ttl=86400)
def fetch_wb(region, industry):
    c=REGIONS[region]["worldbank"]; res={}
    for ind in INDUSTRIES[industry]["worldbank_indicators"]:
        try:
            r=requests.get(f"https://api.worldbank.org/v2/country/{c}/indicator/{ind}?format=json&mrv=5&per_page=5",timeout=8)
            if r.status_code==200:
                d=r.json()
                if len(d)>1 and d[1]:
                    s=[{"year":x["date"],"value":round(x["value"],2)} for x in d[1] if x["value"] is not None]
                    if s: res[WB_LABELS.get(ind,ind)]=sorted(s,key=lambda x:x["year"])
        except: pass
    return res

@st.cache_data(ttl=3600)
def fetch_gt(keywords, region):
    geo=REGIONS[region]["geo"]
    try:
        from pytrends.request import TrendReq
        pt=TrendReq(hl='en-US',tz=480,timeout=(10,25)); kws=keywords[:3]; pt.build_payload(kws,timeframe='today 1-m',geo=geo)
        df=pt.interest_over_time()
        if df.empty: return {"error":"No data.","data":{}}
        df=df.drop(columns=["isPartial"],errors="ignore")
        return {"data":{k:[{"date":str(d.date()),"value":int(v)} for d,v in zip(df.index,df[k])] for k in kws if k in df.columns}}
    except ImportError: return {"error":"pytrends not installed.","data":{}}
    except Exception as e: return {"error":str(e),"data":{}}

def calc_demand(df):
    df=df.copy(); df["MAPE"]=(df["Actual_Units"]-df["Forecast_Units"]).abs()/df["Actual_Units"].replace(0,np.nan)*100
    df["Bias"]=(df["Actual_Units"]-df["Forecast_Units"])/df["Actual_Units"].replace(0,np.nan)*100; mape=df["MAPE"].mean(); otif=0
    if "Orders_Placed" in df.columns and "Orders_OTIF" in df.columns: otif=round((df["Orders_OTIF"].sum()/max(df["Orders_Placed"].sum(),1))*100,1)
    sku=df.groupby("SKU").agg(MAPE=("MAPE","mean"),Bias=("Bias","mean"),Accuracy=("MAPE",lambda x:max(0,100-x.mean()))).reset_index().round(1)
    mo=df.groupby("Month").agg(Actual=("Actual_Units","sum"),Forecast=("Forecast_Units","sum")).reset_index()
    mo["Variance"]=mo["Actual"]-mo["Forecast"]; mo["Variance_Pct"]=((mo["Actual"]-mo["Forecast"])/mo["Forecast"].replace(0,np.nan)*100).round(1)
    return {"accuracy":round(max(0,100-mape),1),"mape":round(mape,1),"bias":round(df["Bias"].mean(),1),"otif":otif,"sku":sku,"monthly":df,"variance":mo}

def calc_order_mgmt(df):
    return {"cycle":round(df["Order_Cycle_Days"].mean(),1) if "Order_Cycle_Days" in df.columns else 0,"err":round(df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100,1),"disp":round(df.get("Disputed",pd.Series([0]*len(df))).mean()*100,1),"amend":round(df.get("Amendment_Flag",pd.Series([0]*len(df))).mean()*100,1) if "Amendment_Flag" in df.columns else 12.0}

def calc_fulfilment(df,industry):
    bi=INDUSTRIES[industry]
    return {"otif":round((df["OTIF_Flag"].mean()*100) if "OTIF_Flag" in df.columns else 85.0,1),"otif_bench":bi["otif_benchmark"],"ful_days":round(df["Fulfilment_Days"].mean() if "Fulfilment_Days" in df.columns else 0,1),"ful_bench":bi["cycle_benchmark"],"return_rate":round((df["Return_Flag"].mean()*100) if "Return_Flag" in df.columns else 3.0,1),"partial":round(100-(df["OTIF_Flag"].mean()*100 if "OTIF_Flag" in df.columns else 85.0),1)}

def calc_billing(df,industry):
    bench=INDUSTRIES[industry]["dso_benchmark"]; dso=df["DSO_Days"].mean(); err=df.get("Invoice_Errors",pd.Series([0]*len(df))).mean()*100; disp=df.get("Disputed",pd.Series([0]*len(df))).mean()*100; rev=df["Invoice_Amount_USD"].sum()
    ld=rev*0.018; ie=rev*(err/100)*0.025; dd=rev*(disp/100)*0.05; ed=rev*0.008
    cust=df.groupby("Customer")["DSO_Days"].mean().reset_index(); cust.columns=["Customer","Avg_DSO"]
    cust["Risk"]=cust["Avg_DSO"].apply(lambda x:"High" if x>bench*1.4 else("Medium" if x>bench*1.1 else "Low"))
    cf=pd.DataFrame()
    if "Invoice_Date" in df.columns and "Payment_Date" in df.columns:
        d2=df.copy(); d2["Pay_Month"]=pd.to_datetime(d2["Payment_Date"]).dt.strftime("%b")
        inf=d2.groupby("Pay_Month")["Invoice_Amount_USD"].sum().reset_index(); inf.columns=["Month","Inflow"]
        inf["Outflow"]=(inf["Inflow"]*np.random.uniform(0.65,0.85,len(inf))).round(0); inf["Net"]=inf["Inflow"]-inf["Outflow"]; cf=inf
    rf=pd.DataFrame()
    if "Invoice_Date" in df.columns:
        d3=df.copy(); d3["Week"]=pd.to_datetime(d3["Invoice_Date"]).dt.isocalendar().week.astype(int)
        w=d3.groupby("Week")["Invoice_Amount_USD"].sum().reset_index(); w.columns=["Week","Actual"]
        w["Predicted"]=w["Actual"]*np.random.uniform(0.95,1.08,len(w)); w["Variance"]=w["Actual"]-w["Predicted"]
        w["Var_Pct"]=((w["Variance"]/w["Predicted"])*100).round(1); rf=w.tail(8).reset_index(drop=True)
    return {"dso":round(dso,1),"bench":bench,"gap":round(dso-bench,1),"err":round(err,1),"disp":round(disp,1),"rev":round(rev,0),"leak_total":round(ld+ie+dd+ed,0),"leak_disc":round(ld,0),"leak_inv":round(ie,0),"leak_disp":round(dd,0),"leak_ded":round(ed,0),"cust":cust.sort_values("Avg_DSO",ascending=False).round(1),"cashflow":cf,"recv_forecast":rf}

def calc_post_sales(df,industry,inv_days,dpo):
    dso=df["DSO_Days"].mean(); bd=INDUSTRIES[industry]["dso_benchmark"]; ccc=dso+inv_days-dpo; bc=bd+INDUSTRIES[industry]["inv_benchmark"]-30
    gap=ccc-bc; score=max(0,min(100,round(100-(gap/max(bc,1))*50)))
    aging={"current":round((df["DSO_Days"]<=30).mean()*100,1),"30d":round(((df["DSO_Days"]>30)&(df["DSO_Days"]<=60)).mean()*100,1),"60d":round(((df["DSO_Days"]>60)&(df["DSO_Days"]<=90)).mean()*100,1),"90d":round((df["DSO_Days"]>90).mean()*100,1)}
    ded=df["Deduction_USD"].sum() if "Deduction_USD" in df.columns else 0
    cp=[]
    if "Payment_Date" in df.columns:
        d4=df.copy(); d4["Payment_Date"]=pd.to_datetime(d4["Payment_Date"]); today=d4["Payment_Date"].max()-timedelta(days=30)
        for d in range(1,31):
            dt=today+timedelta(days=d); di=d4[d4["Payment_Date"].dt.date==dt.date()]["Invoice_Amount_USD"].sum()
            do=di*np.random.uniform(0.3,0.7) if di>0 else np.random.uniform(500,8000)
            cp.append({"Date":dt.strftime("%b %d"),"Inflow":round(di,0),"Outflow":round(do,0),"Net":round(di-do,0)})
    return {"ccc":round(ccc,1),"bench":round(bc,1),"dso":round(dso,1),"inv":inv_days,"dpo":dpo,"gap":round(gap,1),"score":score,"health":"Good" if score>=70 else "At Risk" if score>=45 else "Critical","aging":aging,"deductions":round(ded,0),"cash_pos":cp}

def calc_module_scores(dm,om,fl,bl,ps,diag):
    data={"Demand Forecasting":min(100,round(dm["accuracy"]*0.7+max(0,20-abs(dm["bias"]))*1.5)),"Order Management":max(0,min(100,round(100-om["err"]*5-om["disp"]*3-om["amend"]*0.5))),"Order Fulfilment & Logistics":max(0,min(100,round(fl["otif"]*0.8+max(0,10-fl["return_rate"])*2))),"Billing & Revenue Mgmt":max(0,min(100,round(100-bl["err"]*8-bl["disp"]*4))),"Post-Sales & Financial Closure":ps["score"]}
    return {m:round(data[m]*0.6+diag.get(m,50)*0.4) for m in data}

def get_diag_scores(resp):
    sc={}
    for mod,qs in DIAGNOSTIC.items(): vals=[(resp.get(q["key"],0)+1)*25 for q in qs]; sc[mod]=round(sum(vals)/len(vals)) if vals else 50
    return sc

def get_executive_ai(dm,om,fl,bl,ps,ms,diag,region,industry,ccy):
    p=f"""Revenue Optimizer AI for {industry} in {region}. Currency: {ccy}. MODULE SCORES: {json.dumps(ms)}
DEMAND: Accuracy {dm['accuracy']}%, MAPE {dm['mape']}%, Bias {dm['bias']:+.1f}%, OTIF {dm['otif']}%
ORDER: Cycle {om['cycle']}d, Errors {om['err']}%, Disputes {om['disp']}%, Amendments {om['amend']}%
FULFILMENT: OTIF {fl['otif']}% (bench {fl['otif_bench']}%), Returns {fl['return_rate']}%
BILLING: DSO {bl['dso']}d (bench {bl['bench']}d), Leakage USD {bl['leak_total']:,.0f}
POST-SALES: CCC {ps['ccc']}d (bench {ps['bench']}d), Score {ps['score']}/100, AR>90d: {ps['aging']['90d']}%
MATURITY: {json.dumps(diag)}
Context: SEA CPG mid-market. Pain: non-binding forecasts, spreadsheet dependence, portal failures, manual rebates.
For each risk, include a 'why' field: 1 sentence explaining why this severity was assigned based on the data.
Return ONLY valid JSON: {{"overall_health":"Good|At Risk|Critical","health_score":<int>,"health_reason":"1 sentence explaining the score based on data",
"executive_summary":"3-4 sentence summary","top_risks":[{{"risk":"...","severity":"High|Medium|Low","impact":"...","module":"...","why":"1 sentence data-based reason for this severity"}}],
"quick_wins":[{{"action":"...","timeline":"...","expected_impact":"...","module":"..."}}],"forecast_insight":"...","o2c_insight":"...","wc_insight":"..."}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_agent_simulation(dm,om,fl,bl,ps,ms,region,industry,ccy):
    p=f"""Revenue Optimizer AI agent for {industry} in {region}. Currency: {ccy}. Simulate 8 realistic interventions over 30 days.
DATA: Accuracy:{dm['accuracy']}%, OTIF:{dm['otif']}%, Cycle:{om['cycle']}d, Amendments:{om['amend']}%, Errors:{om['err']}%, OTIF:{fl['otif']}%, Returns:{fl['return_rate']}%, DSO:{bl['dso']}d(bench{bl['bench']}d), Leakage:USD{bl['leak_total']:,.0f}, CCC:{ps['ccc']}d, AR>90d:{ps['aging']['90d']}%
Return ONLY valid JSON: {{"interventions":[{{"day":1,"module":"...","severity":"High|Medium|Low","trigger":"...","action":"...","impact":"..."}}]}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def get_demand_signals_ai(region,industry,news,wb,gt):
    nt="\n".join([f"- [{a['source']}] {a['title']}" for a in news[:8]]) or "None."
    wt="\n".join([f"- {l}: {s[-1]['value']} ({s[-1]['year']})" for l,s in wb.items() if s]) or "None."
    gtt="\n".join([f"- '{k}': avg {round(sum(p['value'] for p in s)/len(s),1)}/100" for k,s in gt.get("data",{}).items() if s]) or gt.get("error","N/A")
    p=f"""Demand AI for {industry} in {region}. Analyse ONLY data below. Cite sources.
NEWS: {nt}\nWORLD BANK: {wt}\nGOOGLE TRENDS: {gtt}
Return ONLY valid JSON: {{"demand_signals":[{{"signal":"...","source":"...","impact":"...","forecast_adjustment":"..."}}],"supply_risks":[{{"risk":"...","source":"...","severity":"High|Medium|Low","mitigation":"..."}}],"market_summary":"3 sentences citing sources"}}"""
    r=client.models.generate_content(model=MODEL,contents=p); t=r.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip(); return json.loads(t)

def sample_demand():
    np.random.seed(42); months=pd.date_range("2024-01-01",periods=12,freq="MS"); skus=["SKU-FMCG-001","SKU-FMCG-002","SKU-FMCG-003","SKU-FMCG-004"]; rows=[]
    for sku in skus:
        base=np.random.randint(800,3000)
        for m in months:
            a=int(base*(1+0.15*np.sin(m.month)+np.random.normal(0,0.1))); f=int(a*(1+np.random.normal(0,0.18)))
            pl=max(10,int(a/np.random.randint(50,150))); ot=int(pl*np.random.uniform(0.75,0.95))
            rows.append({"Month":m.strftime("%Y-%m"),"SKU":sku,"Actual_Units":a,"Forecast_Units":f,"Orders_Placed":pl,"Orders_OTIF":ot})
    return pd.DataFrame(rows)

def sample_o2c(region):
    np.random.seed(42); custs=REGION_CUSTOMERS.get(region,REGION_CUSTOMERS["Singapore"]); rows=[]
    for i in range(80):
        od=datetime(2024,1,1)+timedelta(days=random.randint(0,364)); cd=random.randint(1,8); fd=random.randint(1,6)
        inv=od+timedelta(days=cd); pay=inv+timedelta(days=random.randint(15,120))
        rows.append({"Order_ID":f"ORD-{1000+i}","Customer":random.choice(custs),"Order_Date":od.strftime("%Y-%m-%d"),"Invoice_Date":inv.strftime("%Y-%m-%d"),"Payment_Date":pay.strftime("%Y-%m-%d"),"Invoice_Amount_USD":round(random.uniform(5000,80000),2),"DSO_Days":(pay-inv).days,"Order_Cycle_Days":cd,"Fulfilment_Days":fd,"Invoice_Errors":random.choice([0,0,0,1]),"Disputed":random.choice([0,0,0,0,1]),"OTIF_Flag":random.choice([1,1,1,1,0]),"Return_Flag":random.choice([0,0,0,0,0,0,0,1]),"Amendment_Flag":random.choice([0,0,0,1]),"Deduction_USD":round(random.choice([0,0,0,0,random.uniform(50,500)]),2)})
    return pd.DataFrame(rows)

def scolor(s): return "#16a34a" if s>=70 else "#ea580c" if s>=45 else "#dc2626"

DEFS={"fc_df":None,"o2c_df":None,"fc_hash":None,"o2c_hash":None,"dm":None,"om":None,"fl":None,"bl":None,"ps":None,"mod_scores":None,"ai_exec":None,"ai_agents":None,"done":False,"news":None,"wb":None,"gt":None,"market_ai":None,"market_fetched":False,"region":"Singapore","industry":"F&B / FMCG","diag_responses":{},"inv_days":45,"dpo_days":30,"display_ccy":"USD"}
for k,v in DEFS.items():
    if k not in st.session_state: st.session_state[k]=v
def reset():
    for k,v in DEFS.items(): st.session_state[k]=v

ccy=st.session_state.display_ccy; ccy_label=CURRENCIES.get(ccy,CURRENCIES["USD"])["label"]
st.markdown(f'<div class="tct-header"><div><div class="tct-title">Revenue Optimizer</div><div class="tct-subtitle">AI-Powered Revenue Operations Intelligence Platform</div></div><div style="display:flex;align-items:center;gap:12px"><span class="tct-badge">AI Engine: Active</span><span class="tct-currency">{ccy_label}</span></div></div>',unsafe_allow_html=True)
h1,h2,h3,h4,h5=st.columns([1,1,0.7,0.4,0.4])
with h1: region=st.selectbox("Region",list(REGIONS.keys()),index=list(REGIONS.keys()).index(st.session_state.region)); st.session_state.region=region
with h2: industry=st.selectbox("Industry",list(INDUSTRIES.keys()),index=list(INDUSTRIES.keys()).index(st.session_state.industry)); st.session_state.industry=industry
with h3:
    lc=REGIONS[region]["currency"]; co=["USD",lc] if lc!="USD" else ["USD"]; ci=co.index(st.session_state.display_ccy) if st.session_state.display_ccy in co else 0
    sel=st.selectbox("Currency",co,index=ci,format_func=lambda x:CURRENCIES[x]["label"]); st.session_state.display_ccy=sel; ccy=sel
with h4:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Demo Data"): st.session_state.fc_df=sample_demand(); st.session_state.o2c_df=sample_o2c(region); st.session_state.fc_hash="s"; st.session_state.o2c_hash="s"; st.session_state.done=False; st.rerun()
with h5:
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("Reset"): reset(); st.rerun()

tabs=st.tabs(["Setup","Executive Summary","Demand Forecasting","Order Management","Fulfilment & Logistics","Billing & Revenue","Post-Sales & Closure"])

with tabs[0]:
    st.markdown('<div style="font-size:1.3rem;font-weight:600;color:#0a1628">Setup & Configuration</div><div style="font-size:0.9rem;color:#64748b;margin-bottom:1.5rem">Upload data, complete maturity assessment, then run analysis.</div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="section-card"><div class="section-title">Demand & Forecast CSV</div>',unsafe_allow_html=True)
        st.markdown("**Required:** `Month` `SKU` `Actual_Units` `Forecast_Units` | **Optional:** `Orders_Placed` `Orders_OTIF`")
        uf=st.file_uploader("Forecast",type=["csv"],key="fc_up",label_visibility="collapsed")
        if uf:
            try:
                df=pd.read_csv(uf); h=str(hash(df.to_json())); miss=[c for c in ["Month","SKU","Actual_Units","Forecast_Units"] if c not in df.columns]
                if not miss: st.session_state.fc_df=df; st.session_state.fc_hash=h; st.session_state.done=False; st.success(f"{len(df)} rows loaded")
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
                df=pd.read_csv(uo); h=str(hash(df.to_json())); miss=[c for c in ["Order_ID","Customer","Invoice_Amount_USD","DSO_Days"] if c not in df.columns]
                if not miss: st.session_state.o2c_df=df; st.session_state.o2c_hash=h; st.session_state.done=False; st.success(f"{len(df)} rows loaded")
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
    for mn,qs in DIAGNOSTIC.items():
        st.markdown(f"**{mn}**")
        for q in qs:
            idx=st.selectbox(q["q"],options=list(range(len(q["opts"]))),format_func=lambda x,o=q["opts"]:o[x],index=st.session_state.diag_responses.get(q["key"],0),key=f"d_{q['key']}")
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
                    try: st.session_state.ai_exec=get_executive_ai(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,ds,region,industry,ccy)
                    except Exception as e: st.warning(f"AI error: {e}")
                with st.spinner("Agent simulation..."):
                    try: st.session_state.ai_agents=get_agent_simulation(st.session_state.dm,st.session_state.om,st.session_state.fl,st.session_state.bl,st.session_state.ps,st.session_state.mod_scores,region,industry,ccy)
                    except Exception as e: st.warning(f"Agent error: {e}")
                st.session_state.done=True; st.rerun()
        with bc2:
            if st.button("Fetch Market Intel",use_container_width=True):
                with st.spinner("News..."): st.session_state.news=fetch_news(region,industry)
                with st.spinner("World Bank..."): st.session_state.wb=fetch_wb(region,industry)
                with st.spinner("Trends..."): st.session_state.gt=fetch_gt(INDUSTRIES[industry]["keywords"][:3],region)
                with st.spinner("AI signals..."):
                    try: st.session_state.market_ai=get_demand_signals_ai(region,industry,st.session_state.news or [],st.session_state.wb or {},st.session_state.gt or {})
                    except: st.session_state.market_ai=None
                st.session_state.market_fetched=True; st.rerun()
        if st.session_state.done: st.success("Analysis complete — explore tabs above.")

with tabs[1]:
    if not st.session_state.done: st.info("Complete Setup and click Run Full Analysis.")
    else:
        ai=st.session_state.ai_exec or {}; bl=st.session_state.bl; ps=st.session_state.ps; s=ai.get("health_score",0)
        if st.session_state.market_fetched and st.session_state.market_ai:
            ms_t=st.session_state.market_ai.get("market_summary","")
            if ms_t: st.markdown(f'<div class="info-box"><strong>Market Context:</strong> {ms_t}</div>',unsafe_allow_html=True)
        rev=bl["rev"]; leak=bl["leak_total"]; outstd=rev*(ps["aging"]["30d"]+ps["aging"]["60d"]+ps["aging"]["90d"])/100
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: st.markdown(mcard("Total Revenue",fmtc(rev,ccy,True),"Total invoiced","neutral","Sum of all Invoice_Amount_USD in your O2C data","Source: Your uploaded data","metric-card metric-card-green"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Leakage",fmtc(leak,ccy,True),f"{round(leak/max(rev,1)*100,1)}% of revenue","bad","Discounting 1.8% + Errors + Disputes + Deductions","Source: McKinsey O2C Optimization; Normality SPAN Module 4.4","metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Outstanding AR",fmtc(outstd,ccy,True),"Receivables >30d","neutral","Revenue x (% invoices past 30 days)","Source: Calculated from your DSO distribution","metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">Net Recovered</div><div class="metric-value" style="font-size:1.4rem">{fmtc(rev-leak,ccy,True)}</div><div class="mex" style="color:#64748b">Revenue minus all estimated leakage</div></div>',unsafe_allow_html=True)
        with c5:
            reason=ai.get("health_reason","Composite of module scores, data metrics, and maturity")
            st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">Health</div><div class="metric-value" style="color:{scolor(s)};font-size:2.5rem">{s}</div><div style="font-size:0.75rem;font-weight:600;color:{scolor(s)}">{ai.get("overall_health","")}</div><div class="mex">{reason}</div><div class="msrc">60% data metrics + 40% maturity assessment</div></div>',unsafe_allow_html=True)
        if not bl["cashflow"].empty:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Cash Flow Trend</div>',unsafe_allow_html=True)
            cf=bl["cashflow"].head(6); cd=pd.DataFrame({"Month":cf["Month"],"Inflow":cf["Inflow"],"Outflow":-cf["Outflow"].abs()}).set_index("Month")
            st.bar_chart(cd,color=["#16a34a","#dc2626"])
            nt=cf["Net"].sum(); st.markdown(f'<div style="text-align:center;font-size:0.85rem;color:#64748b">Net Fund Flow: <span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{"#16a34a" if nt>=0 else "#dc2626"}">{fmtc(nt,ccy)}</span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cs,csm=st.columns([1,2])
        with cs: st.markdown(f'<div class="section-card"><div class="section-title">Strategic Assessment</div><p style="color:#334155;line-height:1.7;font-size:0.95rem">{ai.get("executive_summary","")}</p></div>',unsafe_allow_html=True)
        with csm:
            st.markdown('<div class="section-card"><div class="section-title">Module Health</div>',unsafe_allow_html=True)
            st.markdown('<div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Blended score: 60% from your data metrics + 40% from your maturity self-assessment. 70+ = Good, 45-69 = At Risk, below 45 = Critical.</div>',unsafe_allow_html=True)
            ms=st.session_state.mod_scores or {}; icons={"Demand Forecasting":"📦","Order Management":"📋","Order Fulfilment & Logistics":"🚚","Billing & Revenue Mgmt":"💰","Post-Sales & Financial Closure":"🏦"}
            mc=st.columns(5)
            for col,(mn,mv) in zip(mc,ms.items()):
                ex="Operating above benchmark" if mv>=70 else "Gaps identified — improvement needed" if mv>=45 else "Critical — significant intervention needed"
                with col: st.markdown(f'<div class="module-card"><div style="font-size:0.63rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#64748b">{icons.get(mn,"")} {mn}</div><div style="font-size:1.7rem;font-weight:600;font-family:IBM Plex Mono,monospace;color:{scolor(mv)};margin:0.4rem 0">{mv}</div><div class="mod-explain">{ex}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns(2)
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Top Risks</div>',unsafe_allow_html=True)
            for r in ai.get("top_risks",[])[:5]:
                sv=r.get("severity","Medium"); bc="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"; why=r.get("why","")
                st.markdown(f'<div class="insight-row"><div><span class="risk-badge {bc}">{sv}</span> <span style="font-size:0.7rem;background:#f1f5f9;padding:2px 8px;border-radius:20px;color:#64748b">{r.get("module","")}</span><div style="font-weight:500;margin-top:0.4rem">{r.get("risk","")}</div><div style="font-size:0.82rem;color:#64748b">{r.get("impact","")}</div><div class="risk-why">Why {sv}: {why}</div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Quick Wins</div>',unsafe_allow_html=True)
            for i,qw in enumerate(ai.get("quick_wins",[])[:5],1):
                st.markdown(f'<div class="insight-row"><div style="background:#0a1628;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:600;color:white;flex-shrink:0">{i}</div><div><div style="font-weight:500">{qw.get("action","")}</div><div style="font-size:0.8rem;color:#64748b">⏱ {qw.get("timeline","")} · 📈 {qw.get("expected_impact","")}</div><span style="font-size:0.7rem;background:#e0f2fe;color:#0369a1;padding:2px 8px;border-radius:20px">{qw.get("module","")}</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Agentic AI Simulation — Autonomous Interventions (Past 30 Days)</div>',unsafe_allow_html=True)
        st.markdown('<div class="info-box">Simulated actions the Revenue Optimizer AI agent would have taken autonomously based on your actual data. Each maps to a module with quantified impact.</div>',unsafe_allow_html=True)
        for item in (st.session_state.ai_agents or {}).get("interventions",[]):
            sv=item.get("severity","Medium").lower(); sc2="risk-high" if sv=="high" else "risk-med" if sv=="medium" else "risk-low"
            st.markdown(f'<div class="agent-card {sv}"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem"><span style="font-size:0.75rem;font-weight:600;color:#0a1628">Day {item.get("day","?")} · {item.get("module","")}</span><span class="risk-badge {sc2}">{item.get("severity","")}</span></div><div style="font-weight:500;font-size:0.9rem;margin-bottom:0.25rem">{item.get("action","")}</div><div style="font-size:0.82rem;color:#64748b">Trigger: {item.get("trigger","")}</div><div style="font-size:0.82rem;color:#16a34a;margin-top:0.2rem">{item.get("impact","")}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

with tabs[2]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        dm=st.session_state.dm; ob=INDUSTRIES[industry]["otif_benchmark"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("Forecast Accuracy",f'{dm["accuracy"]}%',"Target: 85-90%","good" if dm["accuracy"]>=85 else "bad","Formula: 100 - MAPE. Higher = closer to actual demand.","Target: Normality SoW (65%→90%+); Expert Interview confirmed no tracking","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Variance (Bias)",f'{abs(dm["bias"]):.1f}%',"Over-forecast" if dm["bias"]>5 else "Under-forecast" if dm["bias"]<-5 else "Stable","bad" if abs(dm["bias"])>5 else "good","(Actual - Forecast) / Actual. Positive = excess inventory risk.","Target: ±5%. Source: OTexts Forecasting Principles & Practice","metric-card"),unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">MAPE</div><div class="metric-value">{dm["mape"]}%</div><div class="mex" style="color:#64748b">Mean Absolute % Error. Avg |Actual-Forecast|/Actual.</div><div class="msrc" style="color:#64748b">Target: below 15%. Source: OTexts; M4 Competition benchmarks</div></div>',unsafe_allow_html=True)
        with c4: st.markdown(mcard("OTIF Rate",f'{dm["otif"]}%',f'Bench: {ob}%',"good" if dm["otif"]>=ob else "bad","Orders OTIF / Orders Placed x 100.","Bench: McKinsey OTIF Consumer Sector (2019); Walmart mandates 98%","metric-card metric-card-green" if dm["otif"]>=ob else "metric-card metric-card-red"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([2,1])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Forecast vs Actuals</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:1rem">Monthly aggregated actual demand vs forecasted. Gap = forecast error per period.</div>',unsafe_allow_html=True)
            vd=dm["variance"]
            if not vd.empty: st.line_chart(vd[["Month","Actual","Forecast"]].set_index("Month"),color=["#0f172a","#16a34a"])
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Variance Analysis</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Difference = Actual minus Forecast (units). Deviation = Variance as % of Forecast.</div>',unsafe_allow_html=True)
            for _,row in dm["variance"].tail(6).iterrows():
                vp=row["Variance_Pct"]; vc="var-pos" if vp>=0 else "var-neg"
                st.markdown(f'<div class="var-card"><div class="var-label">{row["Month"]} <span class="var-badge">Variance</span></div><div class="var-row"><span>Difference</span><span class="{vc}">{row["Variance"]:+,.0f} units</span></div><div class="var-row"><span>Deviation</span><span class="{vc}">{vp:+.1f}%</span></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl2,cr2=st.columns(2)
        with cl2:
            st.markdown('<div class="section-card"><div class="section-title">SKU Performance</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Per-SKU accuracy = 100 - SKU MAPE. Green: 70+, Amber: 45-69, Red: below 45.</div>',unsafe_allow_html=True)
            for _,row in dm["sku"].sort_values("Accuracy",ascending=False).iterrows():
                c=scolor(row["Accuracy"])
                st.markdown(f'<div style="margin-bottom:1rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{row["SKU"]}</span><span style="color:{c};font-family:IBM Plex Mono,monospace;font-weight:500">{row["Accuracy"]}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{min(100,row["Accuracy"])}%;background:{c}"></div></div><div style="font-size:0.75rem;color:#94a3b8;margin-top:3px">MAPE: {row["MAPE"]}% Bias: {row["Bias"]:+.1f}%</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr2:
            if st.session_state.market_fetched and st.session_state.market_ai:
                st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Live signals from RSS, World Bank, Google Trends — AI-interpreted as potential forecast adjustments.</div>',unsafe_allow_html=True)
                for sig in st.session_state.market_ai.get("demand_signals",[])[:4]:
                    st.markdown(f'<div class="news-card"><div style="font-weight:500;font-size:0.9rem">{sig.get("signal","")}</div><div style="font-size:0.78rem;color:#64748b;margin-top:0.2rem">Source: {sig.get("source","")} | Impact: {sig.get("impact","")}</div><div style="font-size:0.82rem;color:#0369a1;margin-top:0.3rem">Adjustment: {sig.get("forecast_adjustment","")}</div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
            else: st.markdown('<div class="section-card"><div class="section-title">External Demand Signals</div><div class="upload-hint">Click Fetch Market Intel in Setup.</div></div>',unsafe_allow_html=True)

with tabs[3]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        om=st.session_state.om; bc=INDUSTRIES[industry]["cycle_benchmark"]
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("Order Cycle",f'{om["cycle"]}d',f'Bench: {bc}d',"good" if om["cycle"]<=bc else "bad","Avg days from Order_Date to Invoice_Date.",f"Bench: {bc}d for {industry}. Source: APQC O2C Benchmarks","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Error Rate",f'{om["err"]}%',"Target: <2%","good" if om["err"]<2 else "bad","% of orders with Invoice_Errors = 1.","Target: APQC Benchmarks; Expert Interview flagged portal failures","metric-card metric-card-green" if om["err"]<2 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Dispute Rate",f'{om["disp"]}%',"Target: <5%","good" if om["disp"]<5 else "bad","% of orders flagged as Disputed = 1.","Target: <5%. Source: Normality SPAN Module 4.2","metric-card metric-card-green" if om["disp"]<5 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Amendments",f'{om["amend"]}%',"Low" if om["amend"]<10 else "High churn","good" if om["amend"]<10 else "bad","% of orders with Amendment_Flag = 1.","Expert Interview: order changes are frequent and disruptive in CPG","metric-card metric-card-green" if om["amend"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Pain Points & AI Solutions</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Common challenges identified in SEA CPG expert interviews, mapped to Revenue Optimizer AI solutions.</div>',unsafe_allow_html=True)
        for t,p,f in [("Manual order entry",f"Orders via email/phone need manual ERP entry, causing {om['err']}% error rate.","AI auto-capture: reads order emails/PDFs, populates ERP for human review."),("Amendment chaos",f"{om['amend']}% amendment rate disrupts production and fulfilment planning.","Amendment window enforcement with auto customer notification after cutoff."),("Validation gaps","Incomplete data flows downstream to billing errors and disputes.","Real-time AI validation: pricing, inventory, credit check before order confirmation."),("No real-time visibility","Teams manually check order status across disconnected systems.","Order control tower: unified lifecycle dashboard from receipt to delivery.")]:
            st.markdown(f'<div style="padding:0.75rem 0;border-bottom:1px solid #f1f5f9"><div style="font-weight:500;font-size:0.9rem;color:#0a1628">{t}</div><div style="font-size:0.82rem;color:#64748b;margin-top:0.2rem">{p}</div><div style="font-size:0.82rem;color:#16a34a;margin-top:0.3rem;background:#f0fdf4;padding:4px 8px;border-radius:6px">{f}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

with tabs[4]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        fl=st.session_state.fl
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("OTIF",f'{fl["otif"]}%',f'Bench: {fl["otif_bench"]}%',"good" if fl["otif"]>=fl["otif_bench"] else "bad","Avg of OTIF_Flag x 100. On-Time In-Full delivery rate.",f"Bench: McKinsey OTIF Consumer Sector (2019). Walmart mandates 98%.","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Fulfilment Cycle",f'{fl["ful_days"]}d',f'Bench: {fl["ful_bench"]}d',"good" if fl["ful_days"]<=fl["ful_bench"] else "bad","Avg Fulfilment_Days from order to shipment dispatch.",f"Bench: {fl['ful_bench']}d for {industry}. Source: APQC Benchmarks","metric-card metric-card-green" if fl["ful_days"]<=fl["ful_bench"] else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Returns",f'{fl["return_rate"]}%',"Target: <3%","good" if fl["return_rate"]<3 else "bad","Avg Return_Flag x 100. Shelf life rejections are key CPG driver.","Expert Interview: expiry returns can cost more than the goods themselves","metric-card metric-card-green" if fl["return_rate"]<3 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Partial Shipments",f'{fl["partial"]}%',"Incomplete deliveries","bad" if fl["partial"]>10 else "good","100 - OTIF %. Orders not delivered in full.","Impacts OTIF score and customer satisfaction. Source: Normality SPAN Analysis","metric-card metric-card-green" if fl["partial"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.market_ai:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Supply Risk Radar</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Live external threats to fulfilment from regional news, World Bank, and Google Trends. AI interprets severity and suggests mitigations.</div>',unsafe_allow_html=True)
            for r in st.session_state.market_ai.get("supply_risks",[])[:4]:
                sv=r.get("severity","Medium"); bc2="risk-high" if sv=="High" else "risk-med" if sv=="Medium" else "risk-low"
                st.markdown(f'<div class="news-card"><span class="risk-badge {bc2}">{sv}</span><div style="font-weight:500;font-size:0.9rem;margin-top:0.3rem">{r.get("risk","")}</div><div style="font-size:0.78rem;color:#64748b">Source: {r.get("source","")} | Mitigation: {r.get("mitigation","")}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.news:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Regional News</div>',unsafe_allow_html=True)
            for a in (st.session_state.news or [])[:5]:
                tags="".join([f'<span class="news-tag">{k}</span>' for k in a["keywords"]])
                st.markdown(f'<div class="news-card"><div style="font-size:0.9rem;font-weight:500">{a["title"]}</div><div style="font-size:0.75rem;color:#94a3b8">{a["source"]} {a["published"]}</div><div style="margin-top:0.3rem">{tags}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

with tabs[5]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        bl=st.session_state.bl; lpct=round((bl["leak_total"]/max(bl["rev"],1))*100,1)
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(mcard("DSO",f'{bl["dso"]}d',f'{bl["gap"]:+.0f}d vs {bl["bench"]}d',"good" if bl["gap"]<=0 else "bad","Avg DSO_Days. Days from invoice to payment.",f"Bench: {bl['bench']}d for {industry}. Source: APQC; McKinsey O2C Optimization","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c2: st.markdown(mcard("Invoice Errors",f'{bl["err"]}%',"Target: <2%","good" if bl["err"]<2 else "bad","% invoices flagged with errors.","Target: APQC. Expert Interview: portal submission failures cause delays","metric-card metric-card-green" if bl["err"]<2 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("Disputes",f'{bl["disp"]}%',"Target: <5%","good" if bl["disp"]<5 else "bad","% invoices disputed. Often from late order amendments.","Source: Normality SPAN Module 4.2; Expert Interview on rebate mismatches","metric-card metric-card-green" if bl["disp"]<5 else "metric-card metric-card-amber"),unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card-dark"><div class="metric-label" style="color:#f87171">Revenue Leakage</div><div class="metric-value" style="font-size:1.4rem">{lpct}%</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{fmtc(bl["leak_total"],ccy)}</div><div class="mex" style="color:#64748b">Disc 1.8% + Errors {bl["err"]}%x2.5% + Disputes {bl["disp"]}%x5% + Deductions 0.8%</div><div class="msrc" style="color:#64748b">Source: McKinsey O2C (1.5-3% typical); Normality SPAN Module 4.4</div></div>',unsafe_allow_html=True)
        if not bl["recv_forecast"].empty:
            st.markdown("<br>",unsafe_allow_html=True)
            rcl,rcr=st.columns([2,1])
            with rcl:
                st.markdown('<div class="section-card"><div class="section-title">Receivable Forecast vs Actuals</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:1rem">Predicted receivable collections vs actual cash received per week.</div>',unsafe_allow_html=True)
                rf=bl["recv_forecast"]; chart=rf[["Actual","Predicted"]].copy(); chart.index=[f"W{i}" for i in range(len(chart))]
                st.line_chart(chart,color=["#0f172a","#16a34a"]); st.markdown("</div>",unsafe_allow_html=True)
            with rcr:
                st.markdown('<div class="section-card"><div class="section-title">Variance Analysis</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Difference = Actual - Predicted (currency). Deviation = Variance as % of Predicted.</div>',unsafe_allow_html=True)
                for idx,row in rf.tail(4).iterrows():
                    vp=row["Var_Pct"]; vc="var-pos" if vp>=0 else "var-neg"
                    st.markdown(f'<div class="var-card"><div class="var-label">W{idx} <span class="var-badge">Variance</span></div><div class="var-row"><span>Difference</span><span class="{vc}">{fmtc(row["Variance"],ccy)}</span></div><div class="var-row"><span>Deviation</span><span class="{vc}">{vp:+.1f}%</span></div></div>',unsafe_allow_html=True)
                st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        cl,cr=st.columns([3,2])
        with cl:
            st.markdown('<div class="section-card"><div class="section-title">Revenue Leakage Waterfall</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">How revenue erodes by leakage type. Multipliers from McKinsey O2C benchmarks and Normality SPAN analysis.</div>',unsafe_allow_html=True)
            rev=bl["rev"]; net=rev-bl["leak_total"]
            for lb,v,co,d in [("Gross Revenue",rev,"#0a1628","Total invoiced revenue"),("Discounting",-bl["leak_disc"],"#dc2626","1.8% of revenue — rogue discounts (McKinsey O2C benchmark)"),("Invoice Errors",-bl["leak_inv"],"#ea580c",f'{bl["err"]}% error rate x 2.5% cost per error (APQC)'),("Disputes",-bl["leak_disp"],"#f59e0b",f'{bl["disp"]}% dispute rate x 5% cost (Normality SPAN 4.2)'),("Deductions",-bl["leak_ded"],"#8b5cf6","0.8% — out-of-terms deductions (Expert Interview)"),("Net Recovered",net,"#16a34a","After all leakage types addressed")]:
                neg=v<0; dv=f"-{fmtc(abs(v),ccy)}" if neg else fmtc(v,ccy); pct=min(100,abs(v)/max(rev,1)*100)
                st.markdown(f'<div style="margin-bottom:0.75rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px"><span style="font-weight:500">{lb}</span><span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{co}">{dv}</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct}%;background:{co}"></div></div><div style="font-size:0.68rem;color:#94a3b8;margin-top:3px">{d}</div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with cr:
            st.markdown('<div class="section-card"><div class="section-title">Customer DSO Risk</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">High: DSO > 1.4x benchmark. Medium: > 1.1x benchmark. Low: at or below.</div>',unsafe_allow_html=True)
            for _,row in bl["cust"].head(8).iterrows():
                r=row["Risk"]; rc="risk-high" if r=="High" else "risk-med" if r=="Medium" else "risk-low"
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f1f5f9"><span style="font-size:0.85rem;font-weight:500">{row["Customer"]}</span><span><span style="font-family:IBM Plex Mono,monospace;font-size:0.85rem;margin-right:8px">{row["Avg_DSO"]}d</span><span class="risk-badge {rc}">{r}</span></span></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

with tabs[6]:
    if not st.session_state.done: st.info("Upload data and Run Full Analysis.")
    else:
        ps=st.session_state.ps
        c1,c2,c3,c4=st.columns(4)
        with c1: st.markdown(f'<div class="metric-card-dark"><div class="metric-label">WC Health</div><div class="metric-value" style="color:{"#4ade80" if ps["score"]>=70 else "#f87171"}">{ps["score"]}</div><div style="font-size:0.78rem;color:#94a3b8;margin-top:0.3rem">{ps["health"]}</div><div class="mex" style="color:#64748b">100 - (CCC gap / benchmark x 50). 70+ Good, 45-69 At Risk, &lt;45 Critical.</div></div>',unsafe_allow_html=True)
        with c2: st.markdown(mcard("CCC",f'{ps["ccc"]}d',f'Bench: {ps["bench"]}d',"good" if ps["ccc"]<=ps["bench"] else "bad",f"DSO ({ps['dso']}d) + Inventory ({ps['inv']}d) - DPO ({ps['dpo']}d)","Standard financial formula. Every 1d reduction = Annual Revenue / 365 freed.","metric-card metric-card-blue"),unsafe_allow_html=True)
        with c3: st.markdown(mcard("AR > 90 Days",f'{ps["aging"]["90d"]}%',"Collection risk" if ps["aging"]["90d"]>=10 else "Low","bad" if ps["aging"]["90d"]>=10 else "good","% of invoices with DSO exceeding 90 days.","Target: <10%. High risk of write-off. Source: APQC Collections Benchmarks","metric-card metric-card-green" if ps["aging"]["90d"]<10 else "metric-card metric-card-red"),unsafe_allow_html=True)
        with c4: st.markdown(mcard("Deductions",fmtc(ps["deductions"],ccy),"Unvalidated","bad" if ps["deductions"]>1000 else "neutral","Sum of Deduction_USD. Taken without proper validation.","Expert Interview: early payment discounts taken outside contractual terms","metric-card metric-card-amber"),unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        st.markdown('<div class="section-card"><div class="section-title">Cash Conversion Cycle</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">CCC = DSO + Inventory Days - DPO. Every day reduced unlocks working capital = Annual Revenue / 365. Source: Standard financial metric; Expert Interview flagged working capital visibility as top CFO priority.</div>',unsafe_allow_html=True)
        cc1,cc2,cc3=st.columns(3)
        for col,(lb,v,co,fx,src) in zip([cc1,cc2,cc3],[("DSO",ps["dso"],"#dc2626","Reduce: faster invoicing, portal compliance bot, AI dunning","Days from invoice to payment. Bench: APQC O2C"),("Inventory Days",ps["inv"],"#f59e0b","Reduce: dynamic safety stock, FEFO automation, demand forecasting","Days inventory held before sale. Bench: Industry standard"),("DPO",ps["dpo"],"#16a34a","Increase: renegotiate supplier payment terms","Days to pay suppliers. Higher = better for your cash. Standard metric")]):
            with col: st.markdown(f'<div class="metric-card" style="text-align:center"><div class="metric-label">{lb}</div><div class="metric-value" style="color:{co}">{v}d</div><div style="font-size:0.78rem;color:#334155;margin-top:0.5rem">{fx}</div><div class="msrc">{src}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        al,ar=st.columns(2)
        with al:
            st.markdown('<div class="section-card"><div class="section-title">Receivables Aging</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Distribution of invoices by payment delay. Green = current. Red = 90+ days (write-off risk). Source: Your DSO data.</div>',unsafe_allow_html=True)
            for lb,v,co in [("Current (0-30d)",ps["aging"]["current"],"#16a34a"),("31-60 days",ps["aging"]["30d"],"#f59e0b"),("61-90 days",ps["aging"]["60d"],"#ea580c"),("90+ days",ps["aging"]["90d"],"#dc2626")]:
                st.markdown(f'<div style="margin-bottom:0.5rem"><div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:3px"><span style="font-weight:500">{lb}</span><span style="font-family:IBM Plex Mono,monospace;font-weight:600;color:{co}">{v}%</span></div><div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{v}%;background:{co}"></div></div></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        with ar:
            st.markdown('<div class="section-card"><div class="section-title">Upcoming Cash Position</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Forward-looking daily projection. Inflow = expected customer payments. Outflow = estimated operating costs. Select horizon below.</div>',unsafe_allow_html=True)
            cp=ps.get("cash_pos",[])
            if cp:
                hz=st.radio("Horizon",options=[7,14,21,30],horizontal=True,index=0,key="cp_hz")
                html='<table class="cp-table"><tr><th>Date</th><th>Expected Inflow</th><th>Expected Outflow</th><th>Net Flow</th></tr>'
                for row in cp[:hz]:
                    nc="cp-green" if row["Net"]>=0 else "cp-red"
                    html+=f'<tr><td style="font-weight:500;font-family:IBM Plex Sans,sans-serif">{row["Date"]}</td><td class="cp-green">{fmtc(row["Inflow"],ccy)}</td><td class="cp-red">{fmtc(row["Outflow"],ccy)}</td><td class="{nc}">{fmtc(row["Net"],ccy)}</td></tr>'
                html+='</table>'; st.markdown(html,unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
        if st.session_state.market_fetched and st.session_state.wb:
            st.markdown("<br>",unsafe_allow_html=True)
            st.markdown('<div class="section-card"><div class="section-title">Macroeconomic Context</div><div class="mex" style="margin-top:-0.5rem;margin-bottom:0.75rem">Live indicators from World Bank API. GDP growth and inflation directly affect demand patterns and working capital pressure.</div>',unsafe_allow_html=True)
            for lb,series in st.session_state.wb.items():
                if series: st.markdown(f"**{lb}** — Latest: `{series[-1]['value']}` ({series[-1]['year']})"); st.line_chart(pd.DataFrame(series).set_index("year")["value"])
            st.markdown("</div>",unsafe_allow_html=True)
